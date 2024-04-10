INDEX_MAPPINGS_MOVIES = {
    "dynamic": "strict",
    "properties": {
        "id": {
            "type": "keyword",
        },
        "title": {
            "type": "text",
            "analyzer": "ru_en",
            "fields": {
                "raw": {
                    "type": "keyword",
                },
            },
        },
        "imdb_rating": {
            "type": "float",
        },
        "description": {
            "type": "text",
            "analyzer": "ru_en",
        },
        "genre": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "id": {
                    "type": "keyword",
                },
                "name": {
                    "type": "text",
                    "analyzer": "ru_en",
                },
            },
        },
        "directors": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "id": {
                    "type": "keyword",
                },
                "name": {
                    "type": "text",
                    "analyzer": "ru_en",
                },
            },
        },
        "actors": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "id": {
                    "type": "keyword",
                },
                "name": {
                    "type": "text",
                    "analyzer": "ru_en",
                },
            },
        },
        "writers": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "id": {
                    "type": "keyword",
                },
                "name": {
                    "type": "text",
                    "analyzer": "ru_en",
                },
            },
        },
        "directors_names": {
            "type": "text",
            "analyzer": "ru_en",
        },
        "actors_names": {
            "type": "text",
            "analyzer": "ru_en",
        },
        "writers_names": {
            "type": "text",
            "analyzer": "ru_en",
        },
    },
}
