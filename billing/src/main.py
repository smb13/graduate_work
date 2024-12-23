from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from http import HTTPStatus

import uvicorn
from authlib.integrations import httpx_client
from clients import alchemy, redis, subscription
from clients.yookassa import client as yookassa
from fastapi import FastAPI, Request, Response
from fastapi.responses import ORJSONResponse
from fastapi_pagination import add_pagination
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from api.routers import all_v1_routers
from core.config import settings
from core.tracer import configure_tracer

description = """Проведение платежей и автоплатежей, получение статуса оплаты, отмена оплаты."""


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    redis.redis = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
    )

    dsn = "postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}".format(
        user=settings.postgres_user,
        password=settings.postgres_password,
        host=settings.postgres_host,
        port=settings.postgres_port,
        db_name=settings.postgres_billing_db,
    )
    alchemy.engine = create_async_engine(dsn, echo=True, future=True)
    alchemy.AsyncSessionLocal = async_sessionmaker(
        alchemy.engine,
        expire_on_commit=False,
    )

    yookassa.yookassa = yookassa.YooKassa(
        api_key=settings.yookassa_secret_key,
        shop_id=settings.yookassa_account_id,
    )

    subscription.client = httpx_client.AsyncOAuth2Client(
        base_url=settings.subscription_service_base_url,
        token_endpoint_auth_method="client_secret_post",
    )

    # Импорт моделей необходим для их автоматического создания
    from models import Transaction  # noqa

    if settings.debug:
        await alchemy.create_database()

    yield

    await redis.redis.close()

    await subscription.client.aclose()

    # Для очистки базы данных при выключении сервера if settings.debug: await alchemy.purge_database()


app = FastAPI(
    title="API Биллинга",
    description=description,
    version="1.0.0",
    docs_url=settings.url_prefix + "/api/openapi",
    redoc_url=settings.url_prefix + "/api/redoc",
    openapi_url=settings.url_prefix + "/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

add_pagination(app)


app.include_router(all_v1_routers)


if settings.enable_tracer:
    configure_tracer()
    FastAPIInstrumentor.instrument_app(app)


@app.middleware("http")
async def before_request(request: Request, call_next: Callable) -> Response:
    if not settings.debug and not request.headers.get("X-Request-Id"):
        return ORJSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"detail": "X-Request-Id header is required"})
    return await call_next(request)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
    )
