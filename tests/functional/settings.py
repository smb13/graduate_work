from pydantic import BaseModel
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    # Настройки Redis
    redis_host: str = "redis"
    redis_port: int = 6379

    # Настройки Elasticsearch
    elastic_host: str = "elastic"
    elastic_port: int = 9200

    # Должно соответствовать URL приложения в контейнере
    service_url: str = "http://external_dev:8000"
    ratings_url: str = "http://ratings_dev:8080"
    notifications_url: str = "http://notifications_dev:8000"

    # Настройки приложения
    page_size: int = 10
    page_size_max: int = 100

    # JWT настройки
    jwt_access_token_secret_key: str = "movies_token_secret"


class AuthJWTSettings(BaseModel):
    authjwt_secret_key: str = "movies_token_secret"


test_settings = TestSettings()
authjwt_settings = AuthJWTSettings(authjwt_secret_key=test_settings.jwt_access_token_secret_key)
