import logging
from contextlib import closing, suppress
from typing import Any

import backoff
import psycopg2
from conveyors.genres import GenresETL
from conveyors.movies import MoviesETL
from conveyors.persons import FilmPersonsETL, PersonsETL
from elastic_transport import ConnectionError as ElasticConnectionError
from elasticsearch import Elasticsearch
from exceptions import ElasticError
from psycopg2.extras import DictCursor
from redis import ConnectionError as RedisConnectionError, Redis
from redis.exceptions import LockError
from state import RedisStorage, State

logger = logging.getLogger(__name__)


@backoff.on_exception(
    backoff.expo,
    (ElasticConnectionError, psycopg2.OperationalError, RedisConnectionError),
    max_time=60,
)  # type: ignore
def etl_data(
    postgres_dsn: dict[str, Any],
    redis_dsn: dict[str, Any],
    elastic_host: dict[str, Any],
    batch_size: int,
) -> None:
    """Управляет процессом загрузки данных, блокировками и backoff"""
    redis = Redis(**redis_dsn)
    logger.info('starting "etl_data"')

    try:
        with redis.lock("etl_data", timeout=60 * 10, blocking=False):
            client = Elasticsearch([elastic_host], request_timeout=20)
            storage = RedisStorage(redis)
            state = State(storage)

            with closing(
                psycopg2.connect(**postgres_dsn, cursor_factory=DictCursor),
            ) as pg_conn:
                etl_params = {
                    "postgres": pg_conn,
                    "elasticsearch": client,
                    "batch_size": batch_size,
                    "state": state,
                }
                for etl_class in (MoviesETL, GenresETL, PersonsETL, FilmPersonsETL):
                    with suppress(ElasticError):
                        etl_class(**etl_params).etl()  # type: ignore

    except LockError:
        logger.warning('Unable to acquire lock "etl_movies"')
        return
