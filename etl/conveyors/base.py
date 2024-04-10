import datetime as dt
import itertools
import logging
from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import Any

from elasticsearch import Elasticsearch
from exceptions import ElasticError
from psycopg2._psycopg import connection
from state import State

logger = logging.getLogger(__name__)


class PostgresToElasticsearch(ABC):
    index_name: str
    extract_query: str
    enrich_queries: dict[str, str]

    def __init__(
        self,
        postgres: connection,
        elasticsearch: Elasticsearch,
        state: State,
        batch_size: int,
    ) -> None:
        self.postgres = postgres
        self.elasticsearch = elasticsearch
        self.state = state
        self.batch_size = batch_size

    @property
    def state_key(self) -> str:
        return self.index_name + "__modified"

    @property
    def modified(self) -> str:
        return self.state.get_state(self.state_key) or dt.datetime.min.isoformat()

    @modified.setter
    def modified(self, modified: str) -> None:
        self.state.set_state(self.state_key, modified)

    def extract(self) -> Generator:
        """Возвращает данные батчами по batch_size штук"""
        modified = self.modified
        logger.info(f"starting etl from {modified}")

        with self.postgres.cursor() as cur:
            cur.execute(self.extract_query, [modified])
            while True:
                dt_fetch_start = dt.datetime.now()

                data = cur.fetchmany(self.batch_size)
                if not data:
                    logger.info(f"no more changes on {modified}")
                    break

                logger.info(f"read {len(data)} items")
                yield data

                last_modified = data[-1]["modified"] or dt_fetch_start
                self.modified = last_modified.isoformat()

    def enrich(self, items_batches: Generator) -> Generator:
        """Обогащает данные каждого объекта из items_batches данными жанров и персон"""
        for items_batch in items_batches:
            item_ids = [item["id"] for item in items_batch]

            with self.postgres.cursor() as cur:
                enrich_data = dict()
                table_names = tuple(self.enrich_queries.keys())
                for table_name, query in self.enrich_queries.items():
                    cur.execute(query, [item_ids])
                    enrich_data[table_name] = dict(cur.fetchall())

                yield [
                    dict(item) | {table_name: enrich_data[table_name].get(item["id"], []) for table_name in table_names}
                    for item in items_batch
                ]

    @staticmethod
    @abstractmethod
    def transform_item(item: dict[str, Any]) -> dict[str, Any]:
        """Преобразует данные объекта в формат, подходящий для загрузки в ElasticSearch"""

    def transform(self, items_batches: Generator) -> Generator:
        """Преобразует данные в формат, подходящий для загрузки в ElasticSearch"""
        yield from ((self.transform_item(item) for item in items_batch) for items_batch in items_batches)

    def load(self, items_batches: Generator) -> None:
        """Отправляем данные в ElasticSearch"""
        for items_batch in items_batches:
            to_ids, to_zip = itertools.tee(items_batch)
            index_ids = ({"index": {"_index": self.index_name, "_id": item["id"]}} for item in to_ids)
            ziped = zip(index_ids, to_zip)
            operations = list(itertools.chain.from_iterable(ziped))
            response = self.elasticsearch.bulk(operations=operations)
            if response.body["errors"]:
                for error in response.body["items"]:
                    logger.error(
                        "{type} in bulk load {index} id {id}: {reason}".format(
                            type=error["index"]["error"]["type"],
                            index=error["index"]["_index"],
                            id=error["index"]["_id"],
                            reason=error["index"]["error"]["reason"],
                        ),
                    )
                raise ElasticError("Invalid etl conveyor")

    def etl(self) -> None:
        self.load(self.transform(self.enrich(self.extract())))
