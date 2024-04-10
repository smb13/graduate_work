import datetime
import uuid
from functools import lru_cache
from http import HTTPStatus

import bson
from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, HTTPException
from motor.core import AgnosticClient
from pymongo.errors import DuplicateKeyError

from core.config import settings
from db.mongo import get_mongo
from schemas.notifications import EmailNotification, PushNotification, PushNotificationsListResponse
from services.base import BaseService


class NotificationsService(BaseService):
    """
    Класс для реализации логики работы с закладками.
    """

    async def send_email_notification(self, request: EmailNotification) -> None:
        try:
            await self.db().insert_one(
                {
                    "id": bson.Binary.from_uuid(request.id),
                    "type": "email",
                    "subject": request.subject,
                    "to": request.to,
                    "body": request.body,
                    "updated_at": None,
                    "delivered_at": None,
                    "ts": datetime.datetime.utcnow(),
                },
            )
        except DuplicateKeyError:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Уведомление с таким идентификатором уже существует",
            )

    async def send_push_notification(self, request: PushNotification) -> None:
        try:
            await self.db().insert_one(
                {
                    "id": bson.Binary.from_uuid(request.id),
                    "type": "push",
                    "subject": request.subject,
                    "to": request.to,
                    "body": request.body,
                    "read": False,
                    "updated_at": None,
                    "delivered_at": None,
                    "ts": datetime.datetime.utcnow(),
                },
            )
        except DuplicateKeyError:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Уведомление с таким идентификатором уже существует",
            )

    async def mark_notification_as_read(self, notification_id: uuid.UUID) -> None:
        await self.db().update_one(
            {
                "id": bson.Binary.from_uuid(notification_id),
            },
            {"$set": {"read": True}},
            upsert=True,
        )

    async def get_notifications_history(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = settings.page_size,
    ) -> PushNotificationsListResponse:
        return PushNotificationsListResponse(
            **await self.db()
            .aggregate(
                list(
                    filter(
                        None,
                        [
                            {
                                "$match": {
                                    "to": user_id,
                                    "type": "push",
                                    "delivered_at": {
                                        "$gt": datetime.datetime.utcnow()
                                        - datetime.timedelta(seconds=settings.show_timeout),
                                    },
                                },
                            },
                            {"$project": {"_id": 0}},
                            {"$sort": {"delivered_at": -1}},
                            {
                                "$facet": {
                                    "notifications": [
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
                            {"$project": {"notifications": 1, "total": {"$arrayElemAt": ["$total.total", 0]}}},
                        ],
                    ),
                ),
            )
            .next(),
        )


@lru_cache
def get_notifications_service(
    jwt: AuthJWT = Depends(),
    mongo: AgnosticClient = Depends(get_mongo),
) -> NotificationsService:
    return NotificationsService(jwt, mongo)
