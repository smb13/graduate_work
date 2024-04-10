# Используем pydantic для упрощения работы при перегонке данных из json в объекты
from pydantic import BaseModel, ConfigDict, Field

from models.genre import Genre


class FilmPerson(BaseModel):
    id: str = Field(..., alias="uuid")
    name: str = Field(..., alias="full_name")

    model_config = ConfigDict(populate_by_name=True)


class Film(BaseModel):
    id: str = Field(..., alias="uuid")
    title: str
    imdb_rating: float
    description: str | None = None
    genre: list[Genre]
    directors: list[FilmPerson] | None = None
    actors: list[FilmPerson] | None = None
    writers: list[FilmPerson] | None = None
    directors_names: list[str] | None = None
    actors_names: list[str] | None = None
    writers_names: list[str] | None = None

    model_config = ConfigDict(populate_by_name=True)
