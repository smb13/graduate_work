from typing import Any

import backoff
from pika.exceptions import AMQPError
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    name: str = Field(default="EPK Worker Service")

    debug: bool = False
    enable_tracer: bool = False

    authjwt_secret_key: str = Field(default="movies_token_secret", alias="JWT_ACCESS_TOKEN_SECRET_KEY")

    jaeger_agent_port: int = 6831
    jaeger_agent_host: str = "jaeger"

    auth_host: str = Field(default="auth")
    auth_port: str = Field(default="8000")
    auth_get_users_endpoint: str = Field(default="/api/v1/users")

    events_admin_host: str = Field(default="events_admin")
    events_admin_port: str = Field(default="8000")
    events_admin_get_template_endpoint: str = Field(default="/api/v1/templates")
    events_admin_subscribers_endpoint: str = Field(default="/api/v1/subscribers")

    ratings_host: str = Field(default="ratings")
    ratings_port: str = Field(default="8080")

    notification_host: str = Field(default="notification")
    notification_port: str = Field(default="8000")
    notification_push_endpoint: str = Field(default="/api/v1/push")
    notification_email_endpoint: str = Field(default="/api/v1/email")

    backoff_max_tries: int = 30
    external_api_backoff_max_tries: int = 1

    max_batch_size: int = 1000

    log_format: str = '%(asctime)s [%(levelname)s] [in %(filename)s: line %(lineno)d] - "%(message)s"'


# Класс настройки RabbitMQ
class RabbitMQSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="rabbit_",
        extra="ignore",
    )

    username: str = Field(alias="RABBIT_USER")
    password: str = Field(alias="RABBIT_PASSWORD")
    host: str = Field(default="rabbitmq")
    port: str = Field(default="5672")
    consume_exchange: str = Field(default="consume")
    publish_exchange: str = Field(default="publish")
    virtual_host: str = Field(default="/")
    time_to_consume: int = Field(default=5)
    prefetch_count: int = Field(default=100)
    message_ttl: int = Field(default=86400000)

    consume_queue: str = Field(default="push.review_like")
    publish_queue_suffix: str = Field(default=".sender")

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
            "base": 2,
            "factor": 1,
            "max_value": 60,
            "max_tries": 30,
        }


class AuthJwtSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    authjwt_secret_key: str = Field(default="movies_token_secret", alias="JWT_ACCESS_TOKEN_SECRET_KEY")


authjwt_settings = AuthJwtSettings()
settings = Settings()
rabbitmq_settings = RabbitMQSettings()
