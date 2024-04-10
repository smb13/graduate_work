from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from core.config import settings
from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre
from services.base import BaseService
from services.cache import RedisCache
from services.database import ElasticDatabase


@lru_cache
def get_genres_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> BaseService:
    cache = RedisCache(redis, cache_prefix="genres", model=Genre, expires=settings.cache_expires_in_seconds)
    database = ElasticDatabase(
        elastic,
        index="genres",
        model=Genre,
        search_fields=("name",),
    )
    return BaseService(cache=cache, database=database)
