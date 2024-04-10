from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    def __init__(
        self,
        session: AsyncSession,
        redis: Redis | None = None,
    ) -> None:
        self.session = session
        self.redis = redis
