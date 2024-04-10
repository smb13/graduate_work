from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from api.v1.models import FilmsSortKeys
from core.config import settings
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from services.base import BaseService
from services.cache import RedisCache
from services.database import ElasticDatabase


@lru_cache
def get_films_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> BaseService:
    cache = RedisCache(redis, cache_prefix="movies", model=Film, expires=settings.cache_expires_in_seconds)
    database = ElasticDatabase(
        elastic,
        index="movies",
        model=Film,
        sort_fields=tuple(key.value for key in FilmsSortKeys),
        search_fields=(
            "actors_names",
            "writers_names",
            "title",
            "description",
            "genre",
        ),
    )
    return BaseService(cache=cache, database=database)
