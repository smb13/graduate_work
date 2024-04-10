from functools import lru_cache
from uuid import UUID

import bson
from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from motor.core import AgnosticClient

from db.mongo import get_mongo
from schemas.ratings import RatingsResponse
from services.base import BaseService


class RatingsService(BaseService):
    """
    Класс для реализации логики работы с оценками фильмов.
    """

    async def like(self, movie_id: UUID) -> None:
        await self.set_rating(movie_id, 10)

    async def dislike(self, movie_id: UUID) -> None:
        await self.set_rating(movie_id, 1)

    async def set_rating(self, movie_id: UUID, rating: int) -> None:
        await self.db().update_one(
            {
                "movie_id": bson.Binary.from_uuid(movie_id),
                "user_id": (await self.jwt.get_raw_jwt())["sub"],
            },
            {"$set": {"rating": rating}},
            upsert=True,
        )

    async def remove_rating(self, movie_id: UUID) -> None:
        await self.db().update_one(
            {
                "movie_id": bson.Binary.from_uuid(movie_id),
                "user_id": (await self.jwt.get_raw_jwt())["sub"],
            },
            {"$unset": {"rating": 1}},
        )

    async def get_rating(self, movie_id: UUID) -> RatingsResponse:
        try:
            return RatingsResponse(
                **await self.db()
                .aggregate(
                    [
                        {"$match": {"movie_id": bson.Binary.from_uuid(movie_id)}},
                        {
                            "$group": {
                                "_id": "$movie_id",
                                "total": {"$sum": 1},
                                "likes": {"$sum": {"$cond": [{"$eq": ["$rating", 10]}, 1, 0]}},
                                "dislikes": {"$sum": {"$cond": [{"$eq": ["$rating", 1]}, 1, 0]}},
                                "average": {"$avg": "$rating"},
                                "rating": {
                                    "$sum": {
                                        "$cond": [
                                            {"$eq": ["$user_id", (await self.jwt.get_raw_jwt())["sub"]]},
                                            "$rating",
                                            0,
                                        ],
                                    },
                                },
                            },
                        },
                    ],
                )
                .next(),
            )  # Тут возможен только один элемент в ответе.
        except StopAsyncIteration:
            return RatingsResponse(average=0)


@lru_cache
def get_ratings_service(
    jwt: AuthJWT = Depends(),
    mongo: AgnosticClient = Depends(get_mongo),
) -> RatingsService:
    return RatingsService(jwt, mongo)
