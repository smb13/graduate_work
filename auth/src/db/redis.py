import typing

if typing.TYPE_CHECKING:
    from redis.asyncio import Redis

redis: "Redis | None" = None


async def get_redis() -> "Redis":
    return redis
