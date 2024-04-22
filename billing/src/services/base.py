from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDBService:
    def __init__(
        self,
        session: AsyncSession,
        redis: Redis,
    ) -> None:
        self.session = session
        self.redis = redis
