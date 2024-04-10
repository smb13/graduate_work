from abc import ABC, abstractmethod
from typing import Any

from elasticsearch import NotFoundError
from opentelemetry.trace import get_tracer

from core.types import DataOptType, ModelType, NestedQuery, PageNumberType, PageSizeType, RequestData


class BaseDatabase(ABC):
    def __init__(
        self,
        storage: Any,
        index: str,
        model: type[ModelType],
        sort_fields: tuple[str, ...] = (),
        search_fields: tuple[str, ...] = (),
    ) -> None:
        self.storage = storage
        self.index = index
        self.model = model
        self.sort_fields = sort_fields
        self.search_fields = search_fields

    @abstractmethod
    async def get(self, request_data: RequestData) -> DataOptType:
        """Получить данные из базы данных"""


tracer = get_tracer(__name__)


class ElasticDatabase(BaseDatabase):
    async def get(self, request_data: RequestData) -> DataOptType:
        """Get data from the Elasticsearch"""
        with tracer.start_as_current_span("elasticsearch-get"):
            if request_data.id:
                try:
                    doc = await self.storage.get(index=self.index, id=str(request_data.id))
                except NotFoundError:
                    return None
                return self.model(**doc.body["_source"])

            docs = await self.storage.search(
                index=self.index,
                query=self.make_query_dls(request_data.query)
                or self.make_query_dls_nested(
                    request_data.nested_query,
                ),
                sort=self.make_elastic_sort_string(request_data.sort),
                from_=self.get_item_from(request_data.page_size, request_data.page_number),
                size=request_data.page_size,
            )
            return [self.model(**doc["_source"]) for doc in docs.body["hits"]["hits"]]

    def make_elastic_sort_string(self, sort_string: str | None) -> str | None:
        if sort_string in self.sort_fields:
            direction = "desc" if sort_string[0] == "-" else "asc"
            return sort_string.strip("-") + ":" + direction
        return None

    @staticmethod
    def get_item_from(page_size: PageSizeType | None, page_number: PageNumberType | None) -> int | None:
        """Calcs a "from" offset based on the page size and number"""
        if page_size and page_number:
            return page_size * (page_number - 1)
        return None

    def make_query_dls(self, query_string: str | None) -> dict[str, Any] | None:
        if not query_string:
            return None
        return {
            "multi_match": {
                "query": query_string,
                "fuzziness": "auto",
                "fields": self.search_fields,
            },
        }

    @staticmethod
    def make_query_dls_nested(nested_query: NestedQuery) -> dict[str, Any] | None:
        if not nested_query or not nested_query.path or not nested_query.field or not nested_query.query_string:
            return None

        return {
            "nested": {
                "path": nested_query.path,
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    f"{nested_query.path}.{nested_query.field}": nested_query.query_string,
                                },
                            },
                        ],
                    },
                },
            },
        }
