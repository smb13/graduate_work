import os
from datetime import time

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")


class ProjectSettings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=ENV_PATH,
        env_prefix="app_sender_",
        env_file_encoding="utf-8",
    )
    debug: bool = Field(default=False)
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=9746)
    name: str = Field(default="email-sender")
    prefix: str = Field(default="email-sender")
    version: str = Field(default="v1")
    log_level: int = Field(default=10)
    log_format: str = Field(default='%(asctime)s [%(levelname)s] [in %(filename)s: line %(lineno)d] - "%(message)s"')
    jwt_secret: str = Field(..., alias="JWT_ACCESS_TOKEN_SECRET_KEY")
    allow_origins: list[str] = Field(default=["*"])


class EmailSettings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=ENV_PATH,
        env_prefix="email_sender_",
        env_file_encoding="utf-8",
    )
    api_sendgrid: str = Field(default="default")
    from_email: str = Field(default="middle-team@yandex.ru")
    start_time: time = time(hour=9)
    stop_time: time = time(hour=21)
    max_retries_to_send: int = Field(default=5)


class RabbitSettings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=ENV_PATH,
        env_prefix="rabbit_sender_",
        env_file_encoding="utf-8",
    )
    host: str = Field(default="localhost")
    port: int = Field(default=5672)
    user: str = Field(default="user")
    password: str = Field(default="password")


class Settings:
    app = ProjectSettings()
    rabbit = RabbitSettings()
    email = EmailSettings()


settings = Settings()
