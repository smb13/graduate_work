import datetime as dt
import hashlib
import hmac
import uuid
from base64 import urlsafe_b64decode, urlsafe_b64encode
from collections.abc import Callable, Coroutine, Sequence
from functools import lru_cache
from typing import Annotated, Any

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi_pagination.cursor import CursorPage
from fastapi_pagination.ext.async_sqlalchemy import paginate
from orjson import orjson
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.config import settings
from db.alchemy import get_session
from db.redis import get_redis
from models import RefreshToken, User
from models.access_log import AccessLogEntry
from schemas.auth import JWTTokenPayload
from services.base import BaseService
from services.roles import RolesService, get_roles_service
from services.users import UsersService, get_users_service
from utils.responses import invalid_credentials

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="v1/auth/token",
    scheme_name="JWT Bearer Token",
)


class AuthService(BaseService):
    @staticmethod
    async def make_access_token(user: User, role_codes: Sequence[str]) -> str:
        token, _ = await generate_jwt_signed_token(
            data={"sub": f"username:{user.login}", "roles": role_codes},
            expires_minutes=settings.jwt_access_token_expires_minutes,
            secret_key=settings.jwt_access_token_secret_key,
        )
        return token

    async def make_refresh_token(self, user: User) -> str:
        jti = uuid.uuid4()
        refresh_token, exp = await generate_jwt_signed_token(
            data={"sub": f"username:{user.login}", "jti": str(jti)},
            expires_minutes=settings.jwt_refresh_token_expires_minutes,
            secret_key=settings.jwt_refresh_token_secret_key,
        )
        self.session.add(RefreshToken(jwt_id=jti, user_id=user.id, expires_at=exp))
        await self.session.commit()
        return refresh_token

    async def add_access_log(
        self,
        user: User,
        *,
        x_forwarded_for: str = "",
        user_agent: str = "",
        origin: str = "",
    ) -> AccessLogEntry:
        client_ip = x_forwarded_for.split(", ")[0]
        origin = origin.removeprefix("http://").removeprefix("https://")

        access_log = AccessLogEntry(
            user_id=user.id,
            ip_address=client_ip,
            user_agent=user_agent,
            origin=origin,
            created=dt.datetime.now(),
        )
        self.session.add(access_log)
        await self.session.commit()
        return access_log

    async def get_access_log(self, user: User) -> CursorPage[AccessLogEntry]:
        return await paginate(
            self.session,
            select(AccessLogEntry).where(AccessLogEntry.user_id == user.id).order_by(AccessLogEntry.created.desc()),
        )

    async def revoke_refresh_token(self, jwt_id: uuid.UUID | None) -> None:
        if not jwt_id:
            return

        token = await self.session.scalars(select(RefreshToken).where(RefreshToken.jwt_id == jwt_id))
        token = token.first()
        if token:
            await self.session.delete(token)
            await self.session.commit()

    async def revoke_access_token(self, token: str) -> None:
        await self.redis.setex(
            "access_token:" + token,
            settings.jwt_access_token_expires_minutes * 60,
            "revoked",
        )

    @staticmethod
    async def get_access_token_payload(jwt_token: str) -> JWTTokenPayload | None:
        return await get_jwt_token_payload(jwt_token)

    @staticmethod
    async def check_access_token_signature(jwt_token: str) -> JWTTokenPayload | None:
        return await validate_jwt_token_signature(jwt_token, settings.jwt_access_token_secret_key)

    @staticmethod
    async def check_refresh_token_signature(jwt_token: str) -> JWTTokenPayload | None:
        return await validate_jwt_token_signature(jwt_token, settings.jwt_refresh_token_secret_key)

    async def check_refresh_token_payload(self, payload: JWTTokenPayload | None, user_id: uuid.UUID | None) -> bool:
        if not payload or not user_id:
            return False

        db_refresh_token = await self.session.scalar(
            select(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.jwt_id == payload.jwt_id),
        )

        return bool(db_refresh_token and db_refresh_token.expires_at > dt.datetime.utcnow())

    async def check_access_token(self, payload: JWTTokenPayload | None, token: str) -> bool:
        return bool(
            payload
            and payload.expires_at > dt.datetime.utcnow()
            and token
            and await self.redis.get("access_token:" + token) != "revoked",
        )


async def generate_jwt_signed_token(data: dict, *, expires_minutes: int, secret_key: str) -> tuple[str, dt.datetime]:
    header = {"alg": "HS256", "typ": "JWT"}

    iat = dt.datetime.utcnow()
    exp = iat + dt.timedelta(minutes=expires_minutes)

    payload = data | {"exp": int(exp.timestamp()), "iat": int(iat.timestamp())}

    encoded_header: bytes = urlsafe_b64encode(orjson.dumps(header))
    encoded_payload: bytes = urlsafe_b64encode(orjson.dumps(payload))

    signature = hmac.new(
        key=secret_key.encode("utf-8"),
        msg=encoded_header + b"." + encoded_payload,
        digestmod=hashlib.sha256,
    )
    encoded_signature: bytes = urlsafe_b64encode(signature.digest())

    return (encoded_header + b"." + encoded_payload + b"." + encoded_signature).decode(), exp


async def validate_jwt_token_signature(jwt_token: str, secret_key: str) -> JWTTokenPayload | None:
    try:
        encoded_header, encoded_payload, encoded_signature = jwt_token.split(".")
        header = orjson.loads(urlsafe_b64decode(encoded_header + "=" * (-len(encoded_header) % 4)))
        payload = orjson.loads(urlsafe_b64decode(encoded_payload + "=" * (-len(encoded_payload) % 4)))
    except (ValueError, TypeError):
        return None

    if not (hmac.compare_digest(header.get("alg"), "HS256") and hmac.compare_digest(header.get("typ"), "JWT")):
        return None

    message = (encoded_header + "." + encoded_payload).encode("utf-8")
    computed_signature = hmac.digest(
        key=secret_key.encode("utf-8"),
        msg=message,
        digest=hashlib.sha256,
    )
    received_signature = urlsafe_b64decode(encoded_signature + "=" * (-len(encoded_signature) % 4))
    if not hmac.compare_digest(computed_signature, received_signature):
        return None

    return JWTTokenPayload(**payload)


async def get_jwt_token_payload(jwt_token: str) -> JWTTokenPayload | None:
    try:
        encoded_payload = jwt_token.split(".")[1]
        payload = orjson.loads(urlsafe_b64decode(encoded_payload))
    except (ValueError, TypeError):
        return None

    return JWTTokenPayload(**payload)


@lru_cache
def get_auth_service(
    alchemy: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
) -> AuthService:
    return AuthService(session=alchemy, redis=redis)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    users_service: UsersService = Depends(get_users_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> Coroutine[Any, Any, User]:
    payload = await auth_service.check_access_token_signature(token)
    user = await users_service.retrieve(username=payload and payload.username)
    is_valid = await auth_service.check_access_token(payload, token)

    if not user or not is_valid:
        raise invalid_credentials

    return user


def check_permissions(*permission_actions: str) -> Callable:
    """Returns a Dependency that returns the user if it has the given permissions,
    otherwise raises HTTP403
    """

    async def dependency(
        user: User = Depends(get_current_user),
        roles_service: RolesService = Depends(get_roles_service),
    ) -> User:
        if not await roles_service.check_permissions(user, permission_actions):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user

    return dependency
