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

    authjwt_secret_key: str = Field(..., alias="JWT_ACCESS_TOKEN_SECRET_KEY")

    # Настройки Mongo: mongodb+srv://user:pass@cluster.mongodb.net/myFirstDatabase
    mongo_dsn: str = "mongodb://localhost"
    mongo_db: str = "movies"
    mongo_rating_collection: str = "ratings"
    mongo_review_collection: str = "review"
    mongo_review_rating_collection: str = "review_rating"
    mongo_bookmarks_collection: str = "bookmarks"

    jaeger_agent_port: int = 6831
    jaeger_agent_host: str = "jaeger"

    page_size: int = 50
    page_size_max: int = 100


# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

settings = Settings()
