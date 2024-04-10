from http import HTTPStatus

import pytest

pytestmark = [
    pytest.mark.asyncio(),
]


async def test_films_retrieve_404(make_get_request, faker):
    response = await make_get_request(
        "/api/v1/films/" + faker.uuid4(),
        expected_status=HTTPStatus.NOT_FOUND,
    )

    assert response == {"detail": "film not found"}


async def test_films_retrieve(make_get_request):
    response = await make_get_request(
        "/api/v1/films/3d825f60-9fff-4dfe-b294-1a45fa1e115d",
    )

    assert response == {
        "actors": [
            {
                "full_name": "Mark Hamill",
                "uuid": "26e83050-29ef-4163-a99d-b546cac208f8",
            },
            {
                "full_name": "Harrison Ford",
                "uuid": "5b4bf1bc-3397-4e83-9b17-8b10c6544ed1",
            },
            {
                "full_name": "Carrie Fisher",
                "uuid": "b5d2b63a-ed1f-4e46-8320-cf52a32be358",
            },
            {
                "full_name": "Peter Cushing",
                "uuid": "e039eedf-4daf-452a-bf92-a0085c68e156",
            },
        ],
        "description": "The Imperial Forces, under orders from cruel Darth Vader, "
        "hold Princess Leia hostage in their efforts to quell the "
        "rebellion against the Galactic Empire. Luke Skywalker and Han "
        "Solo, captain of the Millennium Falcon, work together with "
        "the companionable droid duo R2-D2 and C-3PO to rescue the "
        "beautiful princess, help the Rebel Alliance and restore "
        "freedom and justice to the Galaxy.",
        "directors": [
            {
                "full_name": "George Lucas",
                "uuid": "a5a8f573-3cee-4ccc-8a2b-91cb9f55250a",
            },
        ],
        "genre": [
            {
                "name": "Adventure",
                "uuid": "120a21cf-9097-479e-904a-13dd7198c1dd",
            },
            {"name": "Action", "uuid": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff"},
            {"name": "Sci-Fi", "uuid": "6c162475-c7ed-4461-9184-001ef3d9f26e"},
            {"name": "Fantasy", "uuid": "b92ef010-5e4c-4fd0-99d6-41b6456272cd"},
        ],
        "imdb_rating": 8.6,
        "title": "Star Wars: Episode IV - A New Hope",
        "uuid": "3d825f60-9fff-4dfe-b294-1a45fa1e115d",
        "writers": [
            {
                "full_name": "George Lucas",
                "uuid": "a5a8f573-3cee-4ccc-8a2b-91cb9f55250a",
            },
        ],
    }
