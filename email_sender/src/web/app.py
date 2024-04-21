from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from src.api.routers import all_v1_routers
from src.core.config import settings
from src.core.logger import logging_init
from src.web.middlewares import Middleware


@asynccontextmanager
async def lifespan(app: FastAPI, *args, **kwargs) -> AsyncGenerator[Any, Any]:
    """Инициализация при старте приложения."""

    logging_init()
    yield


def init_app(*, is_test: bool = False) -> FastAPI:
    _app = FastAPI(
        title=settings.app.name,
        description="Сервис для отправки сообщений по email",
        version=settings.app.version,
        docs_url=f"/{settings.app.prefix}/api/v1/docs",
        openapi_url=f"/{settings.app.prefix}/openapi.json",
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    _setup_middleware(_app)
    _setup_routes(_app)

    return _app


def _setup_middleware(app: FastAPI) -> None:
    Middleware().setup_middlewares(app=app)


def _setup_routes(app: FastAPI) -> None:
    app.include_router(all_v1_routers, prefix=f"/{settings.app.prefix}")
