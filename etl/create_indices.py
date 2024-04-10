import logging
import sys
from typing import Any

import backoff
from config import settings
from elasticsearch import BadRequestError, Elasticsearch, NotFoundError
from mappings.genres import INDEX_MAPPINGS_GENRES
from mappings.movies import INDEX_MAPPINGS_MOVIES
from mappings.persons import INDEX_MAPPINGS_PERSONS

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

logger = logging.getLogger(__name__)


INDEX_SETTINGS = {
    "refresh_interval": "1s",
    "analysis": {
        "filter": {
            "english_stop": {
                "type": "stop",
                "stopwords": "_english_",
            },
            "english_stemmer": {
                "type": "stemmer",
                "language": "english",
            },
            "english_possessive_stemmer": {
                "type": "stemmer",
                "language": "possessive_english",
            },
            "russian_stop": {
                "type": "stop",
                "stopwords": "_russian_",
            },
            "russian_stemmer": {
                "type": "stemmer",
                "language": "russian",
            },
        },
        "analyzer": {
            "ru_en": {
                "tokenizer": "standard",
                "filter": [
                    "lowercase",
                    "english_stop",
                    "english_stemmer",
                    "english_possessive_stemmer",
                    "russian_stop",
                    "russian_stemmer",
                ],
            },
        },
    },
}


@backoff.on_exception(backoff.expo, (BadRequestError, NotFoundError), max_time=60)
def get_or_create_index(client: Elasticsearch, index_name: str, mapping: dict[str, Any]) -> dict[str, Any]:
    try:
        index = client.indices.get(index=index_name)
    except NotFoundError:
        client.indices.create(
            index=index_name,
            settings=INDEX_SETTINGS,
            mappings=mapping,
        )
        logger.info("Index created")
        raise
    else:
        logger.info("Index exists")
        return index


def main() -> None:
    client = Elasticsearch(
        [{"host": "elastic", "port": settings.elastic_port, "scheme": "http"}],
    )

    get_or_create_index(client, "movies", INDEX_MAPPINGS_MOVIES)
    get_or_create_index(client, "genres", INDEX_MAPPINGS_GENRES)
    get_or_create_index(client, "persons", INDEX_MAPPINGS_PERSONS)


if __name__ == "__main__":
    main()
