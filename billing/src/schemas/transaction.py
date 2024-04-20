import datetime as dt
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from core.enums import CurrencyEnum, TransactionKindEnum, TransactionStateEnum


class PaymentNewCreate(BaseModel):
    user_id: UUID
    description: str
    amount: Decimal
    currency: "CurrencyEnum"


class PaymentRenewCreate(BaseModel):
    user_id: UUID
    description: str
    amount: Decimal
    currency: "CurrencyEnum"
    payment_method_id: UUID


class RefundCreate(BaseModel):
    user_id: UUID
    description: str
    amount: Decimal
    currency: "CurrencyEnum"
    payment_method_id: UUID


class PaymentResponse(BaseModel):
    id: UUID
    payment_method_id: UUID
    refund_payment_id: UUID
    user_id: UUID
    kind: "TransactionKindEnum"
    state: "TransactionStateEnum"
    description: str
    amount: Decimal
    currency: "CurrencyEnum"
    dt_created: dt.datetime
    dt_changed: dt.datetime
    cnt_attempts: int
    dt_last_attempt: dt.datetime

    model_config = ConfigDict(from_attributes=True)
