from abc import ABCMeta, abstractmethod
from functools import lru_cache
from typing import Any

from authlib.integrations.starlette_client import OAuth
from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from db.alchemy import get_session

oauth: OAuth = OAuth()


class AbstractOAuth(metaclass=ABCMeta):
    __slots__ = ("session", "redis")

    def __init__(
        self,
        session: AsyncSession,
        redis: Redis | None = None,
    ) -> None:
        self.session = session
        self.redis = redis

    @abstractmethod
    def get_auth_provider(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @classmethod
    @lru_cache
    def get_provider_service(cls, request: Request, alchemy: AsyncSession = Depends(get_session)) -> "AbstractOAuth":
        return cls(session=alchemy, redis=None)
