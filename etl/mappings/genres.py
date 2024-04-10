INDEX_MAPPINGS_GENRES = {
    "dynamic": "strict",
    "properties": {
        "id": {"type": "keyword"},
        "name": {
            "type": "text",
            "analyzer": "ru_en",
            "fields": {
                "raw": {
                    "type": "keyword",
                },
            },
        },
    },
}
