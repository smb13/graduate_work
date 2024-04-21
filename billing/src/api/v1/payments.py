import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination.cursor import CursorPage

from core.auth import SystemRolesEnum, check_permissions
from core.enums import PaymentStatusEnum, TransactionKindEnum, TransactionProcessStateEnum
from models import Transaction
from schemas.transaction import PaymentInternal, PaymentNewCreate, PaymentRenewCreate, PaymentResponse
from services.payment import YooKassaPaymentService, get_yookassa_payment_service
from services.transaction import TransactionService, get_transaction_service

router = APIRouter()


payment_not_found_exc = HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")


@router.post(
    "/new",
    response_model=PaymentResponse,
    status_code=HTTPStatus.CREATED,
    summary="Process a Payment for a new Subscription",
    dependencies=[Depends(check_permissions(SystemRolesEnum.admin))],
)
async def payment_new_create(
    payment_new: PaymentNewCreate,
    payment_service: YooKassaPaymentService = Depends(get_yookassa_payment_service),
    transaction_service: TransactionService = Depends(get_transaction_service),
) -> PaymentResponse:
    """Process a Payment for a new Subscription and save it as a Transaction to the database.

    Returns the created Transaction in status Pending and confirmation_url to be confirmed by User"""

    payment: PaymentInternal = await payment_service.create_payment(
        amount=payment_new.amount,
        currency=payment_new.currency,
        description=payment_new.description,
    )
    if payment.status != PaymentStatusEnum.pending:
        raise ValueError("Payment status is not pending")

    transaction = await transaction_service.payment_new_create(
        user_id=payment_new.user_id,
        description=payment_new.description,
        amount=payment_new.amount,
        currency=payment_new.currency,
        payment_created_at=payment.created_at,
        external_id=payment.id,
        payment_method_id=payment.payment_method.id if payment.payment_method else None,
        dt_last_attempt=payment.created_at,
        process_state=TransactionProcessStateEnum.pending,
    )

    return PaymentResponse(
        id=transaction.id,
        payment_method_id=transaction.payment_method_id,
        user_id=transaction.user_id,
        kind=transaction.kind,
        process_state=transaction.process_state,
        status=payment.status,
        description=transaction.description,
        amount=transaction.amount,
        currency=transaction.currency,
        created_at=transaction.created_at,
        payment_created_at=transaction.payment_created_at,
        changed_at=transaction.changed_at,
        cnt_attempts=transaction.cnt_attempts,
        last_attempt_at=transaction.last_attempt_at,
        confirmation_url=payment.confirmation.url,
    )


@router.post(
    "/renew",
    response_model=PaymentResponse,
    status_code=HTTPStatus.CREATED,
    summary="Add a Recurring Payment for an existing Subscription",
    dependencies=[Depends(check_permissions(SystemRolesEnum.admin))],
)
async def payment_renew_create(
    payment_renew: PaymentRenewCreate,
    transaction_service: TransactionService = Depends(get_transaction_service),
) -> PaymentResponse:
    """Add a Recurring Payment for an existing Subscription and save it as a Transaction to the database.

    Returns the created Transaction in status New
    Confirmation by user is not required"""

    transaction = await transaction_service.payment_renew_create(
        user_id=payment_renew.user_id,
        description=payment_renew.description,
        amount=payment_renew.amount,
        currency=payment_renew.currency,
        process_state=TransactionProcessStateEnum.new,
        payment_method_id=payment_renew.payment_method_id,
    )

    return PaymentResponse(
        id=transaction.id,
        payment_method_id=transaction.payment_method_id,
        user_id=transaction.user_id,
        kind=transaction.kind,
        process_state=transaction.process_state,
        description=transaction.description,
        amount=transaction.amount,
        currency=transaction.currency,
        changed_at=transaction.changed_at,
        cnt_attempts=transaction.cnt_attempts,
    )


@router.get(
    "",
    response_model=CursorPage[PaymentResponse],
    summary="Show the list of transactions",
    dependencies=[Depends(check_permissions(SystemRolesEnum.admin))],
)
async def users_list(
    user_id: uuid.UUID | None = None,
    payment_method_id: uuid.UUID | None = None,
    kind: TransactionKindEnum | None = None,
    state: PaymentStatusEnum | None = None,
    transaction_service: TransactionService = Depends(get_transaction_service),
) -> CursorPage[Transaction]:
    """List Transactions."""

    return await transaction_service.list_transactions_paginated(
        user_id=user_id,
        payment_method_id=payment_method_id,
        kind=kind,
        state=state,
    )
