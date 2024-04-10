from typing import Annotated, TypeAlias
from uuid import UUID

from pydantic import AfterValidator, BaseModel

from core.config import settings


def is_positive(number: int) -> int:
    if number < 1:
        raise Exception("number must be positive")
    return number


def is_within_range(number: int) -> int:
    if 1 > number or number > settings.page_size_max:
        raise Exception(f"number must be within the range of 1-{settings.page_size_max}")
    return number


PageNumberType = Annotated[int, AfterValidator(is_positive)]
PageSizeType = Annotated[int, AfterValidator(is_within_range)]


class NestedQuery(BaseModel):
    path: str
    field: str
    query_string: str


class RequestData(BaseModel):
    id: UUID | None = None
    sort: str | None = None
    page_number: PageNumberType | None = None
    page_size: PageSizeType | None = None
    query: str | None = None
    nested_query: NestedQuery | None = None


DataType: TypeAlias = BaseModel | list[BaseModel]
DataOptType: TypeAlias = DataType | None
ModelType: TypeAlias = BaseModel
ModelListType: TypeAlias = list[BaseModel]
