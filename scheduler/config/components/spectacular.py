SPECTACULAR_SETTINGS = {
    "SERVE_PERMISSIONS": [],
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_SETTINGS": {
        "persistAuthorization": True,
        "filter": True,
        "displayRequestDuration": True,
    },
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",
    ],
}
