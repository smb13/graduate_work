from datetime import date

from pydantic import BaseModel, Field


class SubscriptionTypeBase(BaseModel):
    name: str = Field(
        title="Название подписки",
        examples=["Базовая подписка"],
    )
    description: str = Field(
        default="",
        title="Описание подписки",
        examples=["Годовая базовая подписка, которая включает в себя фильмы и сериалы"],
    )
    annual_price: int = Field(
        title="Годовая стоимость подписки в рублях",
        examples=[1200],
    )
    monthly_price: int = Field(
        title="Месячная стоимость подписки в рублях",
        examples=[100],
    )
    start_of_sales: date = Field(
        default=date.today(),
        title="Дата начала продаж подписки",
        examples=[date(year=2020, month=1, day=1)],
    )
    end_of_sales: date = Field(
        default=date(year=3000, month=1, day=1),
        title="Дата окончания продаж подписки",
        examples=[date(year=3000, month=1, day=1)],
    )


class SubscriptionTypeResponse(SubscriptionTypeBase):
    id: int = Field(
        title="Id сохраненной подписки",
        examples=[1002],
    )

    class Config:
        from_attributes = True
