from pydantic import BaseModel


class YandexTokenResponse(BaseModel):
    token_type: str
    access_token: str
    expires_in: int
    refresh_token: str


class YandexUserInfoResponse(BaseModel):
    id: str
    login: str
    client_id: str
    display_name: str
    first_name: str
    last_name: str
    default_email: str
    emails: list[str]


class GoogleUserInfoResponse(BaseModel):
    iss: str
    azp: str
    aud: str
    sub: str
    email: str
    email_verified: bool
    at_hash: str
    nonce: str
    name: str
    picture: str
    given_name: str
    family_name: str
    locale: str
    iat: int
    exp: int


class GoogleTokenResponse(BaseModel):
    access_token: str
    expires_in: int
    scope: str
    token_type: str
    id_token: str
    expires_at: int
    refresh_token: str
    userinfo: GoogleUserInfoResponse
