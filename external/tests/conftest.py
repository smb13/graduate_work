from collections.abc import Callable
from typing import TYPE_CHECKING, Any

import pytest

from fastapi.testclient import TestClient

from main import app as fastapi_app
from models.genre import Genre as ModelGenre

if TYPE_CHECKING:
    from fastapi import FastAPI


# Create a new application for testing
@pytest.fixture()
def app() -> "FastAPI":
    return fastapi_app


# Make requests in our tests
@pytest.fixture()
def client(app: "FastAPI") -> TestClient:
    return TestClient(app=app, base_url="http://testserver")


@pytest.fixture()
def mock_service(app: "FastAPI") -> Callable:
    def _service_mocker(get_service_func, func_name, result):
        class MockFilmService:
            pass

        async def func(self, *args, **kwargs) -> Any:
            return result

        setattr(MockFilmService, func_name, func)

        def fake_get_film_service():
            return MockFilmService()

        app.dependency_overrides[get_service_func] = fake_get_film_service

    return _service_mocker


@pytest.fixture(scope="session", autouse=True)
def faker_session_locale():
    return ["it_IT"]


@pytest.fixture()
def genre(faker):
    return ModelGenre(id=faker.uuid4(), name=faker.word())
