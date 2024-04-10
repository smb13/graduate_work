import os
from logging import config as logging_config

from pydantic import Field
from pydantic_settings import BaseSettings

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    url_prefix: str = ""

    debug: bool = False
    enable_tracer: bool = False

    # Настройки Redis
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = Field(alias="REDIS_DB_MOVIES", default=0)

    # Настройки Elasticsearch
    elastic_host: str = "elastic"
    elastic_port: int = 9200

    page_size: int = 10
    page_size_max: int = 100

    cache_expires_in_seconds: int = 60 * 5  # 5 минут

    jwt_access_token_secret_key: str = "movies_token_secret"
    jwt_access_token_expires_minutes: int = 60
    jwt_refresh_token_secret_key: str = "movies_refresh_secret"
    jwt_refresh_token_expires_minutes: int = 60 * 24 * 7

    jaeger_agent_port: int = 6831


# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

settings = Settings()
