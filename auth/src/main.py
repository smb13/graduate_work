from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from http import HTTPStatus

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import ORJSONResponse
from fastapi_pagination import add_pagination
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from starlette.middleware.sessions import SessionMiddleware

from api.routers import all_v1_routers
from core.config import settings
from core.tracer import configure_tracer
from db import alchemy, redis
from db.alchemy import create_database


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db)

    dsn = "postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}".format(
        user=settings.postgres_user,
        password=settings.postgres_password,
        host=settings.postgres_host,
        port=settings.postgres_port,
        db_name=settings.postgres_auth_db,
    )
    alchemy.engine = create_async_engine(dsn, echo=True, future=True)
    alchemy.async_session = sessionmaker(alchemy.engine, class_=AsyncSession, expire_on_commit=False)

    # Импорт моделей необходим для их автоматического создания
    from models import User  # noqa

    if settings.debug:
        await create_database()

    yield

    await redis.redis.close()

    # Для очистки базы данных при выключении сервера if settings.debug: await purge_database()


app = FastAPI(
    title="Authentication and Authorization API",
    description="OAuth2 Tokens, Users, Roles",
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


# we need this to save temporary code & state in session
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret_key)


@app.middleware("http")
async def change_host_header(request: Request, call_next: Callable) -> Response:
    """Update request scope: set host header and scope scheme to the one from the url.
    Required to make starlette.requests.Request.url_for with correct `base_url`."""

    headers = dict(request.scope["headers"])

    if host := headers.get(b"x-forwarded-host"):
        headers[b"host"] = host
        request.scope["headers"] = [(k, v) for k, v in headers.items()]

    if scheme := headers.get(b"x-forwarded-proto"):
        request.scope["scheme"] = scheme.decode("latin-1")

    return await call_next(request)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
    )
