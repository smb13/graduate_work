from datetime import date
from functools import lru_cache
from http import HTTPStatus
from typing import Sequence
from uuid import UUID

from fastapi import Depends, HTTPException
from psycopg.errors import UniqueViolation
from sqlalchemy import select, update, or_, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import billing_settings
from db.postgres import get_session
from models.subscription import UserSubscription, SubscriptionType, SubscriptionStatus


class UserSubscriptionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_user_subscriptions(self, user: dict) -> Sequence[UserSubscription]:
        user_id = UUID(user['sub'])
        result = await self.db.execute(select(UserSubscription).where(UserSubscription.user_id == user_id))
        user_subscriptions = result.scalars().all()
        return user_subscriptions

    async def create_user_subscription(
            self,
            user: dict,
            subscription_type_id: int
    ) -> str | Exception:
        user_id = UUID(user['sub'])
        today = date.today()
        subscription_type = (
            await self.db.execute(select(SubscriptionType)
                                  .where(SubscriptionType.id == subscription_type_id,
                                         SubscriptionType.start_of_sales <= today,
                                         SubscriptionType.end_of_sales >= today
                                         )
                                  )
        ).scalars().first()
        if not subscription_type:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Subscription type not found or subscription is not active')
        exist_active_subscriptions = (
            await self.db.execute(select(UserSubscription)
                                  .where(UserSubscription.type_id == subscription_type_id,
                                         UserSubscription.user_id == user_id,
                                         UserSubscription.status != SubscriptionStatus.INACTIVE,
                                         UserSubscription.status != SubscriptionStatus.NEW))
        ).scalars().all()
        if exist_active_subscriptions:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='User already has this type subscription')
        exist_new_subscriptions = (
            await self.db.execute(select(UserSubscription)
                                  .where(UserSubscription.type_id == subscription_type_id,
                                         UserSubscription.user_id == user_id,
                                         UserSubscription.status == SubscriptionStatus.NEW))
        ).scalars().first()
        if not exist_new_subscriptions:
            user_subscription = UserSubscription(
                type_id=subscription_type_id,
                user_id=user_id,
                payment_method_id=None,
                status=SubscriptionStatus.NEW,
                start_of_subscription=None,
                end_of_subscription=None
            )
            self.db.add(user_subscription)
            try:
                await self.db.commit()
            except IntegrityError as e:
                await self.db.rollback()
                if isinstance(e.orig, UniqueViolation):
                    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='User subscription already exists')
                raise e
            await self.db.refresh(user_subscription)
        else:
            user_subscription = exist_new_subscriptions
        payment_url = await self.billing_service.call_to_billing(
            uri=billing_settings.new_uri,
            user_id=str(user_id),
            subscription_id=str(user_subscription.id),
            amount=subscription_type.annual_price,
            description=f'Оплата за подписку {subscription_type.name}',
            currency='RUB'
        )
        await self.db.execute(update(UserSubscription)
                              .where(UserSubscription.id == user_subscription.id)
                              .values(status=SubscriptionStatus.AWAITING_PAYMENT))
        await self.db.commit()
        return payment_url

    async def cancel_user_subscription(
            self,
            user: dict,
            user_subscription_id: UUID,
    ) -> str | Exception:
        user_id = UUID(user['sub'])
        active_user_subscription = (
            await self.db.execute(select(UserSubscription)
                                  .where(UserSubscription.id == user_subscription_id,
                                         UserSubscription.user_id == user_id,
                                         UserSubscription.status == SubscriptionStatus.ACTIVE
                                         )
                                  )
        ).scalars().first()
        if not active_user_subscription:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail='User subscription does not exist or not active')

        subscription_type = (
            await self.db.execute(select(SubscriptionType)
                                  .where(SubscriptionType.id == active_user_subscription.type_id))
        ).scalars().first()
        if not subscription_type:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail='Subscription type not found')

        days_in_week = 7
        days_in_month = 30
        today = date.today()
        date_of_last_renewal = date(
            year=active_user_subscription.end_of_subscription.year - 1,
            month=active_user_subscription.end_of_subscription.month,
            day=active_user_subscription.end_of_subscription.day)
        if (today - date_of_last_renewal).days < days_in_week:
            refund_amount = subscription_type.annual_price
        elif (today - active_user_subscription.end_of_subscription) < days_in_month:
            refund_amount = 0
        else:
            refund_amount = ((today - date_of_last_renewal).days // days_in_month) * subscription_type.monthly_price

        if refund_amount == 0:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Refund amount equal to zero')

        respond = await self.billing_service.call_to_billing(
            uri=billing_settings.refund_uri,
            payment_method_id=str(active_user_subscription.payment_method_id),
            subscription_id=str(active_user_subscription.id),
            amount=refund_amount,
        )

        return respond

    async def activate_subscription(self, user_subscription_id):
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
                                          end_of_subscription=end_of_subscription))
        else:
            await self.db.execute(update(UserSubscription)
                                  .where(UserSubscription.id == user_subscription_id)
                                  .values(status=SubscriptionStatus.ACTIVE,
                                          end_of_subscription=end_of_subscription))
        await self.db.commit()

    async def cancel_subscription(self, user_subscription_id):
        user_subscription = (
            await self.db.execute(select(UserSubscription)
                                  .where(UserSubscription.id == user_subscription_id,
                                         UserSubscription.status == SubscriptionStatus.AWAITING_PAYMENT))
        ).scalars().first()
        if not user_subscription:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail='User subscription not found or does not have awaiting_payments status')
        today = date.today()
        end_of_subscription = date(year=today.year + 1, month=today.month, day=today.day)
        if not user_subscription.start_of_subscription:
            await self.db.execute(update(UserSubscription)
                                  .where(UserSubscription.id == user_subscription_id)
                                  .values(status=SubscriptionStatus.ACTIVE,
                                          start_of_subscription=today,
                                          end_of_subscription=end_of_subscription))
        else:
            await self.db.execute(update(UserSubscription)
                                  .where(UserSubscription.id == user_subscription_id)
                                  .values(status=SubscriptionStatus.ACTIVE,
                                          end_of_subscription=end_of_subscription))
        await self.db.commit()

    async def list_user_active_subscriptions(self, user_id, subscription_type_id):
        pass


@lru_cache()
def get_user_subscription_service(
        db: AsyncSession = Depends(get_session),
) -> UserSubscriptionService:
    return UserSubscriptionService(db)
