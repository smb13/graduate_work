from typing import Any

from conveyors.base import PostgresToElasticsearch

SQL_FILM_WORK = """
SELECT fw.id,
       fw.rating,
       fw.title,
       fw.description,
       fw.type,
       fw.modified
FROM content.film_work as fw
WHERE fw.modified >= %s
ORDER BY fw.modified, fw.id;
"""

SQL_GENRES = """
SELECT gfw.film_work_id,
       json_agg(
           DISTINCT jsonb_build_object(
                   'id', g.id,
                   'name', g.name
               )
       )
FROM content.genre_film_work as gfw
LEFT JOIN content.genre as g
    ON gfw.genre_id = g.id
WHERE gfw.film_work_id::text = ANY(%s)
GROUP BY gfw.film_work_id
"""

SQL_PERSONS = """
SELECT pfw.film_work_id,
       json_agg(
           DISTINCT jsonb_build_object(
                   'role', pfw.role,
                   'id', p.id,
                   'name', p.full_name
               )
       )
FROM content.person_film_work as pfw
LEFT JOIN content.person as p
ON pfw.person_id = p.id
WHERE pfw.film_work_id::text = ANY(%s)
GROUP BY pfw.film_work_id;
"""


class MoviesETL(PostgresToElasticsearch):
    index_name: str = "movies"
    extract_query: str = SQL_FILM_WORK
    enrich_queries: dict[str, str] = {
        "genres": SQL_GENRES,
        "persons": SQL_PERSONS,
    }

    @staticmethod
    def transform_item(item: dict[str, Any]) -> dict[str, Any]:
        transformed_item = {
            "id": item["id"],
            "imdb_rating": item["rating"],
            "genre": item["genres"],
            "title": item["title"],
            "description": item["description"],
            "directors_names": [],
            "actors_names": [],
            "writers_names": [],
            "directors": [],
            "actors": [],
            "writers": [],
        }
        for person in item["persons"]:
            transformed_item[person["role"] + "s_names"].append(person["name"])
            transformed_item[person["role"] + "s"].append({"id": person["id"], "name": person["name"]})

        return transformed_item
