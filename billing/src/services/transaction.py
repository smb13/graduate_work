import datetime as dt
import uuid
from decimal import Decimal

from clients.alchemy import get_session
from clients.redis import get_redis
from fastapi import Depends
from fastapi_pagination.cursor import CursorPage
from fastapi_pagination.ext.sqlalchemy import paginate
from redis.asyncio import Redis
from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.enums import CurrencyEnum, TransactionKindEnum, TransactionProcessStateEnum
from models.transaction import Transaction
from services.base import BaseDBService


class TransactionService(BaseDBService):
    async def payment_new_create(
        self,
        subscription_id: uuid.UUID,
        user_id: uuid.UUID,
        description: str,
        amount: Decimal,
        currency: CurrencyEnum,
        process_state: TransactionProcessStateEnum,
        external_id: uuid.UUID | None = None,
        payment_created_at: dt.datetime | None = None,
        payment_method_id: uuid.UUID | None = None,
        dt_last_attempt: dt.datetime | None = None,
    ) -> Transaction:
        """Creates a new payment transaction."""
        transaction = Transaction(
            subscription_id=subscription_id,
            user_id=user_id,
            description=description,
            amount=amount,
            currency=currency,
            external_id=external_id,
            payment_created_at=payment_created_at,
            payment_method_id=payment_method_id,
            kind=TransactionKindEnum.payment,
            process_state=process_state,
        )
        if dt_last_attempt:
            transaction.dt_last_attempt = dt_last_attempt

        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def payment_renew_create(
        self,
        subscription_id: uuid.UUID,
        user_id: uuid.UUID,
        description: str,
        amount: Decimal,
        currency: CurrencyEnum,
        process_state: TransactionProcessStateEnum,
        payment_method_id: uuid.UUID,
    ) -> Transaction:
        """Creates a new payment transaction."""
        transaction = Transaction(
            subscription_id=subscription_id,
            user_id=user_id,
            description=description,
            amount=amount,
            currency=currency,
            kind=TransactionKindEnum.payment,
            process_state=process_state,
            payment_method_id=payment_method_id,
        )
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def update_transaction_process_state(
        self,
        transaction_id: uuid.UUID,
        process_state: TransactionProcessStateEnum,
        external_id: uuid.UUID | None = None,
        payment_method_id: uuid.UUID | None = None,
    ) -> Transaction | None:
        transaction: Transaction | None = await self.session.get(Transaction, transaction_id)
        if transaction is None:
            return None

        transaction.process_state = process_state

        if external_id:
            transaction.external_id = external_id

        if payment_method_id:
            transaction.payment_method_id = payment_method_id

        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def increment_attempts(self, transaction_id: uuid.UUID) -> Transaction | None:
        transaction: Transaction | None = await self.session.get(Transaction, transaction_id)
        if transaction is None:
            return None

        transaction.cnt_attempts += 1
        transaction.dt_last_attempt = dt.datetime.now()

        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def payment_get_for_refund(
        self,
        user_id: uuid.UUID,
        subscription_id: uuid.UUID,
    ) -> Transaction | None:
        """Gets last successful payment for subscription_id."""
        payment_to_refund = await self.session.scalars(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .where(Transaction.subscription_id == subscription_id)
            .where(Transaction.kind == TransactionKindEnum.payment)
            .where(Transaction.process_state == TransactionProcessStateEnum.succeeded)
            .order_by(Transaction.created_at.desc())
            .limit(1),
        )
        payment_to_refund = payment_to_refund.first()

        if not payment_to_refund:
            return None

        return payment_to_refund

    async def payment_refund_create(
        self,
        subscription_id: uuid.UUID,
        user_id: uuid.UUID,
        description: str,
        amount: Decimal,
        currency: CurrencyEnum,
        external_id: uuid.UUID,
        payment_created_at: dt.datetime,
        payment_method_id: uuid.UUID,
        payment_to_refund_id: uuid.UUID,
        process_state: TransactionProcessStateEnum,
    ) -> Transaction:
        """Creates a new refund transaction."""

        transaction = Transaction(
            subscription_id=subscription_id,
            user_id=user_id,
            description=description,
            amount=amount,
            currency=currency,
            external_id=external_id,
            kind=TransactionKindEnum.refund,
            process_state=process_state,
            payment_method_id=payment_method_id,
            refund_payment_id=payment_to_refund_id,
            created_at=payment_created_at,
        )

        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def list_transactions_paginated(
        self,
        subscription_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        payment_method_id: uuid.UUID | None = None,
        kind: TransactionKindEnum | None = None,
        process_state: TransactionProcessStateEnum | None = None,
        cnt_attempts_range: tuple[int | None, int | None] | None = None,
        last_attempt_at_date_range: tuple[dt.date | None, dt.date | None] | None = None,
    ) -> CursorPage[Transaction]:
        """List transactions."""
        transactions = await self.list_transactions_query(
            subscription_id=subscription_id,
            user_id=user_id,
            payment_method_id=payment_method_id,
            kind=kind,
            process_state=process_state,
            cnt_attempts_range=cnt_attempts_range,
            last_attempt_at_date_range=last_attempt_at_date_range,
        )
        return await paginate(self.session, transactions)

    @staticmethod
    async def list_transactions_query(  # noqa: C901
        subscription_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        payment_method_id: uuid.UUID | None = None,
        kind: TransactionKindEnum | None = None,
        process_state: TransactionProcessStateEnum | None = None,
        cnt_attempts_range: tuple[int | None, int | None] | None = None,
        last_attempt_at_date_range: tuple[dt.date | None, dt.date | None] | None = None,
    ) -> Select:
        """List transactions Query."""
        query = select(Transaction).order_by(Transaction.created_at.desc())

        if subscription_id:
            query = query.where(Transaction.subscription_id == subscription_id)
        if user_id:
            query = query.where(Transaction.user_id == user_id)
        if payment_method_id:
            query = query.where(Transaction.payment_method_id == payment_method_id)
        if kind:
            query = query.where(Transaction.kind == kind)
        if process_state:
            query = query.where(Transaction.process_state == process_state)
        if cnt_attempts_range:
            if cnt_attempts_range[0] is not None:
                query = query.where(Transaction.cnt_attempts >= cnt_attempts_range[0])
            if cnt_attempts_range[1] is not None:
                query = query.where(Transaction.cnt_attempts <= cnt_attempts_range[1])
        if last_attempt_at_date_range:
            if last_attempt_at_date_range[0] is not None:
                query = query.where(
                    or_(
                        Transaction.last_attempt_at.is_(None),
                        func.date(Transaction.last_attempt_at) >= last_attempt_at_date_range[0],
                    ),
                )
            if last_attempt_at_date_range[1] is not None:
                query = query.where(
                    or_(
                        Transaction.last_attempt_at.is_(None),
                        func.date(Transaction.last_attempt_at) <= last_attempt_at_date_range[1],
                    ),
                )

        return query  # noqa: R504


def get_transaction_service(
    alchemy: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
) -> TransactionService:
    return TransactionService(session=alchemy, redis=redis)
