import typing
from decimal import Decimal
from uuid import UUID

import backoff
from aiohttp import ClientConnectionError
from aioyookassa.exceptions import APIError
from aioyookassa.types import Confirmation
from aioyookassa.types.payment import PaymentAmount
from clients.yookassa.client import YooKassa, get_yookassa
from fastapi import Depends

from core.config import settings
from core.enums import PaymentStatusEnum
from schemas.transaction import PaymentInternal, RefundInternal
from services.base import ServiceError


class YooKassaPaymentService:
    def __init__(
        self,
        payment_client: YooKassa,
    ) -> None:
        self.payment_client = payment_client

    @backoff.on_exception(
        backoff.expo,
        exception=ClientConnectionError,
        base=10,
        max_tries=4,
    )
    async def create_payment(
        self,
        amount: Decimal,
        currency: str,
        description: str,
        payment_method_id: UUID | None = None,
    ) -> PaymentInternal:
        confirmation = Confirmation(
            type="redirect",
            return_url=settings.payment_return_url,
        )
        payment_amount = PaymentAmount(
            value=amount,
            currency=currency,
        )
        try:
            payment = await self.payment_client.create_payment(
                confirmation=confirmation,
                amount=payment_amount,
                description=description,
                payment_method_id=str(payment_method_id) if payment_method_id else None,
                save_payment_method=not payment_method_id,
                capture=True,
            )
        except APIError as exc:
            raise ServiceError(exc.text or str(exc))
        else:
            return PaymentInternal.model_validate(payment.model_dump())

    @backoff.on_exception(
        backoff.expo,
        exception=ClientConnectionError,
        base=10,
        max_tries=4,
    )
    async def create_refund(
        self,
        amount: Decimal,
        currency: str,
        description: str,
        payment_to_refund_id: UUID,
    ) -> RefundInternal:
        payment_amount = PaymentAmount(
            value=amount,
            currency=currency,
        )
        try:
            refund = await self.payment_client.create_refund(
                payment_id=str(payment_to_refund_id),
                amount=payment_amount,
                description=description,
            )
        except APIError as exc:
            raise ServiceError(exc.text or str(exc))
        else:
            return RefundInternal.model_validate(refund.model_dump())

    @backoff.on_exception(
        backoff.expo,
        exception=ClientConnectionError,
        base=10,
        max_tries=4,
    )
    async def get_payment_info(
        self,
        payment_id: UUID | None = None,
    ) -> PaymentInternal:
        try:
            payment = await self.payment_client.get_payment(
                payment_id=str(payment_id),
            )
        except APIError as exc:
            raise ServiceError(exc.text or str(exc))
        else:
            return PaymentInternal.model_validate(payment.model_dump())

    @backoff.on_exception(
        backoff.expo,
        exception=ClientConnectionError,
        base=10,
        max_tries=4,
    )
    async def get_payments_info(
        self,
        status: PaymentStatusEnum | None = None,
    ) -> typing.AsyncGenerator[PaymentInternal, None]:
        cursor = None

        while True:
            try:
                result = await self.payment_client.get_payments(
                    status=status,
                    limit=100,
                    cursor=cursor,
                )
            except APIError as exc:
                raise ServiceError(exc.text or str(exc))
            else:
                for payment in result.list:
                    yield PaymentInternal.model_validate(payment.model_dump())
                cursor = result.cursor


def get_yookassa_payment_service(
    payment_client: YooKassa = Depends(get_yookassa),
) -> YooKassaPaymentService:
    return YooKassaPaymentService(payment_client=payment_client)
