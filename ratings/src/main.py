from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from http import HTTPStatus

import uvicorn
from async_fastapi_jwt_auth import AuthJWT
from fastapi import FastAPI, Request, Response
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from api.routers import all_v1_routers
from core.config import settings
from core.tracer import configure_tracer
from db import mongo


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator:
    mongo.connect(settings.mongo_dsn)
    mongo.mongo[settings.mongo_db][settings.mongo_rating_collection].create_index(
        ["movie_id", "user_id"],
        unique=True,
        background=True,
    )
    mongo.mongo[settings.mongo_db][settings.mongo_review_collection].create_index(
        ["movie_id", "user_id"],
        unique=True,
        background=True,
    )
    mongo.mongo[settings.mongo_db][settings.mongo_bookmarks_collection].create_index(
        ["user_id", "movie_id"],
        unique=True,
        background=True,
    )
    yield
    mongo.mongo.close()


@AuthJWT.load_config
def get_config() -> object:
    return settings


app = FastAPI(
    title="API для онлайн-кинотеатра для оценок пользователей",
    version="1.0.0",
    docs_url=settings.url_prefix + "/api/openapi",
    redoc_url=settings.url_prefix + "/api/redoc",
    openapi_url=settings.url_prefix + "/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

if settings.enable_tracer:
    configure_tracer()
    FastAPIInstrumentor.instrument_app(app)

app.include_router(all_v1_routers)


@app.middleware("http")
async def before_request(request: Request, call_next: Callable) -> Response:
    if not settings.debug and not request.headers.get("X-Request-Id"):
        return ORJSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"detail": "X-Request-Id header is required"})
    return await call_next(request)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
    )
