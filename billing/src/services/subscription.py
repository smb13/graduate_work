from typing import TYPE_CHECKING

from clients.subscription import get_client
from fastapi import Depends

if TYPE_CHECKING:
    import httpx


class SubscriptionService:
    def __init__(
        self,
        client: "httpx.AsyncClient",
    ) -> None:
        self.client = client

    async def activate_subscription(self, subscription_id: str) -> None:
        await self.client.patch(f"/subscriptions/{subscription_id}/activate")

    async def cancel_subscription(self, subscription_id: str) -> None:
        await self.client.patch(f"/subscriptions/{subscription_id}/cancel")


def get_subscription_service(
    client: "httpx.AsyncClient" = Depends(get_client),
) -> SubscriptionService:
    return SubscriptionService(client=client)
