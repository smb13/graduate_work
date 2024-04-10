import datetime as dt
import http
import time as tm
import uuid
from collections.abc import Callable
from enum import Enum

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JOSEError, jwt
from pydantic import BaseModel

from core.config import settings


class SystemRolesEnum(str, Enum):
    user = "user"
    admin = "admin"


class JWTTokenPayload(BaseModel):
    iat: int
    sub: str
    exp: int

    jti: str | None = None
    roles: list[str] = []

    @property
    def expires_at(self) -> dt.datetime:
        return dt.datetime.fromtimestamp(self.exp)

    @property
    def username(self) -> str:
        if not self.sub.startswith("username:"):
            return ""
        return self.sub[len("username:") :]

    @property
    def issued_at(self) -> dt.datetime:
        return dt.datetime.fromtimestamp(self.iat)

    @property
    def jwt_id(self) -> uuid.UUID:
        return uuid.UUID(self.jti)


async def decode_token(token: str) -> JWTTokenPayload | None:
    try:
        decoded_token = jwt.decode(token, settings.jwt_access_token_secret_key, algorithms=["HS256"])
        return JWTTokenPayload.model_validate(decoded_token) if decoded_token["exp"] >= tm.time() else None
    except JOSEError:
        return None


security_jwt = HTTPBearer(auto_error=False)


def check_permissions(*required_roles: SystemRolesEnum) -> Callable:
    """Returns a Dependency that returns the token if it has the given roles,
    otherwise raises HTTP403
    """

    async def dependency(
        credentials: HTTPAuthorizationCredentials | None = Depends(security_jwt),
    ) -> JWTTokenPayload | None:
        token: JWTTokenPayload | None

        token = await decode_token(credentials.credentials) if credentials else None

        if required_roles and (not token or not {role.value for role in required_roles} <= set(token.roles)):
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail="Forbidden")

        return token

    return dependency
