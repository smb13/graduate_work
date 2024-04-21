import asyncio
from typing import cast

from clients.alchemy import get_session
from clients.redis import get_redis
from clients.yookassa.client import YooKassa, get_yookassa
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from core.enums import PaymentStatusEnum, TransactionProcessStateEnum
from main import lifespan
from schemas.transaction import PaymentInternal
from services.payment import YooKassaPaymentService, get_yookassa_payment_service
from services.transaction import TransactionService, get_transaction_service


@lifespan(None)
async def process_recurring_payments() -> None:
    redis: Redis = await get_redis()
    yookassa: YooKassa = await get_yookassa()

    async with get_session() as session:
        cast("AsyncSession", session)
        transaction_service: TransactionService = get_transaction_service(alchemy=session, redis=redis)
        payment_service: YooKassaPaymentService = get_yookassa_payment_service(payment_client=yookassa)

        awaiting_payments = await transaction_service.list_transactions_query()
        transactions = await session.scalars(awaiting_payments)

        for transaction in transactions.yield_per(100):
            payment: PaymentInternal = await payment_service.create_payment(
                amount=transaction.amount,
                currency=transaction.currency,
                description=transaction.description,
                payment_method_id=transaction.payment_method_id,
            )
            match payment.status:
                case PaymentStatusEnum.succeeded:
                    # TODO: Здесь надо сделать запрос в сервис подписок и обновить статус подписки
                    await transaction_service.update_transaction_process_state(
                        transaction_id=transaction.id,
                        process_state=TransactionProcessStateEnum.succeeded,
                    )
                case PaymentStatusEnum.canceled:
                    await transaction_service.increment_attempts(
                        transaction_id=transaction.id,
                    )
                case PaymentStatusEnum.pending:
                    await transaction_service.update_transaction_process_state(
                        transaction_id=transaction.id,
                        process_state=TransactionProcessStateEnum.failed,
                    )
                case _:
                    raise ValueError(f"Unexpected payment status: {payment.status}")


def process_recurring_payments_job() -> None:
    """Process a Recurring Payment."""

    loop = asyncio.get_event_loop()
    loop.run_until_complete(process_recurring_payments())
    loop.close()
