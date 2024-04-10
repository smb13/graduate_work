from functools import lru_cache
from http import HTTPStatus

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, HTTPException
from pika.exceptions import AMQPError

from db.rabbitmq import Actions, RmqPublisher, get_publishers
from schemas.requests import ChannelType, GeneralNoticeRequest, ReviewLikeRequest, WeeklyBookmarksRequest
from schemas.responses import NoticeCreationResponse


class NoticeService:
    """
    NoticeService содержит бизнес-логику по работе с событиями нотификации.
    """

    def __init__(self, publisher: RmqPublisher, jwt: AuthJWT) -> None:
        self.publisher = publisher
        self.jwt = jwt

    async def create_review_like(self, request: ReviewLikeRequest, x_request_id: str | None) -> NoticeCreationResponse:
        routing_key = ChannelType.PUSH.value + "." + Actions.REVIEW_LIKE.value
        message = request.model_dump_json()
        return await self.publish_message(routing_key=routing_key, message=message, x_request_id=x_request_id)

    async def create_weekly_bookmarks(
        self,
        request: WeeklyBookmarksRequest,
        x_request_id: str | None,
    ) -> NoticeCreationResponse:
        routing_key = ChannelType.EMAIL.value + "." + Actions.WEEKLY_BOOKMARKS.value
        message = request.model_dump_json()
        return await self.publish_message(routing_key=routing_key, message=message, x_request_id=x_request_id)

    async def create_create_general_notice(
        self,
        request: GeneralNoticeRequest,
        x_request_id: str | None,
    ) -> NoticeCreationResponse:
        channel_type = request.type.value
        routing_key = channel_type + "." + Actions.GENERAL_NOTICE.value
        message = request.model_dump_json()
        return await self.publish_message(routing_key=routing_key, message=message, x_request_id=x_request_id)

    async def publish_message(self, routing_key: str, message: str, x_request_id: str) -> NoticeCreationResponse:
        try:
            self.publisher.publish(routing_key=routing_key, message=message, x_request_id=x_request_id)
        except AMQPError as e:
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=f"Ошибка отправки в RabbitMQ: {e}",
            )
        return NoticeCreationResponse(success=True, message="Сообщение создано")


@lru_cache
def get_notice_service(
    publisher: RmqPublisher = Depends(get_publishers),
    jwt: AuthJWT = Depends(),
) -> NoticeService:
    return NoticeService(publisher, jwt)
