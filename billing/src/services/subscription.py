from typing import TYPE_CHECKING
from urllib.parse import urljoin

import backoff
import httpx
from authlib.integrations.base_client import OAuthError
from clients.subscription import get_client
from fastapi import Depends
from httpx import Response

from core.config import settings
from services.base import ServiceError

if TYPE_CHECKING:
    from authlib.integrations import httpx_client


class SubscriptionService:
    def __init__(
        self,
        client: "httpx_client.AsyncOAuth2Client",
    ) -> None:
        self.client = client

    _auth_path = "/api/v1/auth/token"

    @property
    def _auth_url(self) -> str:
        return urljoin(settings.auth_service_base_url, self._auth_path)

    async def _authenticate(self) -> None:
        """Для отладки.
        TODO: На проде надо заменить auth сервис на"""
        await self.client.fetch_token(
            url=self._auth_url,
            username=settings.local_user_email,
            password=settings.local_user_password,
        )

    @backoff.on_exception(
        backoff.expo,
        exception=(httpx.HTTPStatusError, OAuthError),
        base=2,
        max_tries=5,
    )
    async def _send_request(self, method: str, url: str, **kwargs) -> "httpx.Response":
        try:
            response: Response = await self.client.request(method=method, url=url, **kwargs)
        except OAuthError:
            await self._authenticate()
            response = await self.client.request(method=method, url=url, **kwargs)
        response.raise_for_status()
        return response

    async def activate_subscription(self, subscription_id: str, **kwargs) -> None:
        try:
            await self._send_request(
                method="POST",
                url=urljoin(
                    settings.subscription_service_base_url,
                    f"/api/v1/user_subscriptions/{subscription_id}/activate",
                ),
                json=kwargs,
            )
        except (httpx.HTTPStatusError, OAuthError, RuntimeError, httpx.ConnectError) as exc:
            raise ServiceError(f"Subscription activation failed: {exc}") from exc

    async def cancel_subscription(self, subscription_id: str) -> None:
        try:
            await self._send_request(
                "POST",
                urljoin(
                    settings.subscription_service_base_url,
                    f"/api/v1/user_subscriptions/{subscription_id}/cancel",
                ),
            )
        except (httpx.HTTPStatusError, OAuthError, RuntimeError, httpx.ConnectError) as exc:
            raise ServiceError(f"Subscription cancellation failed: {exc}") from exc


def get_subscription_service(
    client: "httpx.AsyncClient" = Depends(get_client),
) -> SubscriptionService:
    return SubscriptionService(client=client)
