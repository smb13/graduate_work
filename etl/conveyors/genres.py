from typing import Any

from conveyors.base import PostgresToElasticsearch

SQL_GENRES = """
SELECT fw.id,
       fw.name,
       fw.modified
FROM content.genre as fw
WHERE fw.modified >= %s
ORDER BY fw.modified, fw.id;
"""


class GenresETL(PostgresToElasticsearch):
    index_name: str = "genres"
    extract_query: str = SQL_GENRES
    enrich_queries: dict[str, str] = {}

    @staticmethod
    def transform_item(item: dict[str, Any]) -> dict[str, Any]:
        item.pop("modified")
        return item
