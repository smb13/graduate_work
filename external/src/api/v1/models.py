from enum import Enum

from pydantic import BaseModel
from pydantic.types import UUID4


class GenreExternal(BaseModel):
    uuid: UUID4
    name: str


class FilmPersonExternal(BaseModel):
    uuid: UUID4
    full_name: str


class FilmShortExternal(BaseModel):
    uuid: UUID4
    title: str
    imdb_rating: float


class FilmDetailExternal(FilmShortExternal):
    description: str | None
    genre: list[GenreExternal]
    actors: list[FilmPersonExternal] | None
    writers: list[FilmPersonExternal] | None
    directors: list[FilmPersonExternal] | None


class PersonFilmExternal(BaseModel):
    uuid: UUID4
    roles: list[str]


class PersonDetailExternal(FilmPersonExternal):
    films: list[PersonFilmExternal] | None


class FilmsSortKeys(str, Enum):
    imdb_rating_asc = "imdb_rating"
    imdb_rating_desc = "-imdb_rating"
