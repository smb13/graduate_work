from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ChannelType(Enum):
    EMAIL = "email"
    PUSH = "push"


class LikeDislike(Enum):
    LIKE = 10
    DISLIKE = 1


class BaseRequest(BaseModel):
    """
    Базовый класс риквестов
    """

    notification_id: str | None = Field(
        None,
        description="Id сообщения (опционально)",
        examples=["c7b80121-06fb-4e75-b44e-32fb076e7be9"],
    )

    template_id: str | None = Field(
        None,
        description="Id шаблона (опционально)",
        examples=["e083cf60-7698-493a-abd1-047fd401172d"],
    )

    subject: str = Field(
        default="",
        description="Тема письма",
        examples=["Ну наконец то!"],
    )


class ReviewLikeRequest(BaseRequest):
    """
    Отправить нотификацию о лайке запрос
    """

    user_id: str = Field(
        description="Id пользователя",
        examples=["d091048f-87ba-4577-9387-82a4c3d6f6cd"],
    )

    text: str = Field(
        default="",
        description="Текст сообщения",
        examples=["Привет, тебе лайк!"],
    )

    review_id: str = Field(
        default="",
        description="Id ревью",
        examples=["65f75b90463e3c418e6bec02"],
    )

    rating: LikeDislike = Field(
        default=LikeDislike.LIKE.value,
        description="10 - лайк, 1 - дизлайк",
        examples=[LikeDislike.LIKE.value],
    )

    model_config = ConfigDict(from_attributes=True)


class WeeklyBookmarksRequest(BaseRequest):
    """
    Отправить нотификацию о закладках за неделю
    """

    text: str = Field(
        default="",
        description="Текст сообщения",
        examples=["Привет, вот твои закладки за неделю!"],
    )

    model_config = ConfigDict(from_attributes=True)


class GeneralNoticeRequest(BaseRequest):
    """
    Отправить пользователю(ям) сообщение
    """

    user_id: str | None = Field(
        default=None,
        description="Id пользователя",
        examples=["d091048f-87ba-4577-9387-82a4c3d6f6cd"],
    )

    text: str = Field(
        default="",
        description="Текст сообщения",
        examples=["Привет, вот твои закладки за неделю!"],
    )

    type: ChannelType = Field(
        default=ChannelType.EMAIL.value,
        description="Тип события нотификации (канал отправки)",
        examples=[ChannelType.EMAIL.value],
    )

    model_config = ConfigDict(from_attributes=True)


class HealthCheckResponse(BaseModel):
    """
    Статус работы
    """

    status: str
