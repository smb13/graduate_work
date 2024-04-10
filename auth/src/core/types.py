from typing import Annotated, TypeAlias
from uuid import UUID

from email_validator import validate_email
from fastapi import Query
from pydantic import AfterValidator, BaseModel

from core.config import settings

PageNumberQueryType = Annotated[int, Query(description="Pagination page number", ge=1)]
PageSizeQueryType = Annotated[int, Query(description="Pagination page size", ge=1, le=settings.page_size_max)]


def is_valid_email(email: str) -> str:
    """Validate string as an email"""
    emailinfo = validate_email(email, check_deliverability=False)
    return emailinfo.normalized


def is_positive(number: int) -> int:
    if number < 1:
        raise Exception("number must be positive")
    return number


def is_within_range(number: int) -> int:
    if 1 > number or number > settings.page_size_max:
        raise Exception(f"number must be within the range of 1-{settings.page_size_max}")
    return number


EmailType = Annotated[str, AfterValidator(is_valid_email)]
PageNumberType = Annotated[int, AfterValidator(is_positive)]
PageSizeType = Annotated[int, AfterValidator(is_within_range)]


class RequestData(BaseModel):
    id: UUID | None = None
    sort: str | None = None
    page_number: PageNumberType | None = None
    page_size: PageSizeType | None = None
    query: str | None = None


DataType: TypeAlias = BaseModel | list[BaseModel]
DataOptType: TypeAlias = DataType | None
ModelType: TypeAlias = BaseModel
ModelListType: TypeAlias = list[BaseModel]
