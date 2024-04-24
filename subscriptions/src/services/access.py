import http
import time
from enum import Enum
from functools import wraps

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt

from core.config import settings


class Roles(str, Enum):
    user = "user"
    admin = "admin"


def check_access(allow_roles: set):
    def inner(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("user")
            if not user:
                return
            user_roles = user["roles"]
            if Roles.admin not in user_roles:
                if allow_roles is None:
                    return
                if not allow_roles & set(user_roles):
                    raise HTTPException(
                        status_code=http.HTTPStatus.FORBIDDEN,
                        detail="Insufficient permissions",
                    )
            return await function(*args, **kwargs)

        return wrapper

    return inner


def decode_token(token: str) -> dict | None:
    try:
        decoded_token = jwt.decode(token, settings.authjwt_secret_key)
        return decoded_token if decoded_token["exp"] >= time.time() else None
    except Exception:
        return None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail="Invalid authorization code.")
        if not credentials.scheme == "Bearer":
            raise HTTPException(status_code=http.HTTPStatus.UNAUTHORIZED, detail="Only Bearer token might be accepted")
        decoded_token = self.parse_token(credentials.credentials)
        if not decoded_token:
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail="Invalid or expired token.")
        return decoded_token

    @staticmethod
    def parse_token(jwt_token: str) -> dict | None:
        return decode_token(jwt_token)


security_jwt = JWTBearer()
