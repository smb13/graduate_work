from pydantic import BaseModel, ConfigDict, Field


class PersonFilm(BaseModel):
    id: str = Field(..., alias="uuid")
    role: str

    model_config = ConfigDict(populate_by_name=True)


class Person(BaseModel):
    id: str = Field(..., alias="uuid")
    name: str = Field(..., alias="full_name")
    films: list[PersonFilm] | None = None

    model_config = ConfigDict(populate_by_name=True)
