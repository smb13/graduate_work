from http import HTTPStatus

import pytest

pytestmark = [
    pytest.mark.asyncio(),
]


async def test_persons_retrieve_404(make_get_request, faker):
    response = await make_get_request(
        "/api/v1/persons/" + faker.uuid4(),
        expected_status=HTTPStatus.NOT_FOUND,
    )

    assert response == {"detail": "person not found"}


async def test_persons_retrieve(make_get_request):
    uuid = "df199312-275e-4d1e-83cb-8f96bc5d64fb"

    response = await make_get_request(
        f"/api/v1/persons/{uuid}",
    )

    assert response == {
        "uuid": uuid,
        "full_name": "Rita",
        "films": [
            {
                "uuid": "b56e8825-7551-4117-b05b-0b7b0bd4829b",
                "roles": ["actor"],
            },
        ],
    }
