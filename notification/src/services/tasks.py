import datetime
import uuid
from functools import lru_cache

import bson
from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from motor.core import AgnosticClient

from core.config import settings
from db.mongo import get_mongo
from schemas.notifications import EmailNotification, PushNotification
from services.base import BaseService


class TasksService(BaseService):
    """
    Класс для реализации логики работы с задачами.
    """

    async def get_push_tasks(self, clients: list[str]) -> list[PushNotification]:
        mark = uuid.uuid4()
        result = await self.db().update_many(
            {
                "type": "push",
                "$or": [
                    {"updated_at": None},
                    {
                        "updated_at": {
                            "$lt": datetime.datetime.utcnow() - datetime.timedelta(seconds=settings.send_timeout),
                        },
                    },
                ],
                "delivered_at": None,
                "to": {"$in": clients},
            },
            {"$set": {"updated_at": datetime.datetime.utcnow(), "mark": str(mark)}},
        )
        if result.modified_count == 0:
            return []
        return [
            PushNotification(**task)
            for task in await self.db().find({"mark": str(mark)}).to_list(result.modified_count)
        ]

    async def get_email_task(self) -> list[EmailNotification]:
        mark = uuid.uuid4()
        result = await self.db().update_one(
            {
                "type": "email",
                "$or": [
                    {"updated_at": None},
                    {
                        "updated_at": {
                            "$lt": datetime.datetime.utcnow() - datetime.timedelta(seconds=settings.send_timeout),
                        },
                    },
                ],
                "delivered_at": None,
            },
            {"$set": {"updated_at": datetime.datetime.utcnow(), "mark": str(mark)}},
        )
        if result.modified_count == 0:
            return []
        return [
            EmailNotification(**task)
            for task in await self.db().find({"mark": str(mark)}).to_list(result.modified_count)
        ]

    async def confirm(self, notifications: list[uuid.UUID]) -> None:
        await self.db().update_many(
            {"id": {"$in": [bson.Binary.from_uuid(notification_id) for notification_id in notifications]}},
            {"$set": {"delivered_at": datetime.datetime.utcnow()}},
            upsert=True,
        )


@lru_cache
def get_tasks_service(
    jwt: AuthJWT = Depends(),
    mongo: AgnosticClient = Depends(get_mongo),
) -> TasksService:
    return TasksService(jwt, mongo)
