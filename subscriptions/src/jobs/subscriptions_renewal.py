import asyncio
from datetime import date
from typing import cast

from aiohttp.client_exceptions import ClientError
from fastapi import HTTPException
from httpx import AsyncClient
from sqlalchemy import and_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.http import get_client
from db.postgres import get_session
from main import lifespan
from models import UserSubscription
from models.subscription import SubscriptionStatus, SubscriptionType
from services.billing import BillingService, get_billing_service


@lifespan(None)
async def subscriptions_renewal() -> None:
    client: AsyncClient = await get_client()

    async for db in get_session():
        cast("AsyncSession", db)
        today = date.today()
        today_plus_3 = date(year=today.year, month=today.month, day=today.day + 3)
        subscription_types = (await db.execute(select(SubscriptionType))).scalars().all()
        sub_types_info = {
            type_.id: {"annual_price": type_.annual_price, "name": type_.name} for type_ in subscription_types
        }
        subscriptions_to_renew_query = select(UserSubscription).where(
            and_(
                UserSubscription.end_of_subscription >= today,
                UserSubscription.end_of_subscription <= today_plus_3,
                UserSubscription.status == SubscriptionStatus.ACTIVE,
            ),
        )
        subscriptions = await db.scalars(subscriptions_to_renew_query)
        billing_service: BillingService = get_billing_service(client=client)
        for subscription in subscriptions.yield_per(100):
            try:
                sub_type_info = sub_types_info.get(subscription.type_id)
                if sub_type_info:
                    await billing_service.payments_renew(
                        user_id=str(subscription.user_id),
                        subscription_id=str(subscription.id),
                        payment_method_id=str(subscription.payment_method_id),
                        amount=sub_type_info.get("annual_price"),
                        description=f"Оплата за продление подписки {sub_type_info.get('name')}",
                        currency="RUB",
                    )
                    await db.execute(
                        update(UserSubscription)
                        .where(and_(UserSubscription.id == subscription.id))
                        .values(status=SubscriptionStatus.AWAITING_RENEWAL),
                    )
                    await db.commit()
            except (ClientError, HTTPException, IntegrityError):
                continue


async def subscriptions_renewal_job() -> None:
    """Process of the subscriptions' renewal."""
    loop = asyncio.get_event_loop()
    await loop.create_task(subscriptions_renewal())
