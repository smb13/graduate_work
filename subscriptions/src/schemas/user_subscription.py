from datetime import date, timedelta
from uuid import UUID

from pydantic import Field, BaseModel

from models.subscription import SubscriptionStatus


class UserSubscriptionBase(BaseModel):
    type_id: int = Field(
        title='Id типа подписки',
        examples=[3, ],
    )
    payment_method_id: UUID | None = Field(
        title='UUID автоплатежа',
        examples=[UUID('4439e956-d1bf-41ad-8a9a-41fac7b8d0c8'), ],
    )
    status: SubscriptionStatus = Field(
        title='Статус подписки',
        examples=[SubscriptionStatus.NEW, ],
    )
    start_of_subscription: date | None = Field(
        default=date.today(),
        title='Дата начала подписки',
        examples=[date.today(),],
    )
    end_of_subscription: date | None = Field(
        default=date.today() + timedelta(days=365),
        title='Дата окончания подписки',
        examples=[date.today() + timedelta(days=365),],
    )


class UserSubscriptionResponse(UserSubscriptionBase):
    id: UUID = Field(
        title='UUID сохраненной подписки',
        examples=[UUID('61d07e94-2967-4c91-8e5c-5e558aa8b221'),],
    )

    class Config:
        from_attributes = True


class UrlResponse(BaseModel):
    confirmation_url: str = Field(
        title='ссылка на оплату',
        examples=['https://yoomoney.ru/api-pages/v2/payment-confirm/epl?orderId=2419a771-000f-5000-9000-1edaf29243f2',],
    )
