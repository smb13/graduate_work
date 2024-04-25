from functools import lru_cache
from typing import TYPE_CHECKING
from urllib.parse import urljoin

import backoff
import httpx
from authlib.integrations.base_client import OAuthError
from fastapi import Depends

from core.config import auth_settings, billing_settings, settings
from db.http import get_client

if TYPE_CHECKING:
    from authlib.integrations import httpx_client


class BillingService:
    def __init__(
        self,
        client: "httpx_client.AsyncOAuth2Client",
    ) -> None:
        self.client = client

    _auth_path = "/api/v1/auth/token"

    @property
    def _auth_url(self) -> str:
        return urljoin(auth_settings.service_base_url, self._auth_path)

    async def _authenticate(self) -> None:
        await self.client.fetch_token(
            url=self._auth_url,
            username=settings.local_user_email,
            password=settings.local_user_password,
        )

    @backoff.on_exception(
        backoff.expo,
        exception=(httpx.HTTPStatusError, OAuthError),
        max_tries=billing_settings.backoff_max_tries,
    )
    async def _send_request(self, method: str, url: str, **kwargs) -> "httpx.Response":
        try:
            response = await self.client.request(method=method, url=url, **kwargs)
        except OAuthError:
            await self._authenticate()
            response = await self.client.request(method=method, url=url, **kwargs)
        response.raise_for_status()
        return response.json()

    async def payments_new(self, **kwargs) -> str:
        response = await self._send_request(
            method="POST",
            url=urljoin(billing_settings.service_base_url, billing_settings.new_uri),
            json=kwargs,
        )
        return response.get("confirmation_url")

    async def payments_cancel(self, **kwargs) -> str:
        response = await self._send_request(
            method="POST",
            url=urljoin(billing_settings.service_base_url, billing_settings.refund_uri),
            json=kwargs,
        )
        return response.text

    async def payments_renew(self, **kwargs) -> str:
        response = await self._send_request(
            method="POST",
            url=urljoin(billing_settings.service_base_url, billing_settings.renew_uri),
            json=kwargs,
        )
        return response.text


@lru_cache
def get_billing_service(
    client: "httpx.AsyncClient" = Depends(get_client),
) -> BillingService:
    return BillingService(client=client)
