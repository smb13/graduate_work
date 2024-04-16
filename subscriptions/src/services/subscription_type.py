from datetime import date
from functools import lru_cache, wraps
from http import HTTPStatus
from typing import Optional
from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from psycopg.errors import UniqueViolation, ForeignKeyViolation
from sqlalchemy import delete, select, update, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session

from models.subscription import SubscriptionType
from schemas.subscription_type import SubscriptionTypeResponse, SubscriptionTypeBase


def check_access(allow_permission: str):
    def inner(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            user_role_service = kwargs.get('user_role_service')
            if not await user_role_service.is_superuser():
                await user_role_service.check_access(allow_permission)
            return await function(*args, **kwargs)
        return wrapper
    return inner


class SubscriptionTypeService:
    def __init__(self, db: AsyncSession, jwt: AuthJWT):
        self.db = db
        self.jwt = jwt

    async def list_subscription_types(self, on_date: date) -> list[SubscriptionTypeResponse]:
        await self.jwt.jwt_required()
        if on_date:
            result = await self.db.execute(select(SubscriptionType)
                                           .where(and_(SubscriptionType.start_of_sales <= on_date,
                                                       SubscriptionType.end_of_sales >= on_date))
                                           .order_by(SubscriptionType.name))
        else:
            result = await self.db.execute(select(SubscriptionType))
        subscription_types = result.scalars().all()
        return subscription_types

    async def create_subscription_type(
            self,
            subscription_type_create: SubscriptionTypeBase
    ) -> SubscriptionTypeResponse | Exception:
        await self.jwt.jwt_required()
        subscription_type = SubscriptionType(**jsonable_encoder(subscription_type_create))
        self.db.add(subscription_type)
        try:
            await self.db.commit()
        except IntegrityError as e:
            await self.db.rollback()
            if isinstance(e.orig, UniqueViolation):
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Subscription type already exists')
            raise e
        await self.db.refresh(subscription_type)
        return subscription_type

    async def patch_subscription_type(
            self, subscription_type_id: UUID, subscription_type_patch: SubscriptionTypeBase
    ) -> Optional[SubscriptionTypeResponse]:
        await self.jwt.jwt_required()
        values = jsonable_encoder(subscription_type_patch)
        try:
            await self.db.execute(
                update(SubscriptionType).where(SubscriptionType.id == subscription_type_id)
                .values(**values)
            )
        except IntegrityError as e:
            await self.db.rollback()
            if isinstance(e.orig, UniqueViolation):
                if 'subscription_type_name_key' in str(e):
                    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                        detail='Another subscription type has the same name')
            raise e
        await self.db.commit()
        result = await self.db.execute(select(SubscriptionType).where(SubscriptionType.id == subscription_type_id))
        return result.scalars().first()

    async def get_subscription_type_by_id(self, subscription_type_id: UUID) -> SubscriptionTypeResponse:
        result = await self.db.execute(select(SubscriptionType).where(SubscriptionType.id == subscription_type_id))
        return result.scalars().first()


@lru_cache()
def get_subscription_type_service(
        db: AsyncSession = Depends(get_session),
        jwt: AuthJWT = Depends()
) -> SubscriptionTypeService:
    return SubscriptionTypeService(db, jwt)
