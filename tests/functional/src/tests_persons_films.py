import uuid

import pytest

pytestmark = [
    pytest.mark.asyncio(),
]


async def test_missing_person(make_get_request):
    response = await make_get_request(
        f"/api/v1/persons/{uuid.uuid4()}/film",
    )

    assert response == []


async def test_existent_person(make_get_request):
    response = await make_get_request(
        "/api/v1/persons/df199312-275e-4d1e-83cb-8f96bc5d64fb/film",
    )

    assert response == [
        {
            "uuid": "b56e8825-7551-4117-b05b-0b7b0bd4829b",
            "title": "Rising Star",
            "imdb_rating": 4.2,
        },
    ]
