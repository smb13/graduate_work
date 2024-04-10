from logging import config as logging_config
from typing import Any

import backoff
from pika.exceptions import AMQPError
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    name: str = Field(default="EPK Service")

    debug: bool = False
    enable_tracer: bool = False

    authjwt_secret_key: str = Field(default="movies_token_secret", alias="JWT_ACCESS_TOKEN_SECRET_KEY")

    jaeger_agent_port: int = 6831
    jaeger_agent_host: str = "jaeger"

    model_config = SettingsConfigDict(extra="ignore")


# Класс настройки Kafka
class RabbitMQSettings(BaseSettings):
    username: str = Field(alias="RABBIT_USER")
    password: str = Field(alias="RABBIT_PASSWORD")
    host: str = Field(default="rabbitmq")
    port: str = Field(default="5672")
    exchange: str = Field(default="")
    virtual_host: str = Field(default="/")

    model_config = SettingsConfigDict(env_prefix="rabbit_", extra="ignore")

    def get_dsn(self) -> str:
        return f"amqp://{self.username}:{self.password}@{self.host}:{self.port}{self.virtual_host}"

    @staticmethod
    def get_backoff_settings() -> dict[str, Any]:
        """
        Получение настроек для backoff
        """
        return {
            "wait_gen": backoff.expo,
            "exception": AMQPError,
            "logger": "rmq_publisher",
            "base": 2,
            "factor": 1,
            "max_value": 60,
        }


class GunicornSettings(BaseSettings):
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    workers: int = Field(default=2)
    loglevel: str = Field(default="debug")
    model_config = SettingsConfigDict(env_prefix="epk_api_gunicorn_", extra="ignore")


settings = Settings()
gunicorn_settings = GunicornSettings()
rabbitmq_settings = RabbitMQSettings()
