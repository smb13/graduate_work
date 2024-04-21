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
                          max_tries=1)
    async def new_payment(self, **kwargs) -> Coroutine[Any, Any, str] | Exception:
        url = billing_settings.get_address() + billing_settings.new_uri
        return {"confirmation_url":
                    "https://yoomoney.ru/api-pages/v2/payment-confirm/epl?orderId=2419a771-000f-5000-9000-1edaf29243f2"}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=kwargs) as response:
                if response.status == HTTPStatus.OK:
                    return response.text()
                else:
                    HTTPException(status_code=response.status, detail=response.text())


@lru_cache()
def get_billing_service(
) -> BillingService:
    return BillingService()