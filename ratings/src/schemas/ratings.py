from pydantic import BaseModel, ConfigDict, Field


class RatingsResponse(BaseModel):
    """Данные рейтинга фильма"""

    """Количества лайков у фильма"""
    likes: int | None = Field(
        0,
        description="Количества лайков у фильма",
        example=1,
    )
    """Количества дизлайков у фильма"""
    dislikes: int | None = Field(
        0,
        description="Количества дизлайков у фильма",
        example=123,
    )
    """Средняя пользовательская оценка фильма"""
    average: float | None = Field(
        0,
        description="Средняя пользовательская оценка фильма",
        example=2.3,
    )
    """Оценка фильма текущим пользователем"""
    rating: int | None = Field(
        None,
        description="Оценка фильма текущим пользователем",
        example=2.3,
    )

    total: int | None = Field(
        0,
        description="Число оценок фильма",
    )

    model_config = ConfigDict(from_attributes=True)
