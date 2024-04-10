from enum import Enum

import jinja2
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import List

from core.types import EmailType

jinja_env = jinja2.Environment()


class ChannelType(Enum):
    EMAIL = "email"
    PUSH = "push"


class LikeDislike(Enum):
    LIKE = 10
    DISLIKE = 1


class BaseMessage(BaseModel):
    """
    Базовый класс сообщений
    """

    notification_id: str | None = Field(
        None,
        description="Id сообщения (опционально)",
        examples=["c7b80121-06fb-4e75-b44e-32fb076e7be9"],
    )

    template_id: str | None = Field(
        None,
        description="Id шаблона",
        examples=["e083cf60-7698-493a-abd1-047fd401172d"],
    )

    subject: str = Field(
        default="",
        description="Тема письма",
        examples=["Ну наконец то!"],
    )

    text: str = Field(
        default="",
        description="Текст сообщения",
        examples=["Привет, тебе лайк!"],
    )


class HeadersModel(BaseModel):
    """
    Заголовки сообщений
    """

    headers: dict[str, str | None] | None = Field(
        None,
        description="Заголовок сообщения",
        examples=[{"X-Request-Id": "98bcee6d-3016-447b-9f6d-d6efcbdf056c"}],
    )


class ReviewLikeMessage(BaseMessage):
    """
    Сообщение о лайке
    """

    user_id: str = Field(
        description="Id пользователя",
        examples=["d091048f-87ba-4577-9387-82a4c3d6f6cd"],
    )

    review_id: str = Field(
        default=None,
        description="Id ревью",
        examples=["65f75b90463e3c418e6bec02"],
    )

    rating: LikeDislike = Field(
        default=LikeDislike.LIKE.value,
        description="10 - лайк, 1 - дизлайк",
        examples=[LikeDislike.LIKE.value],
    )

    model_config = ConfigDict(from_attributes=True)


class ReviewLikeModel(HeadersModel):
    """
    Модель сообщения о лайке с заголовками
    """

    message: ReviewLikeMessage


class WeeklyBookmarksMessage(BaseMessage):
    """
    Сообщение о закладках за неделю
    """

    model_config = ConfigDict(from_attributes=True)


class WeeklyBookmarksModel(HeadersModel):
    """
    Модель сообщения о закладках за неделю с заголовками
    """

    message: WeeklyBookmarksMessage


class GeneralNoticeMessage(BaseMessage):
    """
    Сообщение в свободном формате
    """

    user_id: str | None = Field(
        default=None,
        description="Id пользователя",
        examples=["d091048f-87ba-4577-9387-82a4c3d6f6cd"],
    )

    type: ChannelType = Field(
        default=ChannelType.EMAIL.value,
        description="Тип события нотификации (канал отправки)",
        examples=[ChannelType.EMAIL.value],
    )

    model_config = ConfigDict(from_attributes=True)


class GeneralNoticeModel(HeadersModel):
    """
    Модель сообщения в свободном формате с заголовками
    """

    message: GeneralNoticeMessage

    model_config = ConfigDict(from_attributes=True)


class NotificationBaseModel(BaseModel):
    """
    Базовая модель сообщений для сервиса нотификаций
    """

    notification_id: str = Field(
        "",
        description="Id сообщения (опционально)",
        examples=["c7b80121-06fb-4e75-b44e-32fb076e7be9"],
    )

    subject: str = Field(
        default="",
        description="Тема письма",
        examples=["Ну наконец то!"],
    )

    body: str = Field(
        default="",
        description="Текст сообщения",
        examples=["Привет, не ожидал получить о нас сообщение?"],
    )

    model_config = ConfigDict(from_attributes=True)


class PushNotificationModel(NotificationBaseModel):
    """
    Модель PUSH сообщений для сервиса нотификаций
    """

    to: List[str] = Field(
        description="Id пользователя получателя сообщения",
        examples=[["c55aa02c-544d-4681-8f93-0850ac32fd9e"]],
    )


class EmailNotificationModel(NotificationBaseModel):
    """
    Модель Email сообщений для сервиса нотификаций
    """

    to: List[EmailType] = Field(
        description="Email получателя сообщения",
        examples=[["user@yandex.ru"]],
    )
