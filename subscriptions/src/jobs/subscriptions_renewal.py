import asyncio
from datetime import date
from typing import cast

from aiohttp.client_exceptions import ClientError
from fastapi import HTTPException
from sqlalchemy import and_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import billing_settings
from db.postgres import get_session
from main import lifespan
from models import UserSubscription
from models.subscription import SubscriptionStatus, SubscriptionType
from services.billing import BillingService, get_billing_service


@lifespan(None)
async def subscriptions_renewal() -> None:
    async for db in get_session():
        cast("AsyncSession", db)
        today = date.today()
        today_plus_3 = date(year=today.year, month=today.month, day=today.day + 3)
        subscription_types = (await db.execute(select(SubscriptionType))).scalars().all()
        annual_prices = {type_.id: type_.annual_price for type_ in subscription_types}
        subscriptions_to_renew_query = select(UserSubscription).where(
            and_(
                UserSubscription.end_of_subscription >= today,
                UserSubscription.end_of_subscription <= today_plus_3,
                UserSubscription.end_of_subscription == SubscriptionStatus.ACTIVE,
            ),
        )
        subscriptions = await db.scalars(subscriptions_to_renew_query)
        billing_service: BillingService = get_billing_service()
        for subscription in subscriptions.yield_per(100):
            try:
                await billing_service.call_to_billing(
                    uri=billing_settings.renew_uri,
                    payment_method_id=subscription.payment_method_id,
                    amount=annual_prices.get(subscription.type_id),
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
