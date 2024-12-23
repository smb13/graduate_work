import logging
import os

import sentry_sdk
from pydantic import Field
from pydantic_settings import BaseSettings
from sentry_sdk.integrations.logging import LoggingIntegration

# Инициализация Sentry SDK если есть env SENTRY_DSN
if SENTRY_DSN := os.getenv("SENTRY_DSN"):
    sentry_logging = LoggingIntegration(
        level=logging.WARNING,  # Захват логов уровня WARNING и выше
        event_level=logging.ERROR,  # Отправка событий в Sentry начиная с уровня ERROR
    )

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[sentry_logging],
        traces_sample_rate=float(os.getenv("TRACES_SAMPLE_RATE", 0.01)),
        profiles_sample_rate=float(os.getenv("PROFILES_SAMPLE_RATE", 0.01)),
    )


class Settings(BaseSettings):
    postgres_user: str = "etl"
    postgres_password: str
    postgres_movies_db: str = "movies_database"
    postgres_port: int = 5432
    postgres_host: str = "postgres"

    elastic_port: int = 9200
    elastic_host: str = "elastic"

    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = Field(alias="REDIS_DB_ETL", default=2)

    batch_size: int = 100


settings = Settings()
