import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination.cursor import CursorPage

from core.auth import SystemRolesEnum, check_permissions
from core.enums import PaymentStatusEnum, TransactionKindEnum, TransactionProcessStateEnum
from models import Transaction
from schemas.transaction import (
    PaymentInternal,
    PaymentNewCreate,
    PaymentRenewCreate,
    PaymentResponse,
    RefundCreate,
    RefundInternal,
)
from services.base import ServiceError
from services.payment import YooKassaPaymentService, get_yookassa_payment_service
from services.transaction import TransactionService, get_transaction_service

router = APIRouter()


payment_not_found_exc = HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Payment not found")


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
    try:
        payment: PaymentInternal = await payment_service.create_payment(
            amount=payment_new.amount,
            currency=payment_new.currency,
            description=payment_new.description,
        )
    except ServiceError as exc:
        raise ValueError(f"Payment cannot be created: {exc}") from exc

    if not payment:
        raise ValueError("Payment cannot be created")

    if payment.status != PaymentStatusEnum.pending:
        raise ValueError("Payment status is not pending")

    transaction = await transaction_service.payment_new_create(
        subscription_id=payment_new.subscription_id,
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
        subscription_id=transaction.subscription_id,
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
        subscription_id=payment_renew.subscription_id,
        user_id=payment_renew.user_id,
        description=payment_renew.description,
        amount=payment_renew.amount,
        currency=payment_renew.currency,
        process_state=TransactionProcessStateEnum.new,
        payment_method_id=payment_renew.payment_method_id,
    )

    return PaymentResponse(
        id=transaction.id,
        subscription_id=transaction.subscription_id,
        payment_method_id=transaction.payment_method_id,
        user_id=transaction.user_id,
        kind=transaction.kind,
        process_state=transaction.process_state,
        description=transaction.description,
        amount=transaction.amount,
        currency=transaction.currency,
        created_at=transaction.created_at,
        payment_created_at=transaction.payment_created_at,
        changed_at=transaction.changed_at,
        cnt_attempts=transaction.cnt_attempts,
    )


@router.post(
    "/refund",
    response_model=PaymentResponse,
    summary="Refund a Transaction",
    dependencies=[Depends(check_permissions(SystemRolesEnum.admin))],
)
async def payment_refund_create(
    payment_refund: RefundCreate,
    payment_service: YooKassaPaymentService = Depends(get_yookassa_payment_service),
    transaction_service: TransactionService = Depends(get_transaction_service),
) -> PaymentResponse:
    """Process a Refund for a Payment and save it as a Transaction to the database.

    Returns the created Refund Transaction"""
    payment_for_refund = await transaction_service.payment_get_for_refund(
        user_id=payment_refund.user_id,
        subscription_id=payment_refund.subscription_id,
    )
    if not payment_for_refund:
        raise payment_not_found_exc

    try:
        refund: RefundInternal = await payment_service.create_refund(
            amount=payment_refund.amount,
            currency=payment_refund.currency,
            description=payment_refund.description,
            payment_to_refund_id=payment_for_refund.external_id,
        )
    except ServiceError as exc:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if not refund:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Unknown error",
        )

    if refund.status != PaymentStatusEnum.succeeded:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Payment was not succeeded and can not be refunded",
        )

    transaction = await transaction_service.payment_refund_create(
        subscription_id=payment_refund.subscription_id,
        user_id=payment_refund.user_id,
        description=payment_refund.description,
        amount=payment_refund.amount,
        currency=payment_refund.currency,
        payment_created_at=refund.created_at,
        external_id=refund.id,
        payment_method_id=payment_for_refund.payment_method_id,
        payment_to_refund_id=payment_for_refund.id,
        process_state=TransactionProcessStateEnum.succeeded,
    )

    return PaymentResponse(
        id=transaction.id,
        subscription_id=transaction.subscription_id,
        payment_method_id=transaction.payment_method_id,
        refund_payment_id=payment_for_refund.id,
        user_id=transaction.user_id,
        kind=transaction.kind,
        process_state=transaction.process_state,
        status=refund.status,
        description=transaction.description,
        amount=transaction.amount,
        currency=transaction.currency,
        created_at=transaction.created_at,
        changed_at=transaction.changed_at,
        payment_created_at=transaction.payment_created_at,
    )


@router.get(
    "",
    response_model=CursorPage[PaymentResponse],
    summary="Show the list of Transactions",
    dependencies=[Depends(check_permissions(SystemRolesEnum.admin))],
)
async def users_list(
    subscription_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    payment_method_id: uuid.UUID | None = None,
    kind: TransactionKindEnum | None = None,
    process_state: TransactionProcessStateEnum | None = None,
    transaction_service: TransactionService = Depends(get_transaction_service),
) -> CursorPage[Transaction]:
    """List Transactions."""

    return await transaction_service.list_transactions_paginated(
        subscription_id=subscription_id,
        user_id=user_id,
        payment_method_id=payment_method_id,
        kind=kind,
        process_state=process_state,
    )
