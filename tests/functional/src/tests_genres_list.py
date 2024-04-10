from unittest.mock import ANY

import pytest

pytestmark = [
    pytest.mark.asyncio(),
]


async def test_genres_list(make_get_request):
    response = await make_get_request(
        "/api/v1/genres/",
        params={"page_size": 2},
    )

    assert response == [
        {
            "uuid": ANY,
            "name": ANY,
        },
        {
            "uuid": ANY,
            "name": ANY,
        },
    ]
