from http import HTTPStatus

import pytest

pytestmark = [
    pytest.mark.asyncio(),
]


async def test_bookmarks(make_get_request, make_post_request, make_delete_request):
    movie_id = "0dbfdff6-1bd9-49be-b9b0-27f4d4503904"

    assert (
        await make_delete_request(
            f"/api/v1/bookmarks/{movie_id}/",
            service="ratings",
        )
        is None
    )

    assert (
        await make_post_request(
            f"/api/v1/bookmarks/{movie_id}",
            expected_status=HTTPStatus.CREATED,
            service="ratings",
        )
        is None
    )

    assert await make_get_request(
        "/api/v1/bookmarks/",
        service="ratings",
    ) == {"total": 1, "bookmarks": [movie_id]}

    assert (
        await make_delete_request(
            f"/api/v1/bookmarks/{movie_id}/",
            service="ratings",
        )
        is None
    )

    assert await make_get_request(
        "/api/v1/bookmarks/",
        service="ratings",
    ) == {"total": 0, "bookmarks": []}
