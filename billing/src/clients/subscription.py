from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import httpx


client: "httpx.AsyncClient | None" = None


async def get_client() -> "httpx.AsyncClient":
    if not client:
        raise RuntimeError("Subscriptions Client is not initialized")

    return client
