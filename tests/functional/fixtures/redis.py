from typing import Any

import pytest_asyncio
from orjson import loads
from redis.asyncio import Redis
from settings import test_settings
from test_utils.cache import make_cache_key


@pytest_asyncio.fixture(scope="session")
async def redis():
    redis = Redis(host=test_settings.redis_host, port=test_settings.redis_port)
    yield redis
    await redis.aclose()


@pytest_asyncio.fixture(scope="session")
def redis_get(redis):
    async def inner(cache_prefix, request_data: dict["str", Any]):
        cache_key = make_cache_key(cache_prefix, request_data)
        data = await redis.get(cache_key)
        return loads(data) if data else None

    return inner


@pytest_asyncio.fixture(scope="session")
def redis_flush(redis):
    async def inner():
        await redis.flushall()

    return inner
