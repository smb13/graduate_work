import contextlib

from django.core.paginator import Paginator
from django.db import InternalError, OperationalError, connection, transaction
from django.utils.functional import cached_property

# Условимся, что это число превышает возможное число записей в наших таблицах
OBVIOUSLY_EXCEEDING_NUMBER = 999999999999


class RelTuplesPaginator(Paginator):
    @cached_property
    def count(self) -> int:
        """
        Returns an estimated number of objects, across all pages.
        """
        with contextlib.suppress(
            InternalError,
            OperationalError,
        ), transaction.atomic(), connection.cursor() as cursor:
            # Limit to 150 ms
            cursor.execute("SET LOCAL statement_timeout TO 200;")
            return super().count
        return OBVIOUSLY_EXCEEDING_NUMBER
