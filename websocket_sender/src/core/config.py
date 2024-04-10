import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")


class ProjectSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", env_file=ENV_PATH, env_file_encoding="utf-8")
    log_level: int = Field(default=20)
    log_format: str = Field(default='%(asctime)s [%(levelname)s] [in %(filename)s: line %(lineno)d] - "%(message)s"')
    backoff_max_tries: int = Field(default=30)  # кол-во попыток переподключения к БД при потери соединения
    jwt_secret: str = Field(default="BIG_BIG_SECRET")


class WebsocketSettings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=ENV_PATH,
        env_prefix="websocket_sender_",
        env_file_encoding="utf-8",
    )
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8080)
    exchange: str = Field(default="websocket")


class RabbitSettings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=ENV_PATH,
        env_prefix="rabbit_",
        env_file_encoding="utf-8",
    )
    host: str = Field(default="rabbit")
    port: int = Field(default=5672)
    user: str = Field(default="rabbit")
    password: str = Field(default="rabbit")


class Settings:
    app = ProjectSettings()
    websocket = WebsocketSettings()
    rabbit = RabbitSettings()


settings = Settings()
