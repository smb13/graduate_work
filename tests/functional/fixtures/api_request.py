from http import HTTPStatus
from uuid import uuid4

import aiohttp
import pytest_asyncio
from async_fastapi_jwt_auth import AuthJWT
from settings import authjwt_settings, test_settings


@AuthJWT.load_config
def get_config():
    return authjwt_settings


@pytest_asyncio.fixture(scope="session")
async def session():
    jwt = AuthJWT()
    access_token = await jwt.create_access_token(
        subject=str(uuid4()),
        user_claims={"sub": "username:user@yandex.ru", "roles": ["user"]},
    )
    async with aiohttp.ClientSession(headers={"Authorization": f"Bearer {access_token}"}) as session:
        yield session


def service_url(service: str = "external"):
    if service == "external":
        return test_settings.service_url
    elif service == "notifications":
        return test_settings.notifications_url
    return test_settings.ratings_url


@pytest_asyncio.fixture
def make_get_request(session):
    async def inner(
        path: str,
        params: dict | None = None,
        expected_status: HTTPStatus = HTTPStatus.OK,
        service: str = "external",
    ):
        url = service_url(service) + path
        async with session.get(url, params=params) as response:
            body = await response.json()
            status = response.status
        if status != expected_status:
            raise ValueError(f"Expected response status {expected_status}, got {status}: {body}")
        return body

    return inner


@pytest_asyncio.fixture
def make_post_request(session):
    async def inner(
        path: str,
        params: dict | None = None,
        expected_status: HTTPStatus = HTTPStatus.OK,
        service: str = "external",
    ):
        url = service_url(service) + path
        async with session.post(url, json=params) as response:
            body = await response.json()
            status = response.status
        if status != expected_status:
            raise ValueError(f"Expected response status {expected_status}, got {status}: {body}")
        return body

    return inner


@pytest_asyncio.fixture
def make_delete_request(session):
    async def inner(
        path: str,
        params: dict | None = None,
        expected_status: HTTPStatus = HTTPStatus.OK,
        service: str = "external",
    ):
        url = service_url(service) + path
        async with session.delete(url, params=params) as response:
            body = await response.json()
            status = response.status
        if status != expected_status:
            raise ValueError(f"Expected response status {expected_status}, got {status}: {body}")
        return body

    return inner
