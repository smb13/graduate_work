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

subscription_type_1 = SubscriptionType(
    name='Премиум подписка',
    description='Годовая премиум подписка, которая включает в себя фильмы и сериалы',
    annual_price=2400,
    monthly_price=200,
    start_of_sales=date(2020,1,1),
    end_of_sales=date(3000,1,1),
    id=2
)
subscription_type_2 = SubscriptionType(
    name='Базовая подписка',
    description='Годовая базовая подписка, которая включает в себя фильмы и сериалы',
    annual_price=1200,
    monthly_price=100,
    start_of_sales=date(2020,1,1),
    end_of_sales=date(2024,1,1),
    id=1
)
subscription_type_3 = SubscriptionType(
    name='Базовая подписка NEW',
    description='Годовая базовая подписка c 2024 г, которая включает в себя фильмы и сериалы',
    annual_price=1800,
    monthly_price=150,
    start_of_sales=date(2024,1,1),
    end_of_sales=date(2024,1,1),
    id=3
)


class SubscriptionTypeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_current_subscription_types(self) -> list[SubscriptionTypeResponse]:
        today = date.today()
        result = await self.db.execute(select(SubscriptionType)
                                       .where(and_(SubscriptionType.start_of_sales <= today,
                                                   SubscriptionType.end_of_sales >= today))
                                       .order_by(SubscriptionType.name))
        subscription_types = result.scalars().all()
        return subscription_types

    async def list_all_subscription_types(self) -> list[SubscriptionTypeResponse]:
        result = await self.db.execute(select(SubscriptionType))
        subscription_types = result.scalars().all()
        return subscription_types

    async def mock_list_all_subscription_types(self) -> list[SubscriptionTypeResponse]:
        return [subscription_type_1, subscription_type_2, subscription_type_3]

    async def create_subscription_type(
            self,
            subscription_type_create: SubscriptionTypeBase
    ) -> SubscriptionTypeResponse | Exception:
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
            self, subscription_type_id: int, subscription_type_patch: SubscriptionTypeBase
    ) -> Optional[SubscriptionTypeResponse]:
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

    async def get_subscription_type_by_id(self, subscription_type_id: int) -> SubscriptionTypeResponse:
        result = await self.db.execute(select(SubscriptionType).where(SubscriptionType.id == subscription_type_id))
        return result.scalars().first()


@lru_cache()
def get_subscription_type_service(
        db: AsyncSession = Depends(get_session),
) -> SubscriptionTypeService:
    return SubscriptionTypeService(db)
