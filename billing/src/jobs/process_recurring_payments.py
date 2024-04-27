import asyncio
import datetime as dt
import logging

from clients.alchemy import get_session
from clients.redis import get_redis
from clients.subscription import get_client
from clients.yookassa.client import YooKassa, get_yookassa
from httpx import AsyncClient
from redis import Redis

from core.config import settings
from core.enums import PaymentStatusEnum, TransactionKindEnum, TransactionProcessStateEnum
from main import lifespan
from schemas.transaction import PaymentInternal
from services.base import ServiceError
from services.payment import YooKassaPaymentService, get_yookassa_payment_service
from services.subscription import SubscriptionService, get_subscription_service
from services.transaction import TransactionService, get_transaction_service

logger = logging.getLogger(__name__)


@lifespan(None)
async def process_recurring() -> None:
    redis: Redis = await get_redis()
    yookassa: YooKassa = await get_yookassa()
    client: AsyncClient = await get_client()

    async for session in get_session():
        transaction_service: TransactionService = get_transaction_service(alchemy=session, redis=redis)
        payment_service: YooKassaPaymentService = get_yookassa_payment_service(payment_client=yookassa)
        subscription_service: SubscriptionService = get_subscription_service(client=client)

        awaiting_payments = await transaction_service.list_transactions_query(
            kind=TransactionKindEnum.payment,
            process_state=TransactionProcessStateEnum.new,
            cnt_attempts_range=(
                0,
                settings.payment_attempts_limit,
            ),
            last_attempt_at_date_range=(
                dt.date.today() - dt.timedelta(days=settings.payment_attempts_limit),
                dt.date.today(),
            ),
        )
        transactions = await session.scalars(awaiting_payments)

        for transaction in transactions.yield_per(100):
            try:
                payment: PaymentInternal = await payment_service.create_payment(
                    amount=transaction.amount,
                    currency=transaction.currency,
                    description=transaction.description,
                    payment_method_id=transaction.payment_method_id,
                )
            except ServiceError as exc:
                raise ValueError(f"Payment external_id: {transaction.external_id} cannot be created: {exc}")

            if not payment:
                raise ValueError(f"Payment external_id: {transaction.external_id} cannot be created")

            match payment.status:
                case PaymentStatusEnum.succeeded:
                    await transaction_service.update_transaction_process_state(
                        transaction_id=transaction.id,
                        process_state=TransactionProcessStateEnum.pending,
                        external_id=payment.id,
                        payment_method_id=transaction.payment_method_id,
                    )

                    try:
                        await subscription_service.activate_subscription(subscription_id=transaction.subscription_id)
                    except ServiceError as exc:
                        await transaction_service.increment_attempts(
                            transaction_id=transaction.id,
                        )
                        logger.error(f"Subscription activation failed: {exc}")
                        raise

                    await transaction_service.update_transaction_process_state(
                        transaction_id=transaction.id,
                        process_state=TransactionProcessStateEnum.succeeded,
                    )
                case PaymentStatusEnum.canceled:
                    try:
                        await subscription_service.cancel_subscription(subscription_id=transaction.subscription_id)
                    except ServiceError as exc:
                        await transaction_service.increment_attempts(
                            transaction_id=transaction.id,
                        )
                        logger.error(f"Subscription cancellation failed: {exc}")
                        raise

                case PaymentStatusEnum.pending:
                    await transaction_service.increment_attempts(
                        transaction_id=transaction.id,
                    )
                case _:
                    raise ValueError(f"Unexpected payment status: {payment.status}")


async def process_recurring_job() -> None:
    """Process of the subscriptions' renewal."""
    loop = asyncio.get_event_loop()
    await loop.create_task(process_recurring())
