import datetime as dt
import uuid
from decimal import Decimal

from clients.alchemy import Base
from sqlalchemy import DECIMAL, UUID, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from core.enums import CurrencyEnum, TransactionKindEnum, TransactionProcessStateEnum


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    subscription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    external_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        unique=True,
    )
    payment_method_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )  # Nullable for non-recurring transactions
    refund_payment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )  # Only filled for refunds
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    kind: Mapped[TransactionKindEnum] = mapped_column(
        String(15),
        nullable=False,
    )
    process_state: Mapped[TransactionProcessStateEnum] = mapped_column(
        String(25),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="",
    )
    amount: Mapped[Decimal] = mapped_column(
        DECIMAL(asdecimal=True),
        nullable=False,
    )
    currency: Mapped[CurrencyEnum] = mapped_column(
        String(3),
        nullable=False,
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    changed_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.current_timestamp(),
    )
    payment_created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    cnt_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    last_attempt_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        return "<Transaction(id={id}, action='{kind}', user_id={user_id}, amount={amount}, state='{state}')>".format(
            id=self.id,
            kind=self.kind,
            user_id=self.user_id,
            amount=self.amount,
            state=self.state,
        )
