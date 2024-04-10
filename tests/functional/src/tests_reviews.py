from http import HTTPStatus

import pytest

pytestmark = [
    pytest.mark.asyncio(),
]


async def test_ratings(make_get_request, make_post_request, make_delete_request):
    movie_id = "0dbfdff6-1bd9-49be-b9b0-27f4d4503904"
    review = "Этот фильм просто отвратительный!"

    assert (
        await make_delete_request(
            f"/api/v1/reviews/{movie_id}/",
            service="ratings",
        )
        is None
    )

    assert (
        await make_post_request(
            f"/api/v1/reviews/{movie_id}",
            params={"review": review},
            expected_status=HTTPStatus.CREATED,
            service="ratings",
        )
        is None
    )

    response = await make_get_request(
        f"/api/v1/reviews/{movie_id}",
        service="ratings",
    )
    review_id = response["review_id"]
    assert response == {"review": review, "review_id": review_id, "likes": 0, "dislikes": 0, "average": 0}

    assert (
        await make_post_request(
            f"/api/v1/reviews/{movie_id}/{review_id}/like",
            service="ratings",
        )
        is None
    )

    assert await make_get_request(
        f"/api/v1/reviews/{movie_id}",
        service="ratings",
    ) == {"review": review, "review_id": review_id, "likes": 1, "dislikes": 0, "average": 10}

    assert (
        await make_post_request(
            f"/api/v1/reviews/{movie_id}/{review_id}/dislike",
            service="ratings",
        )
        is None
    )

    assert await make_get_request(
        f"/api/v1/reviews/{movie_id}",
        service="ratings",
    ) == {"review": review, "review_id": review_id, "likes": 0, "dislikes": 1, "average": 1}

    assert await make_get_request(
        f"/api/v1/reviews/{movie_id}/list",
        service="ratings",
    ) == {
        "total": 1,
        "reviews": [
            {
                "review": review,
                "review_id": review_id,
                "likes": 0,
                "dislikes": 1,
                "average": 1,
            },
        ],
    }

    assert (
        await make_delete_request(
            f"/api/v1/reviews/{movie_id}/{review_id}/",
            service="ratings",
        )
        is None
    )

    assert await make_get_request(
        f"/api/v1/reviews/{movie_id}/list",
        service="ratings",
    ) == {
        "total": 1,
        "reviews": [
            {
                "review": review,
                "review_id": review_id,
                "likes": 0,
                "dislikes": 0,
                "average": 0,
            },
        ],
    }

    assert (
        await make_post_request(
            f"/api/v1/reviews/{movie_id}/{review_id}/like",
            service="ratings",
        )
        is None
    )

    assert await make_get_request(
        f"/api/v1/reviews/{movie_id}/list",
        service="ratings",
    ) == {
        "total": 1,
        "reviews": [
            {
                "review": review,
                "review_id": review_id,
                "likes": 1,
                "dislikes": 0,
                "average": 10,
            },
        ],
    }

    assert (
        await make_delete_request(
            f"/api/v1/reviews/{movie_id}",
            service="ratings",
        )
        is None
    )

    assert await make_get_request(
        f"/api/v1/reviews/{movie_id}/list",
        service="ratings",
    ) == {"total": 0, "reviews": []}
