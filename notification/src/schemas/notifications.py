import uuid
from uuid import UUID

from pydantic import BaseModel, Field


class EmailNotification(BaseModel):
    """Уведомление по электронной почте"""

    id: UUID = Field(default=..., description="Идентификатор уведомления", examples=[uuid.uuid4()])
    subject: str = Field(default=..., description="Заголовок письма", examples=["Очень важная нотификация"])
    to: str | list[str] = Field(
        ...,
        description="Реципиент или список реципиентов",
        examples=[["test@test.com", "vasya@test.com"], "test@test.com"],
    )
    body: str = Field(..., description="Текст уведомления")


class PushNotification(BaseModel):
    """Push уведомление"""

    id: UUID = Field(default=..., description="Идентификатор уведомления", examples=[uuid.uuid4()])
    subject: str = Field(default=..., description="Заголовок уведомления", examples=["Очень важная нотификация"])
    to: str = Field(
        ...,
        description="Идентификатор клиента или список иденитификаторов клиентов",
        examples=["test@test.com"],
    )
    body: str = Field(..., description="Текст уведомления")


class PushNotificationState(PushNotification):
    """Push уведомление"""

    read: bool = Field(default=..., description="Признак прочитанного уведомления", examples=[True, False])


class PushNotificationsListResponse(BaseModel):
    """Список закладок"""

    total: int = Field(default=0, description="Общее число найденных уведомлений", example=17)
    notifications: list[PushNotificationState] = Field(description="Список уведомлений")
