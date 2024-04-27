from collections.abc import Sequence
from datetime import date
from functools import lru_cache
from http import HTTPStatus
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import and_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.subscription import SubscriptionStatus, UserSubscription
from schemas.user_subscription import PaymentMethodId


class UserSubscriptionService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def activate_subscription(self, user_subscription_id: UUID, payment_method_id: PaymentMethodId) -> None:
        user_subscription = (
            (
                await self.db.execute(
                    select(UserSubscription).where(
                        and_(
                            UserSubscription.id == user_subscription_id,
                            or_(
                                UserSubscription.status == SubscriptionStatus.AWAITING_PAYMENT,
                                UserSubscription.status == SubscriptionStatus.AWAITING_RENEWAL,
                            ),
                        ),
                    ),
                )
            )
            .scalars()
            .first()
        )
        if not user_subscription:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="User subscription not found or does not have appropriate status",
            )
        today = date.today()
        end_of_subscription = date(year=today.year + 1, month=today.month, day=today.day)
        if not user_subscription.start_of_subscription:
            await self.db.execute(
                update(UserSubscription)
                .where(UserSubscription.id == user_subscription_id)
                .values(
                    status=SubscriptionStatus.ACTIVE,
                    start_of_subscription=today,
                    end_of_subscription=end_of_subscription,
                    payment_method_id=payment_method_id.payment_method_id,
                ),
            )
        else:
            await self.db.execute(
                update(UserSubscription)
                .where(UserSubscription.id == user_subscription_id)
                .values(
                    status=SubscriptionStatus.ACTIVE,
                    end_of_subscription=end_of_subscription,
                    payment_method_id=payment_method_id.payment_method_id,
                ),
            )
        await self.db.commit()

    async def cancel_subscription(self, user_subscription_id: UUID) -> None:
        user_subscription = (
            (
                await self.db.execute(
                    select(UserSubscription).where(
                        and_(
                            UserSubscription.id == user_subscription_id,
                            UserSubscription.status != SubscriptionStatus.INACTIVE,
                        ),
                    ),
                )
            )
            .scalars()
            .first()
        )
        if not user_subscription:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="User subscription not found or already inactive",
            )
        end_of_subscription = date.today()
        await self.db.execute(
            update(UserSubscription)
            .where(UserSubscription.id == user_subscription_id)
            .values(
                status=SubscriptionStatus.INACTIVE,
                end_of_subscription=end_of_subscription,
            ),
        )
        await self.db.commit()

    async def list_user_active_subscriptions(
        self,
        user_id: UUID,
        subscription_type_id: int | None,
    ) -> Sequence[UserSubscription]:
        if subscription_type_id:
            return (
                (
                    await self.db.execute(
                        select(UserSubscription).where(
                            and_(
                                UserSubscription.user_id == user_id,
                                UserSubscription.type_id == subscription_type_id,
                                UserSubscription.status == SubscriptionStatus.ACTIVE,
                            ),
                        ),
                    )
                )
                .scalars()
                .all()
            )

        else:
            return (
                (
                    await self.db.execute(
                        select(UserSubscription).where(
                            and_(
                                UserSubscription.user_id == user_id,
                                UserSubscription.status == SubscriptionStatus.ACTIVE,
                            ),
                        ),
                    )
                )
                .scalars()
                .all()
            )


@lru_cache
def get_user_subscription_service(
    db: AsyncSession = Depends(get_session),
) -> UserSubscriptionService:
    return UserSubscriptionService(db)
