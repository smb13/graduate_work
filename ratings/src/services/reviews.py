from functools import lru_cache
from re import split
from typing import Any
from uuid import UUID

import bson
from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from motor.core import AgnosticClient

from core.config import settings
from db.mongo import get_mongo
from schemas.review import ReviewListResponse, ReviewResponse, ReviewSortKeys
from services.base import BaseService


class ReviewsService(BaseService):
    """
    Класс для реализации логики работы с рецензиями на фильмы.
    """

    async def add_review(self, movie_id: UUID, review: str) -> None:
        await self.db_review().update_one(
            {
                "movie_id": bson.Binary.from_uuid(movie_id),
                "user_id": (await self.jwt.get_raw_jwt())["sub"],
            },
            {"$set": {"review": review}},
            upsert=True,
        )

    async def remove_review(self, movie_id: UUID) -> None:
        review = await self.get_review(movie_id)
        await self.db_review_ratings().delete_many(
            {
                "movie_id": bson.Binary.from_uuid(movie_id),
                "review_id": bson.ObjectId(review.review_id),
            },
        )
        await self.db_review().delete_one({"_id": bson.ObjectId(review.review_id)})

    async def get_review(self, movie_id: UUID) -> ReviewResponse:
        result = await self.__get_review_list(
            match_stage={
                "$match": {
                    "movie_id": bson.Binary.from_uuid(movie_id),
                    "user_id": (await self.jwt.get_raw_jwt())["sub"],
                },
            },
        )
        return result.reviews[0] if result.total else ReviewResponse(review="")

    async def like(self, movie_id: UUID, review_id: str) -> None:
        await self.db_review_ratings().update_one(
            {
                "movie_id": bson.Binary.from_uuid(movie_id),
                "user_id": (await self.jwt.get_raw_jwt())["sub"],
                "review_id": bson.ObjectId(review_id),
            },
            {"$set": {"rating": 10}},
            upsert=True,
        )

    async def dislike(self, movie_id: UUID, review_id: str) -> None:
        await self.db_review_ratings().update_one(
            {
                "movie_id": bson.Binary.from_uuid(movie_id),
                "user_id": (await self.jwt.get_raw_jwt())["sub"],
                "review_id": bson.ObjectId(review_id),
            },
            {"$set": {"rating": 1}},
            upsert=True,
        )

    async def remove_rating(self, movie_id: UUID, review_id: str) -> None:
        await self.db_review_ratings().delete_one(
            {
                "movie_id": bson.Binary.from_uuid(movie_id),
                "user_id": (await self.jwt.get_raw_jwt())["sub"],
                "review_id": bson.ObjectId(review_id),
            },
        )

    async def get_review_list(
        self,
        movie_id: UUID,
        sort: ReviewSortKeys,
        page: int = 1,
        page_size: int = settings.page_size,
    ) -> ReviewListResponse:
        sort_split = split("_", sort.name if sort else "")
        return await self.__get_review_list(
            match_stage={"$match": {"movie_id": bson.Binary.from_uuid(movie_id)}},
            sort_stage={"$sort": {sort_split[0]: 1 if sort_split[1] == "desc" else -1}} if sort else None,
            skip=(page - 1) * page_size,
            limit=page_size,
        )

    async def __get_review_list(
        self,
        match_stage: dict[str, Any] = None,
        sort_stage: dict[str, Any] = None,
        skip: int = None,
        limit: int = None,
    ) -> ReviewListResponse:
        return ReviewListResponse(
            **await self.db_review()
            .aggregate(
                list(
                    filter(
                        None,
                        [
                            match_stage,
                            {
                                "$lookup": {  # type: ignore
                                    "from": settings.mongo_review_rating_collection,
                                    "localField": "_id",
                                    "foreignField": "review_id",
                                    "as": "review_data",
                                    "pipeline": [
                                        {
                                            "$group": {
                                                "_id": "$id",
                                                "likes": {"$sum": {"$cond": [{"$eq": ["$rating", 10]}, 1, 0]}},
                                                "dislikes": {"$sum": {"$cond": [{"$eq": ["$rating", 1]}, 1, 0]}},
                                                "average": {"$avg": "$rating"},
                                            },
                                        },
                                        {
                                            "$project": {"_id": 0},
                                        },
                                    ],
                                },
                            },
                            {
                                "$project": {  # type: ignore
                                    "_id": 0,
                                    "review_id": {"$toString": "$_id"},
                                    "movie_id": 1,
                                    "user_id": 1,
                                    "review": 1,
                                    "ratings": {"$arrayElemAt": ["$review_data", 0]},
                                },
                            },
                            {
                                "$project": {  # type: ignore
                                    "review_id": 1,
                                    "movie_id": 1,
                                    "user_id": 1,
                                    "review": 1,
                                    "likes": "$ratings.likes",
                                    "dislikes": "$ratings.dislikes",
                                    "average": "$ratings.average",
                                },
                            },
                            sort_stage,
                            {
                                "$facet": {  # type: ignore
                                    "reviews": [
                                        {
                                            "$skip": skip or 0,
                                        },
                                        {
                                            "$limit": limit or settings.page_size_max,
                                        },
                                    ],
                                    "total": [{"$count": "total"}],
                                },
                            },
                            {"$project": {"reviews": 1, "total": {"$arrayElemAt": ["$total.total", 0]}}},
                        ],
                    ),
                ),
            )
            .next(),
        )


@lru_cache
def get_review_service(
    jwt: AuthJWT = Depends(),
    mongo: AgnosticClient = Depends(get_mongo),
) -> ReviewsService:
    return ReviewsService(jwt, mongo)
