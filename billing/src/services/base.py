from typing import Any

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


class BasePaymentService:
    def __init__(
        self,
        payment_client: Any,
    ) -> None:
        self.payment_client = payment_client
