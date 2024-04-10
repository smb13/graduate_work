from uuid import UUID

from pydantic import BaseModel, Field


class BookmarksListResponse(BaseModel):
    """Список закладок"""

    total: int = Field(default=0, description="Общее число найденных закладок", example=17)
    bookmarks: list[UUID] = Field(description="Список закладок")
