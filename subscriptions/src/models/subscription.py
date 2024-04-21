from datetime import date
import enum

from sqlalchemy import Column, ForeignKey, String, UniqueConstraint, Integer, Date, Enum, Identity
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from models.base import Base
from models.mixin import IdMixin, TimestampMixin


class SubscriptionStatus(enum.Enum):
    NEW = 'new'
    AWAITING_PAYMENTS = 'awaiting_payment'
    ACTIVE = 'active'
    AWAITING_RENEWAL = 'awaiting_renewal'
    INACTIVE = 'inactive'


class SubscriptionType(TimestampMixin, Base):
    __tablename__ = 'subscription_type'

    id = Column(Integer, Identity(), primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(String(255), unique=False, nullable=True)
    annual_price = Column(Integer, unique=False, nullable=False)
    monthly_price = Column(Integer, unique=False, nullable=False)
    start_of_sales = Column(Date, default=date.today())
    end_of_sales = Column(Date, default=date(year=3000, month=1, day=1))

    user_subscriptions = relationship('UserSubscription', back_populates='subscription_type', lazy='selectin')

    def __repr__(self) -> str:
        return f'<SubscriptionType name:{self.name}, description: {self.description}, ' + \
            f'annual_price:{self.annual_price}, monthly_price: {self.monthly_price}, ' + \
            f'start_of_sales:{self.start_of_sales}, end_of_sales: {self.end_of_sales}>'


class UserSubscription(IdMixin, TimestampMixin, Base):
    __tablename__ = 'user_subscription'

    __table_args__ = (
        UniqueConstraint('type_id', 'user_id', 'payment_method_id'),
    )

    type_id = Column(Integer,
                     ForeignKey('subscription_type.id', ondelete='CASCADE'),
                     nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    payment_method_id = Column(UUID(as_uuid=True), nullable=True)
    status = Column(Enum(SubscriptionStatus), nullable=False)
    start_of_subscription = Column(Date, nullable=True)
    end_of_subscription = Column(Date, nullable=True)

    subscription_type = relationship('SubscriptionType', back_populates='user_subscriptions', lazy='selectin')

    def __repr__(self) -> str:
        return f'<UserSubscription type_id:{self.type_id}, user_id: {self.user_id}, ' + \
            f'payment_method_id:{self.payment_method_id}, start_of_subscription: {self.start_of_subscription}, ' + \
            f'end_of_subscription:{self.end_of_subscription}>'
