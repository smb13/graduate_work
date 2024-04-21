from functools import lru_cache
from functools import lru_cache
from http import HTTPStatus
from typing import Optional, Any, Sequence
from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from psycopg.errors import UniqueViolation
from sqlalchemy import select, update, Row, RowMapping
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.subscription import UserSubscription, SubscriptionType, SubscriptionStatus
from schemas.user_subscription import UserSubscriptionResponse, UserSubscriptionBase
from services.billing import BillingService, get_billing_service


class MeUserSubscriptionService:
    def __init__(self, db: AsyncSession, billing_service: BillingService):
        self.db = db
        self.billing_service = billing_service

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
        subscription_type = (
            await self.db.execute(select(SubscriptionType).where(SubscriptionType.id == subscription_type_id))
        ).scalars().first()
        if not subscription_type:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Subscription type not found')
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
        payment_url = await self.billing_service.new_payment(
            subscription_id=str(user_subscription.id),
            amount=subscription_type.annual_price
        )
        user_subscription.status = SubscriptionStatus.AWAITING_PAYMENTS
        await self.db.execute(update(UserSubscription)
                              .where(UserSubscription.id == user_subscription.id)
                              .values(status=SubscriptionStatus.AWAITING_PAYMENTS))
        await self.db.commit()
        return payment_url

    async def cancel_user_subscription(
            self,
            user: dict,
            user_subscription_id: UUID,
    ) -> Optional[UserSubscriptionResponse]:
        user_id = UUID(user['sub'])
        values = jsonable_encoder()
        try:
            await self.db.execute(
                update(UserSubscription).where(UserSubscription.id == user_subscription_id)
                .values(**values)
            )
        except IntegrityError as e:
            await self.db.rollback()
            if isinstance(e.orig, UniqueViolation):
                if 'user_subscription_name_key' in str(e):
                    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                        detail='Another role has the same name')
            raise e
        await self.db.commit()
        result = await self.db.execute(select(UserSubscription).where(UserSubscription.id == user_subscription_id))
        return result.scalars().first()

    async def get_user_subscription_by_id(self, user_subscription_id: UUID) -> UserSubscription:
        result = await self.db.execute(select(UserSubscription).where(UserSubscription.id == user_subscription_id))
        return result.scalars().first()

    async def activate_subscription(self, user_subscription_id):
        pass

    async def cancel_subscription(self, user_subscription_id):
        pass


@lru_cache()
def get_me_user_subscription_service(
        db: AsyncSession = Depends(get_session),
        billing_service: BillingService = Depends(get_billing_service)
) -> MeUserSubscriptionService:
    return MeUserSubscriptionService(db, billing_service)
