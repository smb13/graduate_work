import logging
from collections.abc import Callable
from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import Any

import uvicorn
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from api.v1 import health_check, notices
from core.config import rabbitmq_settings, settings
from core.logger import LOGGING
from core.tracer import configure_tracer
from db import rabbitmq


@asynccontextmanager
async def lifespan(_: FastAPI) -> Any:
    # Создаем паблишер для RabbitMQ.
    rabbitmq.rmq_publisher = rabbitmq.RmqPublisher(
        exchange=rabbitmq_settings.exchange,
        queues=rabbitmq.get_rmq_queues_list(),
        host=rabbitmq_settings.host,
        port=rabbitmq_settings.port,
        virtual_host=rabbitmq_settings.virtual_host,
        username=rabbitmq_settings.username,
        password=rabbitmq_settings.password,
    )
    rabbitmq.rmq_publisher.start()

    yield

    # Отключаемся от RabbitMQ
    rabbitmq.rmq_publisher.stop()


@AuthJWT.load_config
def get_config() -> object:
    return settings


app = FastAPI(
    # Название проекта, используемое в документации.
    title=settings.name,
    # Адрес документации (swagger).
    docs_url="/api/openapi",
    # Адрес документации (openapi).
    openapi_url="/api/openapi.json",
    # Оптимизация работы с JSON-сериализатором.
    default_response_class=ORJSONResponse,
    # Указываем функцию, обработки жизненного цикла приложения.
    lifespan=lifespan,
    # Описание сервиса
    description="API информации о ",
)

# Подключаем роутер к серверу с указанием префикса для API
app.include_router(notices.router, prefix="/api/v1")
app.include_router(health_check.router, prefix="/health_check/v1")


if settings.enable_tracer:
    configure_tracer()
    FastAPIInstrumentor.instrument_app(app)


@app.middleware("http")
async def before_request(request: Request, call_next: Callable) -> Response:
    if not settings.debug and not request.headers.get("X-Request-Id"):
        return ORJSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"detail": "X-Request-Id header is required"})
    return await call_next(request)


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(_: Request, exc: AuthJWTException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


if __name__ == "__main__":
    # Запускаем приложение с помощью uvicorn сервера.
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
