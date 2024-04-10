import datetime as dt

import pytest
from freezegun import freeze_time

from schemas.auth import JWTTokenPayload
from services.auth import generate_jwt_signed_token, validate_jwt_token_signature


@pytest.fixture()
def jwt_access_token_secret_key():
    return "movies_token_secret"


@pytest.fixture()
def jwt_access_token_expires_minutes():
    return 60


@pytest.mark.asyncio()
async def test_generate_jwt_token(
    jwt_access_token_secret_key: str,
    jwt_access_token_expires_minutes: int,
):
    dt_now = dt.datetime(2024, 1, 1, 0, 0)
    expected_expiration_dt = dt_now + dt.timedelta(minutes=jwt_access_token_expires_minutes)

    expected_token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiJ1c2VybmFtZTp0ZXN0QHRlc3QuY29tIiwicm9sZXMiOlsidXNlci"
        "IsImFkbWluIl0sImV4cCI6MTcwNDA3MDgwMCwiaWF0IjoxNzA0MDY3MjAwfQ==."
        "QSy4r_1YxbuLEkISGaNDzFcUH91H0ZnuhGITG4VGrSs="
    )

    with freeze_time(dt_now):
        assert await generate_jwt_signed_token(
            data={"sub": "username:test@test.com", "roles": ["user", "admin"]},
            secret_key=jwt_access_token_secret_key,
            expires_minutes=jwt_access_token_expires_minutes,
        ) == (
            expected_token,
            expected_expiration_dt,
        )


@pytest.mark.asyncio()
async def test_validate_jwt_token(
    jwt_access_token_secret_key: str,
    jwt_access_token_expires_minutes: int,
):
    dt_now = dt.datetime(2024, 1, 1, 0, 0)
    expected_expiration_dt = dt_now + dt.timedelta(minutes=jwt_access_token_expires_minutes)

    validated_token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiJ1c2VybmFtZTp0ZXN0QHRlc3QuY29tIiwicm9sZXMiOlsidXNlci"
        "IsImFkbWluIl0sImV4cCI6MTcwNDA3MDgwMCwiaWF0IjoxNzA0MDY3MjAwfQ==."
        "QSy4r_1YxbuLEkISGaNDzFcUH91H0ZnuhGITG4VGrSs="
    )

    with freeze_time(dt_now):
        assert await validate_jwt_token_signature(
            validated_token,
            jwt_access_token_secret_key,
        ) == JWTTokenPayload(
            iat=dt_now.timestamp(),
            sub="username:test@test.com",
            exp=expected_expiration_dt.timestamp(),
            jti=None,
            roles=["user", "admin"],
        )
