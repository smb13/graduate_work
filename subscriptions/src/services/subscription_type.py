from datetime import date
from functools import lru_cache
from http import HTTPStatus

from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from psycopg.errors import UniqueViolation
from sqlalchemy import and_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.subscription import SubscriptionType
from schemas.subscription_type import SubscriptionTypeBase, SubscriptionTypeResponse


class SubscriptionTypeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_current_subscription_types(self) -> list[SubscriptionTypeResponse]:
        today = date.today()
        result = await self.db.execute(
            select(SubscriptionType)
            .where(
                and_(
                    SubscriptionType.start_of_sales <= today,
                    SubscriptionType.end_of_sales >= today,
                ),
            )
            .order_by(SubscriptionType.name),
        )
        subscription_types = result.scalars().all()
        return subscription_types

    async def list_all_subscription_types(self) -> list[SubscriptionTypeResponse]:
        result = await self.db.execute(select(SubscriptionType))
        subscription_types = result.scalars().all()
        return subscription_types

    async def create_subscription_type(
        self,
        subscription_type_create: SubscriptionTypeBase,
    ) -> SubscriptionTypeResponse | Exception:
        subscription_type = SubscriptionType(**jsonable_encoder(subscription_type_create))
        self.db.add(subscription_type)
        try:
            await self.db.commit()
        except IntegrityError as e:
            await self.db.rollback()
            if isinstance(e.orig, UniqueViolation):
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Subscription type already exists")
            raise e
        await self.db.refresh(subscription_type)
        return subscription_type

    async def patch_subscription_type(
        self,
        subscription_type_id: int,
        subscription_type_patch: SubscriptionTypeBase,
    ) -> SubscriptionTypeResponse | None:
        values = jsonable_encoder(subscription_type_patch)
        try:
            await self.db.execute(
                update(SubscriptionType).where(SubscriptionType.id == subscription_type_id).values(**values),
            )
        except IntegrityError as e:
            await self.db.rollback()
            if isinstance(e.orig, UniqueViolation):
                if "subscription_type_name_key" in str(e):
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST,
                        detail="Another subscription type has the same name",
                    )
            raise e
        await self.db.commit()
        result = await self.db.execute(select(SubscriptionType).where(SubscriptionType.id == subscription_type_id))
        return result.scalars().first()

    async def get_subscription_type_by_id(self, subscription_type_id: int) -> SubscriptionTypeResponse:
        result = await self.db.execute(select(SubscriptionType).where(SubscriptionType.id == subscription_type_id))
        return result.scalars().first()


@lru_cache
def get_subscription_type_service(
    db: AsyncSession = Depends(get_session),
) -> SubscriptionTypeService:
    return SubscriptionTypeService(db)
