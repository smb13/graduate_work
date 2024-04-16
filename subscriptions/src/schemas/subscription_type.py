from datetime import date
from uuid import UUID

from pydantic import Field, BaseModel


class SubscriptionTypeBase(BaseModel):
    name: str | None = Field(
        title='Название подписки',
        examples=["Базовая подписка",],
    )
    description: str | None = Field(
        default='',
        title='Описание подписки',
        examples=["Годовая базовая подписка, которая включает в себя фильмы и сериалы",],
    )
    annual_price: int | None = Field(
        title='Годовая стоимость подписки в рублях',
        examples=[1200,],
    )
    monthly_price: int | None = Field(
        title='Месячная стоимость подписки в рублях',
        examples=[100,],
    )
    start_of_sales: date | None = Field(
        title='Дата начала продаж подписки',
        examples=[date(year=2020, month=1, day=1),],
    )
    end_of_sales: date | None = Field(
        default=date(year=3000, month=1, day=1),
        title='Дата окончания продаж подписки',
        examples=[date(year=3000, month=1, day=1),],
    )


class SubscriptionTypeResponse(SubscriptionTypeBase):
    id: UUID = Field(
        title='UUID сохраненной подписки',
        examples=[UUID('61d07e94-2967-4c91-8e5c-5e558aa8b221'),],
    )

    class Config:
        from_attributes = True
