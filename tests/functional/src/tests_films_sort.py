from http import HTTPStatus

import pytest

pytestmark = [
    pytest.mark.asyncio(),
]


@pytest.mark.parametrize(
    argnames=("sort_param", "reverse"),
    argvalues=[
        ("imdb_rating", False),
        ("-imdb_rating", True),
    ],
)
async def test_sort_imdb_rating(make_get_request, sort_param, reverse):
    response = await make_get_request(
        "/api/v1/films/",
        params={"sort": sort_param},
    )

    ratings = [film["imdb_rating"] for film in response]

    assert ratings == sorted(ratings, reverse=reverse)
    assert ratings != sorted(ratings, reverse=not reverse)


async def test_no_sort(make_get_request):
    response = await make_get_request("/api/v1/films/")

    ratings = [film["imdb_rating"] for film in response]

    assert ratings != sorted(ratings, reverse=True)
    assert ratings != sorted(ratings, reverse=False)


@pytest.mark.parametrize(
    argnames="invalid_sort",
    argvalues=["", "id"],
    ids=("empty", "not_existent"),
)
async def test_sort_validation(make_get_request, invalid_sort):
    response = await make_get_request(
        "/api/v1/films/",
        params={"sort": invalid_sort},
        expected_status=HTTPStatus.UNPROCESSABLE_ENTITY,
    )

    assert response.get("detail", [{}])[0].get("msg") == "Input should be 'imdb_rating' or '-imdb_rating'"
