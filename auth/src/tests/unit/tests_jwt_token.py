import datetime as dt
import uuid

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


@pytest.fixture()
def user_id() -> uuid.UUID:
    return uuid.UUID("8fc77a26-2473-4ed1-bd07-5fc6d41a8267")


@pytest.mark.asyncio()
async def test_generate_jwt_token(
    jwt_access_token_secret_key: str,
    jwt_access_token_expires_minutes: int,
    user_id: uuid.UUID,
):
    dt_now = dt.datetime(2024, 1, 1, 0, 0)
    expected_expiration_dt = dt_now + dt.timedelta(minutes=jwt_access_token_expires_minutes)

    expected_token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiI4ZmM3N2EyNi0yNDczLTRlZDEtYmQwNy01ZmM2ZDQxYTgyNjciLCJyb2xlcy"
        "I6WyJ1c2VyIiwiYWRtaW4iXSwiZXhwIjoxNzA0MDcwODAwLCJpYXQiOjE3MDQwNjcyMDB9."
        "xjQL9-KNGoMdfwTY4dhiLw_lLnSNPlicW84tuzG09LQ="
    )

    with freeze_time(dt_now):
        assert await generate_jwt_signed_token(
            data={"sub": user_id, "roles": ["user", "admin"]},
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
    user_id: uuid.UUID,
):
    dt_now = dt.datetime(2024, 1, 1, 0, 0)
    expected_expiration_dt = dt_now + dt.timedelta(minutes=jwt_access_token_expires_minutes)

    validated_token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiI4ZmM3N2EyNi0yNDczLTRlZDEtYmQwNy01ZmM2ZDQxYTgyNjciLCJyb2xlcy"
        "I6WyJ1c2VyIiwiYWRtaW4iXSwiZXhwIjoxNzA0MDcwODAwLCJpYXQiOjE3MDQwNjcyMDB9."
        "xjQL9-KNGoMdfwTY4dhiLw_lLnSNPlicW84tuzG09LQ="
    )

    with freeze_time(dt_now):
        assert await validate_jwt_token_signature(
            validated_token,
            jwt_access_token_secret_key,
        ) == JWTTokenPayload(
            iat=dt_now.timestamp(),
            sub=user_id,
            exp=expected_expiration_dt.timestamp(),
            jti=None,
            roles=["user", "admin"],
        )
