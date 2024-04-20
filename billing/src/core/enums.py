from enum import Enum


class TransactionKindEnum(str, Enum):
    payment = "payment"
    refund = "refund"


class TransactionStateEnum(str, Enum):
    pending = "pending"
    waiting_for_capture = "waiting_for_capture"
    succeeded = "succeeded"
    canceled = "canceled"


class CurrencyEnum(str, Enum):
    rub = "RUB"
