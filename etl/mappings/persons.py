INDEX_MAPPINGS_PERSONS = {
    "dynamic": "strict",
    "properties": {
        "id": {
            "type": "keyword",
        },
        "full_name": {
            "type": "text",
            "analyzer": "ru_en",
            "fields": {
                "raw": {
                    "type": "keyword",
                },
            },
        },
        "films": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "id": {
                    "type": "keyword",
                },
                "role": {
                    "type": "keyword",
                },
            },
        },
    },
}
