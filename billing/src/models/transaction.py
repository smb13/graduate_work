import uuid
from decimal import Decimal

from clients.alchemy import Base
from sqlalchemy import DECIMAL, UUID, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from core.enums import CurrencyEnum, TransactionKindEnum


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    external_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False, unique=True)
    payment_method_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )  # Nullable for non-recurring transactions
    refund_payment_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True)  # Only filled for refunds
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    kind: Mapped[TransactionKindEnum] = mapped_column(String(15), nullable=False)
    state: Mapped[str] = mapped_column(String(25), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    amount: Mapped[Decimal] = mapped_column(DECIMAL(asdecimal=True), nullable=False)
    currency: Mapped[CurrencyEnum] = mapped_column(String(3), nullable=False)
    dt_created: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    dt_changed: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    cnt_attempts: Mapped[int] = mapped_column(Integer, nullable=False)
    dt_last_attempt: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return "<Transaction(id={id}, action='{action}', user_id={user_id}, amount={amount}, state='{state}')>".format(
            id=self.id,
            action=self.action,
            user_id=self.user_id,
            amount=self.amount,
            state=self.state,
        )
