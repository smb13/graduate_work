from decimal import Decimal
from uuid import UUID

from aioyookassa.types import Confirmation
from aioyookassa.types.payment import PaymentAmount
from clients.yookassa.client import YooKassa, get_yookassa
from fastapi import Depends

from core.config import settings
from schemas.transaction import PaymentInternal


class YooKassaPaymentService:
    def __init__(
        self,
        payment_client: YooKassa,
    ) -> None:
        self.payment_client = payment_client

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
        payment = await self.payment_client.create_payment(
            confirmation=confirmation,
            amount=payment_amount,
            description=description,
            payment_method_id=payment_method_id,
            save_payment_method=not payment_method_id,
            capture=True,
        )
        return PaymentInternal.model_validate(payment.model_dump())

    async def create_refund(
        self,
        amount: Decimal,
        currency: str,
        description: str,
        payment_to_refund_id: UUID = None,
    ) -> str:
        payment_amount = PaymentAmount(
            value=amount,
            currency=currency,
        )
        payment = await self.payment_client.create_refund(
            payment_id=str(payment_to_refund_id),
            amount=payment_amount,
            description=description,
        )
        return payment.confirmation.url


def get_yookassa_payment_service(
    payment_client: YooKassa = Depends(get_yookassa),
) -> YooKassaPaymentService:
    return YooKassaPaymentService(payment_client=payment_client)
