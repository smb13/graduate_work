from logging import config as logging_config

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.logger import LOGGING
from core.utils import get_base_url

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    subscriptions_project_name: str = Field("Subscriptions Service")
    authjwt_secret_key: str = Field(default="movies_token_secret", alias="JWT_ACCESS_TOKEN_SECRET_KEY")
    authjwt_algorithm: str = Field(default="HS256")

    local_user_email: str
    local_user_password: str
    debug: bool = Field(default=False, alias="DEBUG")
    enable_tracer: bool = False
    jaeger_agent_port: int = 6831

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Класс настройки Postgres
class PostgresSettings(BaseSettings):
    subscriptions_db: str = Field("subscriptions_database")
    user: str
    password: str
    host: str = Field("localhost")
    port: int = Field(5432)
    echo: bool = Field(True)
    dbschema: str = Field("public")

    model_config = SettingsConfigDict(env_prefix="postgres_", env_file=".env", extra="ignore")

    def get_dsn(self) -> str:
        return f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.subscriptions_db}"

    def get_connection_info(self) -> dict:
        return {
            "url": self.get_dsn(),
            "connect_args": {"options": f"-c search_path={self.dbschema},public"},
        }


# Класс настройки сервиса Billing
class BillingSettings(BaseSettings):
    service_host: str = Field("billing")
    service_port: str = Field("8000")
    new_uri: str = Field("/api/v1/payments/new")
    renew_uri: str = Field("/api/v1/payments/renew")
    refund_uri: str = Field("/api/v1/payments/refund")
    backoff_max_tries: int = Field(30)

    @property
    def service_base_url(self) -> str:
        return get_base_url(
            billing_settings.service_host,
            billing_settings.service_port,
        )

    model_config = SettingsConfigDict(env_prefix="billing_", env_file=".env", extra="ignore")


class AuthSettings(BaseSettings):
    service_host: str = "auth"
    service_port: str = "8000"

    @property
    def service_base_url(self) -> str:
        return get_base_url(
            auth_settings.service_host,
            auth_settings.service_port,
        )

    model_config = SettingsConfigDict(env_prefix="auth_", env_file=".env", extra="ignore")


# Класс настройки Gunicorn
class GunicornSettings(BaseSettings):
    host: str = Field("0.0.0.0")
    port: int = Field(8000)
    workers: int = Field(2)
    loglevel: str = Field("debug")

    model_config = SettingsConfigDict(env_prefix="gunicorn_", env_file=".env", extra="ignore")


settings = Settings()
postgres_settings = PostgresSettings()
billing_settings = BillingSettings()
gunicorn_settings = GunicornSettings()
auth_settings = AuthSettings()
