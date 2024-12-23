import datetime as dt
import uuid

from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class JWTTokenPayload(BaseModel):
    iat: int
    sub: uuid.UUID
    exp: int

    jti: str | None = None
    roles: list[str] = []
    subs: list[int] | None = []

    @property
    def expires_at(self) -> dt.datetime:
        return dt.datetime.fromtimestamp(self.exp)

    @expires_at.setter
    def expires_at(self, expires_at: dt.datetime) -> None:
        self.exp = int(expires_at.timestamp())

    @property
    def issued_at(self) -> dt.datetime:
        return dt.datetime.fromtimestamp(self.iat)

    @issued_at.setter
    def issued_at(self, issued_at: dt.datetime) -> None:
        self.iat = int(issued_at.timestamp())

    @property
    def jwt_id(self) -> uuid.UUID:
        return uuid.UUID(self.jti)

    @jwt_id.setter
    def jwt_id(self, jwt_id: uuid.UUID) -> None:
        self.jti = str(jwt_id)
