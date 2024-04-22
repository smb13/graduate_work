from pydantic import BaseModel, Field


class ResponseBase(BaseModel):
    """Базовая схема для сообщения от сервиса."""

    detail: str | dict | list = Field(description="Сообщение от сервиса")
