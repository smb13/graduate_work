from functools import lru_cache
from functools import lru_cache
from http import HTTPStatus
from typing import Optional
from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from psycopg.errors import UniqueViolation
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.subscription import UserSubscription
from schemas.user_subscription import UserSubscriptionResponse, UserSubscriptionBase


class UserSubscriptionService:
    def __init__(self, db: AsyncSession, jwt: AuthJWT):
        self.db = db
        self.jwt = jwt

    async def list_user_subscriptions(self) -> list[UserSubscriptionResponse]:
        await self.jwt.jwt_required()
        user_id = (await self.jwt.get_raw_jwt())["sub"]
        result = await self.db.execute(select(UserSubscription).where(UserSubscription.user_id == user_id))
        user_subscriptions = result.scalars().all()
        return user_subscriptions

    async def create_user_subscription(
            self,
            user_subscription_create: UserSubscriptionBase
    ) -> UserSubscriptionResponse | Exception:
        await self.jwt.jwt_required()
        user_subscription = UserSubscription(**jsonable_encoder(user_subscription_create))
        self.db.add(user_subscription)
        try:
            await self.db.commit()
        except IntegrityError as e:
            await self.db.rollback()
            if isinstance(e.orig, UniqueViolation):
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='User subscription already exists')
            raise e
        await self.db.refresh(user_subscription)
        return user_subscription

    async def patch_user_subscription(
            self, user_subscription_id: UUID, user_subscription_patch: UserSubscriptionBase
    ) -> Optional[UserSubscriptionResponse]:
        await self.jwt.jwt_required()
        values = jsonable_encoder(user_subscription_patch)
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
def get_user_subscription_service(
        db: AsyncSession = Depends(get_session),
        jwt: AuthJWT = Depends()
) -> UserSubscriptionService:
    return UserSubscriptionService(db, jwt)
