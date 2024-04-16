from datetime import date, timedelta
from uuid import UUID

from pydantic import Field, BaseModel


class UserSubscriptionBase(BaseModel):
    type_id: UUID = Field(
        title='UUID типа подписки',
        examples=[UUID('7fb9f6e0-f13d-4409-b924-1563b4a8774c'), ],
    )
    payment_method_id: UUID = Field(
        title='UUID автоплатежа',
        examples=[UUID('4439e956-d1bf-41ad-8a9a-41fac7b8d0c8'), ],
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
