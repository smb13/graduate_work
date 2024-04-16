from datetime import date

from sqlalchemy import Column, ForeignKey, String, UniqueConstraint, Integer, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from models.base import Base
from models.mixin import IdMixin, TimestampMixin


class SubscriptionType(IdMixin, TimestampMixin, Base):
    __tablename__ = 'subscription_type'

    name = Column(String(255), unique=True, nullable=False)
    description = Column(String(255), unique=False, nullable=True)
    annual_price = Column(Integer, unique=False, nullable=False)
    monthly_price = Column(Integer, unique=False, nullable=False)
    start_of_sales = Column(Date, default=date.today())
    end_of_sales = Column(Date, default=date(year=3000, month=1, day=1))

    users = relationship('UserSubscription', back_populates='subscription_type', lazy='selectin')

    def __repr__(self) -> str:
        return f'<SubscriptionType name:{self.name}, description: {self.description}, ' + \
            f'annual_price:{self.annual_price}, monthly_price: {self.monthly_price}, ' + \
            f'start_of_sales:{self.start_of_sales}, end_of_sales: {self.end_of_sales}>'


class UserSubscription(IdMixin, TimestampMixin, Base):
    __tablename__ = 'user_subscription'

    __table_args__ = (
        UniqueConstraint('type_id', 'user_id', 'payment_method_id'),
    )

    type_id = Column(UUID(as_uuid=True),
                     ForeignKey('subscription_type.id', ondelete='CASCADE'),
                     nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    payment_method_id = Column(UUID(as_uuid=True), nullable=False)
    start_of_subscription = Column(Date, nullable=False)
    end_of_subscription = Column(Date, nullable=False)

    subscription_type = relationship('SubscriptionType', back_populates='users', lazy='selectin')

    def __repr__(self) -> str:
        return f'<UserSubscription type_id:{self.type_id}, user_id: {self.user_id}, ' + \
            f'payment_method_id:{self.payment_method_id}, start_of_subscription: {self.start_of_subscription}, ' + \
            f'end_of_subscription:{self.end_of_subscription}>'
