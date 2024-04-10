import uuid
from http import HTTPStatus

import pytest

pytestmark = [
    pytest.mark.asyncio(),
]


async def test_email(make_get_request, make_post_request, make_delete_request):
    email_id = uuid.uuid4()
    to = str(uuid.uuid4()) + "@test.com"

    assert (
        await make_post_request(
            "/api/v1/notifications/email",
            {
                "id": str(email_id),
                "subject": "Очень важная нотификация",
                "to": to,
                "body": "string",
            },
            expected_status=HTTPStatus.CREATED,
            service="notifications",
        )
        is None
    )

    assert await make_get_request("/api/v1/tasks/email", service="notifications") == [
        {
            "body": "string",
            "id": str(email_id),
            "subject": "Очень важная нотификация",
            "to": to,
        },
    ]

    assert (
        await make_post_request(
            "/api/v1/tasks/confirm",
            [str(email_id)],
            service="notifications",
        )
        is None
    )


async def test_push(make_get_request, make_post_request, make_delete_request):
    push_id = uuid.uuid4()
    to = str(uuid.uuid4()) + "@test.com"

    assert (
        await make_post_request(
            "/api/v1/notifications/push",
            {
                "id": str(push_id),
                "subject": "Очень важная нотификация",
                "to": to,
                "body": "string",
            },
            expected_status=HTTPStatus.CREATED,
            service="notifications",
        )
        is None
    )

    assert await make_get_request("/api/v1/tasks/push", {"clients": to}, service="notifications") == [
        {
            "body": "string",
            "id": str(push_id),
            "subject": "Очень важная нотификация",
            "to": to,
        },
    ]

    assert await make_get_request(
        f"/api/v1/notifications/push/{to}",
        {"user_id": str(push_id)},
        service="notifications",
    ) == {"total": 0, "notifications": []}

    assert (
        await make_post_request(
            "/api/v1/tasks/confirm",
            [str(push_id)],
            service="notifications",
        )
        is None
    )

    assert await make_get_request(
        f"/api/v1/notifications/push/{to}",
        {"user_id": str(push_id)},
        service="notifications",
    ) == {
        "total": 1,
        "notifications": [
            {
                "id": str(push_id),
                "subject": "Очень важная нотификация",
                "to": to,
                "body": "string",
                "read": False,
            },
        ],
    }

    assert (
        await make_post_request(
            f"/api/v1/notifications/push/{str(push_id)}",
            service="notifications",
        )
        is None
    )

    assert await make_get_request(f"/api/v1/notifications/push/{to}", service="notifications") == {
        "total": 1,
        "notifications": [
            {
                "id": str(push_id),
                "subject": "Очень важная нотификация",
                "to": to,
                "body": "string",
                "read": True,
            },
        ],
    }
