from http import HTTPStatus

import pytest

from settings import test_settings

pytestmark = [
    pytest.mark.asyncio(),
]


@pytest.mark.parametrize(
    argnames="page_size",
    argvalues=[
        None,
        1,
        test_settings.page_size_max // 2,
        test_settings.page_size_max,
    ],
)
async def test_page_size(make_get_request, page_size):
    query_data = {"page_size": page_size} if page_size else {}

    response = await make_get_request(
        "/api/v1/films/",
        params=query_data,
    )

    assert len(response) == page_size if page_size is not None else test_settings.page_size


@pytest.mark.parametrize(
    argnames=("page_size", "error_type"),
    argvalues=[
        ("", "int_parsing"),
        (-1, "greater_than_equal"),
        (0, "greater_than_equal"),
        (1.1, "int_parsing"),
        (test_settings.page_size_max + 1, "less_than_equal"),
    ],
)
async def test_page_size_validation(make_get_request, page_size, error_type):
    query_data = {"page_size": page_size}

    response = await make_get_request(
        "/api/v1/films/",
        params=query_data,
        expected_status=HTTPStatus.UNPROCESSABLE_ENTITY,
    )

    assert response.get("detail", [{}])[0].get("type") == error_type


async def test_page_number(make_get_request):
    url = "/api/v1/films/"
    query_data = {"page_size": 1}

    response_1 = await make_get_request(url, params=query_data | {"page_number": 1})
    response_2 = await make_get_request(url, params=query_data | {"page_number": 2})

    assert response_1[0].get("uuid") != response_2[0].get("uuid")
