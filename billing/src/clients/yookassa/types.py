import datetime as dt
from enum import Enum

from aioyookassa.types.enum import PaymentStatus
from aioyookassa.types.payment import Deal, PaymentAmount
from pydantic import BaseModel


class CancellationParty(str, Enum):
    yoo_money = "yoo_money"
    refund_network = "refund_network"


class CancellationReason(str, Enum):
    insufficient_funds = "insufficient_funds"
    general_decline = "general_decline"
    rejected_by_payee = "rejected_by_payee"
    yoo_money_account_closed = "yoo_money_account_closed"


class ReceiptRegistration(str, Enum):
    pending = "pending"
    succeeded = "succeeded"
    canceled = "canceled"


class CancellationDetails(BaseModel):
    party: CancellationParty
    reason: CancellationReason


class RefundSource(BaseModel):
    account_id: str
    amount: PaymentAmount


class RefundMethodEnum(str, Enum):
    sbp = "sbp"


class RefundMethod(BaseModel):
    type: RefundMethodEnum
    sbp_operation_id: str | None


class Refund(BaseModel):
    """
    Refund
    """

    id: str
    payment_id: str
    status: PaymentStatus
    cancellation_details: CancellationDetails
    created_at: dt.datetime
    amount: PaymentAmount
    description: str | None = None
    sources: list[RefundSource] | None = None
    platform_fee_amount: PaymentAmount | None = None
    deal: Deal | None = None
    refund_method: RefundMethod | None = None
