from functools import lru_cache
from uuid import UUID

import bson
from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from motor.core import AgnosticClient

from core.config import settings
from db.mongo import get_mongo
from schemas.bookmarks import BookmarksListResponse
from services.base import BaseService


class BookmarksService(BaseService):
    """
    Класс для реализации логики работы с закладками.
    """

    async def add(self, movie_id: UUID) -> None:
        await self.db_bookmarks().update_one(
            {
                "movie_id": bson.Binary.from_uuid(movie_id),
                "user_id": (await self.jwt.get_raw_jwt())["sub"],
            },
            {"$set": {}},
            upsert=True,
        )

    async def remove(self, movie_id: UUID) -> None:
        await self.db_bookmarks().delete_one(
            {
                "movie_id": bson.Binary.from_uuid(movie_id),
                "user_id": (await self.jwt.get_raw_jwt())["sub"],
            },
        )

    async def list(self, page: int = 1, page_size: int = settings.page_size) -> BookmarksListResponse:
        bookmarks = (
            await self.db_bookmarks()
            .aggregate(
                list(
                    filter(
                        None,
                        [
                            {"$match": {"user_id": (await self.jwt.get_raw_jwt())["sub"]}},
                            {"$project": {"_id": 0, "movie_id": 1}},
                            {"$sort": {"_id": 1}},
                            {
                                "$facet": {
                                    "bookmarks": [
                                        {
                                            "$skip": (page - 1) * page_size or 0,
                                        },
                                        {
                                            "$limit": page_size or settings.page_size_max,
                                        },
                                    ],
                                    "total": [{"$count": "total"}],
                                },
                            },
                            {"$project": {"bookmarks": 1, "total": {"$arrayElemAt": ["$total.total", 0]}}},
                        ],
                    ),
                ),
            )
            .next()
        )

        return BookmarksListResponse(
            total=bookmarks.get("total", 0),
            bookmarks=[bookmark["movie_id"] for bookmark in bookmarks["bookmarks"]],
        )


@lru_cache
def get_bookmarks_service(
    jwt: AuthJWT = Depends(),
    mongo: AgnosticClient = Depends(get_mongo),
) -> BookmarksService:
    return BookmarksService(jwt, mongo)
