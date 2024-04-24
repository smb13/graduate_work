from enum import Enum


class TransactionKindEnum(str, Enum):
    payment = "payment"
    refund = "refund"


class TransactionProcessStateEnum(str, Enum):
    new = "new"  # initial state, payment is created
    pending = "pending"  # payment is created and waiting for confirmation
    succeeded = "succeeded"  # payment is confirmed
    applied = "applied"  # payment is applied to subscription
    failed = "failed"  # payment is failed


class PaymentStatusEnum(str, Enum):
    pending = "pending"
    waiting_for_capture = "waiting_for_capture"
    succeeded = "succeeded"
    canceled = "canceled"


class CurrencyEnum(str, Enum):
    rub = "RUB"
