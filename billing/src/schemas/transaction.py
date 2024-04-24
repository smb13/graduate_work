import datetime as dt
import uuid
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from core.enums import CurrencyEnum, PaymentStatusEnum, TransactionKindEnum, TransactionProcessStateEnum


class PaymentNewCreate(BaseModel):
    user_id: UUID
    subscription_id: UUID
    description: str
    amount: Decimal = Field(..., gt=0)  # Ensure amount is greater than 0
    currency: CurrencyEnum


class PaymentRenewCreate(BaseModel):
    user_id: UUID
    subscription_id: UUID
    description: str
    amount: Decimal = Field(..., gt=0)  # Ensure amount is greater than 0
    currency: CurrencyEnum
    payment_method_id: UUID


class RefundCreate(BaseModel):
    user_id: UUID
    subscription_id: UUID
    description: str
    amount: Decimal = Field(..., gt=0)  # Ensure amount is greater than 0
    currency: CurrencyEnum


class PaymentResponse(BaseModel):
    id: UUID
    subscription_id: UUID
    payment_method_id: UUID | None = None
    refund_payment_id: UUID | None = None
    user_id: UUID
    kind: TransactionKindEnum
    process_state: TransactionProcessStateEnum
    status: PaymentStatusEnum | None = None
    description: str
    amount: Decimal
    currency: CurrencyEnum
    created_at: dt.datetime
    changed_at: dt.datetime
    payment_created_at: dt.datetime | None
    cnt_attempts: int | None = None
    last_attempt_at: dt.datetime | None = None
    confirmation_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ConfirmationType(str, Enum):
    redirect = "redirect"


class PaymentAmount(BaseModel):
    """
    Payment amount
    """

    value: int | float
    currency: CurrencyEnum


class PaymentMethod(BaseModel):
    """
    Payment method
    """

    id: uuid.UUID
    saved: bool


class Confirmation(BaseModel):
    """
    Confirmation
    """

    type: ConfirmationType
    url: str | None


class PaymentInternal(BaseModel):
    """
    Payment
    """

    id: uuid.UUID
    status: PaymentStatusEnum
    amount: PaymentAmount
    description: str
    payment_method: PaymentMethod | None = None
    created_at: dt.datetime
    confirmation: Confirmation | None = None
    test: bool
    refunded_amount: PaymentAmount | None = None
    paid: bool
    cancellation_details: dict | None = None
    metadata: dict | None = None


class RefundInternal(BaseModel):
    """
    Refund
    """

    id: uuid.UUID
    status: PaymentStatusEnum
    amount: PaymentAmount
    description: str
    created_at: dt.datetime
    payment_id: uuid.UUID
    test: bool | None = None
    cancellation_details: dict | None = None
    metadata: dict | None = None
