import pytest

import pytest_asyncio
from redis import Redis

pytestmark = [
    pytest.mark.asyncio(),
]


@pytest_asyncio.fixture(autouse=True)
async def _clear_cache(redis: Redis):
    yield
    await redis.flushall()


async def test_genres_retrieve(make_get_request, redis_get, redis_flush):
    uuid = "120a21cf-9097-479e-904a-13dd7198c1dd"

    await redis_flush()

    # Пока что кэш пуст
    cache_data = await redis_get("genres", {"id": uuid})
    assert cache_data is None

    # Запрашиваем данные из базы, они должны закэшироваться
    await make_get_request(f"/api/v1/genres/{uuid}")

    # Теперь в кэше есть данные
    cache_data = await redis_get("genres", {"id": uuid})
    assert cache_data == {"id": uuid, "name": "Adventure"}
