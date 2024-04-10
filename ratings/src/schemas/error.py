from collections.abc import Callable

import orjson
from pydantic import BaseModel


def orjson_dumps(value: object, *, default: Callable) -> str:
    return orjson.dumps(value, default=default).decode()


class HttpExceptionModel(BaseModel):
    detail: str
