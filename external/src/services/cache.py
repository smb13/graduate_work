from abc import ABC, abstractmethod
from typing import Any

from opentelemetry import trace
from orjson import dumps
from orjson.orjson import loads
from redis import Redis

from core.types import DataOptType, DataType, ModelType, RequestData


class BaseCache(ABC):
    def __init__(
        self,
        storage: Any,
        cache_prefix: str,
        model: type[ModelType],
        expires: int,
    ) -> None:
        self.storage = storage
        self.cache_prefix = cache_prefix
        self.model = model
        self.expires = expires

    @abstractmethod
    async def get(self, request_data: RequestData) -> DataOptType:
        """Получить данные из кэша"""

    @abstractmethod
    async def put(self, data: DataOptType, request_data: RequestData) -> None:
        """Отправить данные в кэш"""


tracer = trace.get_tracer(__name__)


class RedisCache(BaseCache):
    storage: Redis

    async def get(self, request_data: RequestData) -> DataOptType:
        """Gets data from Redis"""
        with tracer.start_as_current_span("redis-get"):
            data = await self.storage.get(self.make_cache_key(request_data))
            if not data:
                return None

            return self.load_cache_value(data)

    async def put(self, data: DataOptType, request_data: RequestData) -> None:
        """Puts data to Redis"""
        with tracer.start_as_current_span("redis-put"):
            await self.storage.set(
                name=self.make_cache_key(request_data),
                value=self.make_cache_value(data),
                ex=self.expires,
            )

    def make_cache_key(self, request_data: RequestData) -> str:
        return self.cache_prefix + "_" + dumps(request_data.model_dump(exclude_unset=True)).decode("UTF-8")

    def load_cache_value(self, data: bytes) -> DataOptType:
        data = loads(data)
        match data:  # noqa: R503
            case list():
                return [self.model.model_validate(film) for film in data]
            case dict():
                return self.model.model_validate(data)
            case _:
                return None

    @staticmethod
    def make_cache_value(data: DataType) -> bytes:
        match data:  # noqa: R503
            case list():
                return dumps([model.model_dump() for model in data])
            case ModelType():
                return dumps(data.model_dump())
            case _:
                raise TypeError(f"Invalid data type: {type(data)}")
