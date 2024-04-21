import uuid
from uuid import UUID

from pydantic import BaseModel, Field


class EmailNotification(BaseModel):
    """Запрашиваемое уведомление для отправки."""

    is_priority: bool = Field(default=False, description="Признак приоритетной отправки")
    retries: int = Field(default=0, description="Попытка отправки email")
    user_timezone: str = Field(default="Europe/Moscow")
    message_id: UUID = Field(default=..., description="Идентификатор уведомления", examples=[uuid.uuid4()])
    message_subject: str = Field(default=..., description="Заголовок письма", examples=["Очень важная нотификация"])
    message_to_email: str | list[str] = Field(
        ...,
        description="Email пользователя или список email`ов",
        examples=[["test@test.com", "vasya@test.com"], "test@test.com"],
    )
    message_body: str = Field(..., description="Текст уведомления")
