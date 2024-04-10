from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from http import HTTPStatus

import uvicorn
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
    await mongo.mongo[settings.mongo_db][settings.mongo_notifications_collection].create_index(
        ["id"],
        unique=True,
        background=True,
    )
    await mongo.mongo[settings.mongo_db][settings.mongo_notifications_collection].create_index(
        ["type", "delivered_at"],
        unique=False,
        background=True,
    )
    await mongo.mongo[settings.mongo_db][settings.mongo_notifications_collection].create_index(
        ["type", "to", "delivered_at"],
        unique=False,
        background=True,
    )
    await mongo.mongo[settings.mongo_db][settings.mongo_notifications_collection].create_index(
        ["mark"],
        unique=False,
        background=True,
    )
    yield
    mongo.mongo.close()


app = FastAPI(
    title="API для сервиса нотификаций",
    version="1.0.0",
    docs_url=settings.url_prefix + "/api/openapi",
    redoc_url=settings.url_prefix + "/api/redoc",
    openapi_url=settings.url_prefix + "/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)


@app.middleware("http")
async def before_request(request: Request, call_next: Callable) -> Response:
    if not settings.debug and not request.headers.get("X-Request-Id"):
        return ORJSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"detail": "X-Request-Id header is required"})
    return await call_next(request)


app.include_router(all_v1_routers)

FastAPIInstrumentor.instrument_app(app)

if __name__ == "__main__":
    if settings.enable_tracer:
        configure_tracer()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
    )
