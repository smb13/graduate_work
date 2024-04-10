import logging
import sys

from config import settings
from etl import etl_data

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    postgres_dsn = {
        "dbname": settings.postgres_movies_db,
        "user": settings.postgres_user,
        "password": settings.postgres_password,
        "host": "postgres",
        "port": settings.postgres_port,
        "options": "-c search_path=content,public",
    }
    redis_dsn = {
        "host": "redis",
        "port": settings.redis_port,
        "db": settings.redis_db,
    }
    elastic_host = {
        "host": "elastic",
        "port": settings.elastic_port,
        "scheme": "http",
    }
    batch_size = settings.batch_size

    etl_data(postgres_dsn, redis_dsn, elastic_host, batch_size)
