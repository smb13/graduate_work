import logging
import typing
from contextlib import asynccontextmanager
from http import HTTPStatus

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from async_fastapi_jwt_auth import AuthJWT
from authlib.integrations import httpx_client
from fastapi import FastAPI, Response
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from starlette.requests import Request

from api.v1 import me_user_subscriptions, subscription_types, user_subscription_types, user_subscriptions
from core.config import postgres_settings, settings, billing_settings
from core.logger import LOGGING
from core.tracer import configure_tracer
from db import postgres, http


@asynccontextmanager
async def lifespan(_: FastAPI) -> typing.AsyncGenerator:
    from jobs.subscriptions_renewal import subscriptions_renewal_job

    postgres.engine = create_async_engine(
        **postgres_settings.get_connection_info(),
        echo=postgres_settings.echo,
        future=True,
    )
    postgres.async_session = async_sessionmaker(
        postgres.engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    if settings.debug:
        await postgres.create_database()

    http.client = httpx_client.AsyncOAuth2Client(
        base_url=billing_settings.service_base_url,
        token_endpoint_auth_method="client_secret_post",
    )

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        subscriptions_renewal_job,
        CronTrigger.from_crontab("* * * * *"),
    )
    scheduler.start()

    yield

    await http.client.aclose()

    scheduler.shutdown()


@AuthJWT.load_config
def get_config() -> "BaseSettings":
    return settings


app = FastAPI(
    # Название проекта, используемое в документации.
    title=settings.subscriptions_project_name,
    # Адрес документации (swagger).
    docs_url="/api/openapi",
    # Адрес документации (openapi).
    openapi_url="/api/openapi.json",
    # Оптимизация работы с JSON-сериализатором.
    default_response_class=ORJSONResponse,
    # Указываем функцию, обработки жизненного цикла приложения.
    lifespan=lifespan,
    # Описание сервиса
    description="API управления подписками",
)

# Подключаем роутер к серверу с указанием префикса для API (/v1/films).
app.include_router(subscription_types.router, prefix="/api/v1")
app.include_router(user_subscription_types.router, prefix="/api/v1")
app.include_router(me_user_subscriptions.router, prefix="/api/v1")
app.include_router(user_subscriptions.router, prefix="/api/v1")


if settings.enable_tracer:
    configure_tracer()
    FastAPIInstrumentor.instrument_app(app)


@app.middleware("http")
async def before_request(request: Request, call_next: typing.Callable) -> Response:
    if not settings.debug and not request.headers.get("X-Request-Id"):
        return ORJSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"detail": "X-Request-Id header is required"})
    return await call_next(request)


if __name__ == "__main__":
    # Запускаем приложение с помощью uvicorn сервера.
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
