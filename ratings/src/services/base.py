from async_fastapi_jwt_auth import AuthJWT
from motor.core import AgnosticClient, AgnosticCollection

from core.config import settings


class BaseService:
    """
    Базовый класс для работы с бизнес-логикой
    """

    def __init__(self, jwt: AuthJWT, mongo: AgnosticClient) -> None:
        self.jwt = jwt
        self.mongo = mongo

    def db(self) -> AgnosticCollection:
        return self.mongo[settings.mongo_db][settings.mongo_rating_collection]

    def db_review(self) -> AgnosticCollection:
        return self.mongo[settings.mongo_db][settings.mongo_review_collection]

    def db_review_ratings(self) -> AgnosticCollection:
        return self.mongo[settings.mongo_db][settings.mongo_review_rating_collection]

    def db_bookmarks(self) -> AgnosticCollection:
        return self.mongo[settings.mongo_db][settings.mongo_bookmarks_collection]
