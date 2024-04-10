from typing import Any

from orjson import dumps


def make_cache_key(cache_prefix, request_data: dict["str", Any]) -> str:
    return cache_prefix + "_" + dumps(request_data).decode("UTF-8")
