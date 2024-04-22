from redis.asyncio import Redis

redis: Redis | None = None


async def get_redis() -> Redis:
    if not redis:
        raise RuntimeError("Redis is not initialized")

    return redis
