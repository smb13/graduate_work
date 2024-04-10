from typing import TYPE_CHECKING

import pytest

from models.film import Film as ModelsFilm, FilmPerson as ModelsFilmPerson
from services.films import get_films_service

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_404(mock_service, client: "TestClient", faker):
    mock_service(get_films_service, "get_data", None)

    response = client.get("http://testserver/api/v1/films/" + faker.uuid4())

    assert response.status_code == 404
    assert response.json() == {"detail": "film not found"}


def test_films_retrieve(faker, mock_service, client: "TestClient", genre):
    actor, director, writer = (ModelsFilmPerson(uuid=faker.uuid4(), full_name=faker.name()) for _ in range(3))
    film = ModelsFilm(
        id=faker.uuid4(),
        title=faker.sentence(),
        imdb_rating=faker.pyfloat(1, 1, True),
        description=faker.text(),
        genre=[genre],
        actors=[actor],
        directors=[director],
        writers=[writer],
    )
    mock_service(get_films_service, "get_data", film)

    response = client.get(f"http://testserver/api/v1/films/{film.id}")

    assert response.status_code == 200
    assert response.json() == {
        "uuid": film.id,
        "title": film.title,
        "imdb_rating": film.imdb_rating,
        "description": film.description,
        "genre": [{"uuid": genre.id, "name": genre.name}],
        "actors": [{"uuid": actor.id, "full_name": actor.name}],
        "directors": [{"uuid": director.id, "full_name": director.name}],
        "writers": [{"uuid": writer.id, "full_name": writer.name}],
    }


@pytest.mark.parametrize(
    argnames="path",
    argvalues=["/api/v1/films", "/api/v1/films/search?query=star"],
)
def test_films_list(faker, mock_service, client: "TestClient", genre, path):
    films = [
        ModelsFilm(
            id=faker.uuid4(),
            title=faker.sentence(),
            imdb_rating=faker.pyfloat(1, 1, True),
            genre=[genre],
        )
        for _ in range(3)
    ]
    mock_service(get_films_service, "get_data", films)

    response = client.get("http://testserver" + path)

    assert response.status_code == 200
    assert response.json() == [
        {
            "uuid": film.id,
            "title": film.title,
            "imdb_rating": film.imdb_rating,
        }
        for film in films
    ]
