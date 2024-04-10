from enum import Enum

from pydantic import BaseModel, Field


class ReviewSortKeys(str, Enum):
    average_asc = "rating"
    avergae_desc = "-rating"
    likes_asc = "likes"
    likes_desc = "-likes"
    dislikes_asc = "dislikes"
    dislikes_desc = "-dislikes"


class ReviewRequest(BaseModel):
    review: str = Field(description="Текст рецензии на фильм", examples=["Этот фильм просто отвратительный!"])


class ReviewResponse(ReviewRequest):
    """Количество лайков у рецензии"""

    review_id: str | None = Field(default=None, description="Идентификатор отзыва", example="65f75b90463e3c418e6bec02")
    likes: int | None = Field(0, description="Количества лайков у фильма", example=1)
    dislikes: int | None = Field(0, description="Количества дизлайков у фильма", example=123)
    average: float | None = Field(0, description="Средняя пользовательская оценка фильма", example=2.3)


class ReviewListResponse(BaseModel):
    """Список отзывов"""

    total: int = Field(default=0, description="Общее число найденных отзывов", example=17)
    reviews: list[ReviewResponse] = Field(description="Список отзывов")
