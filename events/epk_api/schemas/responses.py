from pydantic import BaseModel, Field


class NoticeCreationResponse(BaseModel):
    success: bool = Field(
        True,
        description="True - выполнено успешно, False - ошибка",
        examples=[True],
    )

    message: str | None = Field(
        default=None,
        description="Текст сообщения",
        examples=["Сообщение создано"],
    )


class HealthCheckResponse(BaseModel):
    """
    Статус работы
    """

    status: str
