from typing import Annotated

from pydantic import AfterValidator

from core.config import settings


def is_positive(number: int) -> int:
    if number < 1:
        raise ValueError("number must be positive")
    return number


def is_within_range(number: int) -> int:
    if 1 > number or number > settings.page_size_max:
        raise ValueError(f"number must be within the range of 1-{settings.page_size_max}")
    return number


PageNumberType = Annotated[int, AfterValidator(is_positive)]
PageSizeType = Annotated[int, AfterValidator(is_within_range)]
