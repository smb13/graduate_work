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

    # Настройки PostgreSQL
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_user: str
    postgres_password: str
    postgres_auth_db: str

    page_size: int = 10
    page_size_max: int = 100

    cache_expires_in_seconds: int = 60 * 5  # 5 минут

    jwt_access_token_secret_key: str = "movies_token_secret"
    jwt_access_token_expires_minutes: int = 60

    yookassa_account_id: str
    yookassa_secret_key: str

    jaeger_agent_port: int = 6831
    payment_return_url: str = "http://localhost:8000/payment/return"

    subscription_service_host: str = "http://subscription"
    subscription_service_port: str = "8000"


# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

settings = Settings()
