from http import HTTPStatus

import pytest

pytestmark = [
    pytest.mark.asyncio(),
]


async def test_genres_retrieve_404(make_get_request, faker):
    response = await make_get_request(
        "/api/v1/genres/" + faker.uuid4(),
        expected_status=HTTPStatus.NOT_FOUND,
    )

    assert response == {"detail": "genre not found"}


async def test_genres_retrieve(make_get_request):
    uuid = "120a21cf-9097-479e-904a-13dd7198c1dd"

    response = await make_get_request(
        f"/api/v1/genres/{uuid}",
    )

    assert response == {
        "uuid": uuid,
        "name": "Adventure",
    }
