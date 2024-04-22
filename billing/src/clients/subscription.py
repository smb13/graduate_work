from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from authlib.integrations import httpx_client


client: "httpx_client.AsyncOAuth2Client | None" = None


async def get_client() -> "httpx_client.AsyncOAuth2Client":
    if not client:
        raise RuntimeError("Subscriptions Client is not initialized")

    return client
