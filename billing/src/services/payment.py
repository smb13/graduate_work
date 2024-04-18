from decimal import Decimal
from uuid import UUID

from aioyookassa.types import Confirmation
from aioyookassa.types.payment import PaymentAmount
from clients.yookassa.client import get_yookassa, YooKassa
from fastapi import Depends

from core.config import settings
from services.base import BasePaymentService


class YooKassaPaymentService(BasePaymentService):
    payment_client: YooKassa

    async def create_payment_redirect(
        self,
        amount: Decimal,
        currency: str,
        description: str,
        payment_method_id: UUID = None,
    ) -> str:
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
        )
        return payment.confirmation.url

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


def get_transaction_service(
    payment_client: YooKassa = Depends(get_yookassa),
) -> YooKassaPaymentService:
    return YooKassaPaymentService(payment_client=payment_client)
