from functools import lru_cache
from http import HTTPStatus
from fastapi import HTTPException
from typing import Any, Coroutine

import aiohttp
import backoff
from aiohttp.client_exceptions import ClientError
from core.config import billing_settings


class BillingService:

    @backoff.on_exception(backoff.expo,
                          ClientError,
                          max_tries=billing_settings.backoff_max_tries)
    async def call_to_billing(self, uri: str, **kwargs) -> Coroutine[Any, Any, str] | Exception:
        url = billing_settings.get_address() + uri
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=kwargs) as response:
                if response.status in (HTTPStatus.OK, HTTPStatus.CREATED):
                    return response.text()
                else:
                    raise HTTPException(status_code=response.status, detail=response.text())


@lru_cache()
def get_billing_service(
) -> BillingService:
    return BillingService()
