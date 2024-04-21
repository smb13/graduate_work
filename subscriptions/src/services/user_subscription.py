from datetime import date
from functools import lru_cache
from http import HTTPStatus
from typing import Sequence
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import select, update, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.subscription import UserSubscription, SubscriptionStatus
from schemas.user_subscription import PaymentMethodId

user_subscription_1 = UserSubscription(
    type_id=2,
    payment_method_id=UUID('5a3f85b0-b4e2-432b-8732-0813bf09c29f'),
    status='active',
    start_of_subscription=date(2024, 4, 21),
    end_of_subscription=date(2024, 4, 21),
    id=UUID('58842c26-45fa-4aac-aa55-19062939e69f')
)
user_subscription_2 = UserSubscription(
    type_id=3,
    payment_method_id=UUID('437bc796-035b-4d02-a247-c6ed607e9868'),
    status='active',
    start_of_subscription=date(2024, 4, 21),
    end_of_subscription=date(2024, 4, 21),
    id=UUID('8ed2b403-f889-4887-8a8a-d47d33fca1dd')
)


class UserSubscriptionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def activate_subscription(self, user_subscription_id: UUID, payment_method_id: PaymentMethodId):
        user_subscription = (
            await self.db.execute(select(UserSubscription)
                                  .where(and_(UserSubscription.id == user_subscription_id,
                                              or_(UserSubscription.status == SubscriptionStatus.AWAITING_PAYMENT,
                                                  UserSubscription.status == SubscriptionStatus.AWAITING_RENEWAL)))
                                  )
        ).scalars().first()
        if not user_subscription:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail='User subscription not found or does not have appropriate status')
        today = date.today()
        end_of_subscription = date(year=today.year + 1, month=today.month, day=today.day)
        if not user_subscription.start_of_subscription:
            await self.db.execute(update(UserSubscription)
                                  .where(UserSubscription.id == user_subscription_id)
                                  .values(status=SubscriptionStatus.ACTIVE,
                                          start_of_subscription=today,
                                          end_of_subscription=end_of_subscription,
                                          payment_method_id=payment_method_id.payment_method_id))
        else:
            await self.db.execute(update(UserSubscription)
                                  .where(UserSubscription.id == user_subscription_id)
                                  .values(status=SubscriptionStatus.ACTIVE,
                                          end_of_subscription=end_of_subscription,
                                          payment_method_id=payment_method_id.payment_method_id))
        await self.db.commit()

    async def cancel_subscription(self, user_subscription_id) -> None:
        user_subscription = (
            await self.db.execute(select(UserSubscription)
                                  .where(and_(UserSubscription.id == user_subscription_id,
                                              UserSubscription.status != SubscriptionStatus.INACTIVE)))
        ).scalars().first()
        if not user_subscription:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail='User subscription not found or already inactive')
        end_of_subscription = date.today()
        await self.db.execute(update(UserSubscription)
                              .where(UserSubscription.id == user_subscription_id)
                              .values(status=SubscriptionStatus.INACTIVE,
                                      end_of_subscription=end_of_subscription))
        await self.db.commit()

    async def list_user_active_subscriptions(
            self,
            user_id: UUID,
            subscription_type_id: int | None
    ) -> Sequence[UserSubscription]:
        if subscription_type_id:
            user_subscriptions = (
                await self.db.execute(select(UserSubscription)
                                      .where(and_(UserSubscription.user_id == user_id,
                                                  UserSubscription.type_id == subscription_type_id,
                                                  UserSubscription.status == SubscriptionStatus.ACTIVE)))
            ).scalars().all()

        else:
            user_subscriptions = (
                await self.db.execute(select(UserSubscription)
                                      .where(and_(UserSubscription.user_id == user_id,
                                                  UserSubscription.status == SubscriptionStatus.ACTIVE)))
            ).scalars().all()
        return user_subscriptions

    async def mock_list_user_active_subscriptions(
            self,
            user_id: UUID,
            subscription_type_id: int | None,
    ) -> Sequence[UserSubscription]:
        user_subscriptions = [user_subscription_1, user_subscription_2]
        if subscription_type_id:
            return list(filter(lambda x: (x.type_id == subscription_type_id), user_subscriptions))
        else:
            return user_subscriptions


@lru_cache()
def get_user_subscription_service(
        db: AsyncSession = Depends(get_session),
) -> UserSubscriptionService:
    return UserSubscriptionService(db)