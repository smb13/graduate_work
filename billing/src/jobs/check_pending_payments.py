from clients.alchemy import get_session
from clients.redis import get_redis
from clients.subscription import get_client
from clients.yookassa.client import YooKassa, get_yookassa
from httpx import AsyncClient
from redis import Redis

from core.enums import PaymentStatusEnum, TransactionKindEnum, TransactionProcessStateEnum
from main import lifespan
from schemas.transaction import PaymentInternal
from services.base import ServiceError
from services.payment import YooKassaPaymentService, get_yookassa_payment_service
from services.subscription import SubscriptionService, get_subscription_service
from services.transaction import TransactionService, get_transaction_service


@lifespan(None)
async def check_pending() -> None:
    redis: Redis = await get_redis()
    yookassa: YooKassa = await get_yookassa()
    client: AsyncClient = await get_client()

    async for session in get_session():
        transaction_service: TransactionService = get_transaction_service(alchemy=session, redis=redis)
        payment_service: YooKassaPaymentService = get_yookassa_payment_service(payment_client=yookassa)
        subscription_service: SubscriptionService = get_subscription_service(client=client)

        awaiting_payments = await transaction_service.list_transactions_query(
            kind=TransactionKindEnum.payment,
            process_state=TransactionProcessStateEnum.pending,
            cnt_attempts_range=(
                0,
                5,
            ),
        )
        transactions = await session.scalars(awaiting_payments)

        for transaction in transactions.yield_per(100):
            try:
                payment: PaymentInternal = await payment_service.get_payment_info(
                    payment_id=transaction.external_id,
                )
            except ServiceError:
                await transaction_service.increment_attempts(
                    transaction_id=transaction.id,
                )
                continue

            if not payment:
                await transaction_service.increment_attempts(
                    transaction_id=transaction.id,
                )
                continue

            match payment.status:
                case PaymentStatusEnum.succeeded:
                    try:
                        await subscription_service.activate_subscription(subscription_id=transaction.subscription_id)
                    except ServiceError:
                        await transaction_service.increment_attempts(
                            transaction_id=transaction.id,
                        )
                        continue

                    await transaction_service.update_transaction_process_state(
                        transaction_id=transaction.id,
                        process_state=TransactionProcessStateEnum.succeeded,
                        payment_method_id=payment.payment_method and payment.payment_method.id,
                    )
                case PaymentStatusEnum.canceled:
                    try:
                        await subscription_service.cancel_subscription(subscription_id=transaction.subscription_id)
                    except ServiceError:
                        await transaction_service.increment_attempts(
                            transaction_id=transaction.id,
                        )
                        continue
                    await transaction_service.increment_attempts(
                        transaction_id=transaction.id,
                    )
                case PaymentStatusEnum.pending:
                    await transaction_service.increment_attempts(
                        transaction_id=transaction.id,
                    )
                case _:
                    await transaction_service.increment_attempts(
                        transaction_id=transaction.id,
                    )
