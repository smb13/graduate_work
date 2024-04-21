from logging import config as logging_config

from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class ProjectSettings(BaseSettings):
    name: str = Field('Subscriptions Service')
    authjwt_secret_key: str = Field(default="movies_token_secret", alias="JWT_ACCESS_TOKEN_SECRET_KEY")
    authjwt_algorithm: str = Field(default="HS256")
    debug: bool = Field(default=False, alias="DEBUG")

    model_config = SettingsConfigDict(env_prefix='project_', env_file='.env')


# Класс настройки Postgres
class PostgresSettings(BaseSettings):
    dbname: str = Field('movies_database')
    user: str = ...
    password: str = ...
    host: str = Field('localhost')
    port: int = Field(5432)
    echo: bool = Field(True)
    dbschema: str = Field('public')

    model_config = SettingsConfigDict(env_prefix='postgres_', env_file='.env')

    def get_dsn(self):
        return f'postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}'

    def get_connection_info(self):
        return {
            'url': self.get_dsn(),
            'connect_args': {'options': f"-c search_path={self.dbschema},public"}
        }


# Класс настройки сервиса Billing
class BillingSettings(BaseSettings):
    host: str = Field('billing')
    port: int = Field(8000)
    new_uri: str = Field('/api/v1/payments/new')
    renew_uri: str = Field('/api/v1/payments/renew')
    refund_uri: str = Field('/api/v1/payments/refund')

    def get_address(self):
        return f'http://{self.host}:{self.port}'

    model_config = SettingsConfigDict(env_prefix='billing_', env_file='.env')


# Класс настройки Elasticsearch
class GunicornSettings(BaseSettings):
    host: str = Field('0.0.0.0')
    port: int = Field(8000)
    workers: int = Field(2)
    loglevel: str = Field('debug')

    model_config = SettingsConfigDict(env_prefix='gunicorn_', env_file='.env')


project_settings = ProjectSettings()
postgres_settings = PostgresSettings()
billing_settings = BillingSettings()
gunicorn_settings = GunicornSettings()