import uuid
from decimal import Decimal

from clients.alchemy import get_session
from clients.redis import get_redis
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.enums import CurrencyEnum, TransactionKindEnum, TransactionStateEnum
from models.transaction import Transaction
from schemas.transaction import PaymentResponse
from services.base import BaseDBService


class TransactionService(BaseDBService):
    async def payment_new_create(
        self,
        user_id: uuid.UUID,
        description: str,
        amount: Decimal,
        currency: CurrencyEnum,
    ) -> PaymentResponse:
        """Creates a new payment transaction."""
        transaction = Transaction(
            user_id=user_id,
            description=description,
            amount=amount,
            currency=currency,
            kind=TransactionKindEnum.payment,
            state=TransactionStateEnum.pending,
        )
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return PaymentResponse.model_validate(transaction)

    async def payment_renew_create(
        self,
        user_id: uuid.UUID,
        description: str,
        amount: Decimal,
        currency: CurrencyEnum,
        payment_method_id: uuid.UUID,
    ) -> PaymentResponse:
        """Creates a new payment transaction."""
        transaction = Transaction(
            user_id=user_id,
            description=description,
            amount=amount,
            currency=currency,
            kind=TransactionKindEnum.payment,
            state=TransactionStateEnum.pending,
            payment_method_id=payment_method_id,
        )
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return PaymentResponse.model_validate(transaction)

    async def payment_get_for_refund(
        self,
        user_id: uuid.UUID,
        payment_method_id: uuid.UUID,
    ):
        """Gets last payment for payment_method_id and refunds it."""
        payment_to_refund = await self.session.scalars(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .where(Transaction.payment_method_id == payment_method_id)
            .where(Transaction.kind == TransactionKindEnum.payment)
            .where(Transaction.state == TransactionStateEnum.succeeded)
            .order_by(Transaction.dt_created.desc())
            .limit(1),
        )
        payment_to_refund = payment_to_refund.first()

        if not payment_to_refund:
            return None

        return PaymentResponse.model_validate(payment_to_refund)

    async def payment_refund_create(
        self,
        user_id: uuid.UUID,
        description: str,
        amount: Decimal,
        currency: CurrencyEnum,
        payment_method_id: uuid.UUID,
        payment_to_refund_id: uuid.UUID,
    ) -> PaymentResponse | None:
        """Gets last payment for payment_method_id and refunds it."""

        transaction = Transaction(
            user_id=user_id,
            description=description,
            amount=amount,
            currency=currency,
            kind=TransactionKindEnum.refund,
            state=TransactionStateEnum.pending,
            payment_method_id=payment_method_id,
            refund_payment_id=payment_to_refund_id,
        )

        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return PaymentResponse.model_validate(transaction)


def get_transaction_service(
    alchemy: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
) -> TransactionService:
    return TransactionService(session=alchemy, redis=redis)
