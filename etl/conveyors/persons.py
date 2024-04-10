from typing import Any

from conveyors.base import PostgresToElasticsearch

SQL_PERSONS = """
SELECT
   p.id,
   p.full_name,
   json_agg(
       DISTINCT jsonb_build_object(
               'id', pfw.film_work_id,
               'role', pfw.role
           )
   ) as films,
   p.modified
FROM content.person AS p
LEFT JOIN content.person_film_work AS pfw ON p.id = pfw.person_id
LEFT JOIN content.film_work AS fw ON pfw.film_work_id = fw.id
WHERE p.modified >= %s
GROUP BY p.id, p.modified
ORDER BY p.modified;
"""


SQL_FILM_PERSONS = """
SELECT
   p.id,
   p.full_name,
   json_agg(
       DISTINCT jsonb_build_object(
               'id', pfw.film_work_id,
               'role', pfw.role
           )
   ) as films,
   MAX(fw.modified) AS modified
FROM content.person AS p
LEFT JOIN content.person_film_work AS pfw ON p.id = pfw.person_id
LEFT JOIN content.film_work AS fw ON pfw.film_work_id = fw.id
GROUP BY p.id
HAVING MAX(fw.modified) >= %s
ORDER BY MAX(fw.modified);
"""


class PersonsETL(PostgresToElasticsearch):
    index_name: str = "persons"
    extract_query: str = SQL_PERSONS
    enrich_queries: dict[str, str] = {}

    @staticmethod
    def transform_item(item: dict[str, Any]) -> dict[str, Any]:
        item.pop("modified")
        return item


class FilmPersonsETL(PostgresToElasticsearch):
    index_name: str = "film_persons"
    extract_query: str = SQL_FILM_PERSONS
    enrich_queries: dict[str, str] = {}

    @staticmethod
    def transform_item(item: dict[str, Any]) -> dict[str, Any]:
        item.pop("modified")
        return item
