from unittest.mock import ANY

import pytest

pytestmark = [
    pytest.mark.asyncio(),
]


async def test_films_list(make_get_request):
    response = await make_get_request(
        "/api/v1/films/",
        params={"page_size": 2},
    )

    assert response == [
        {
            "uuid": ANY,
            "title": ANY,
            "imdb_rating": ANY,
        },
        {
            "uuid": ANY,
            "title": ANY,
            "imdb_rating": ANY,
        },
    ]


async def test_filter_by_genre(make_get_request):
    response = await make_get_request(
        "/api/v1/films",
        params={"genre": "f24fd632-b1a5-4273-a835-0119bd12f829"},  # find News
    )

    assert len(response) == 5
