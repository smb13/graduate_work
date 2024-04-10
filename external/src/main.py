from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from http import HTTPStatus

import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request, Response
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis

from api.routers import all_v1_routers
from core.config import settings
from core.tracer import configure_tracer
from db import elastic, redis

description = """Information about films, genres and people involved in the creation of the work"""


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db)
    elastic.es = AsyncElasticsearch(
        hosts=[{"host": settings.elastic_host, "port": settings.elastic_port, "scheme": "http"}],
    )
    yield
    await redis.redis.close()
    await elastic.es.close()


app = FastAPI(
    title="Read-only API для онлайн-кинотеатра",
    description=description,
    version="1.0.0",
    docs_url=settings.url_prefix + "/api/openapi",
    redoc_url=settings.url_prefix + "/api/redoc",
    openapi_url=settings.url_prefix + "/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

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
        port=8000,
    )
