from config.components.base import env

JWT_ACCESS_TOKEN_SECRET_KEY = env("JWT_ACCESS_TOKEN_SECRET_KEY", default="movies_token_secret")


SIMPLE_JWT = {
    # "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),  # noqa: E800
    # "REFRESH_TOKEN_LIFETIME": timedelta(days=1),  # noqa: E800
    # "ROTATE_REFRESH_TOKENS": False,  # noqa: E800
    # "BLACKLIST_AFTER_ROTATION": False,  # noqa: E800
    # "UPDATE_LAST_LOGIN": False,  # noqa: E800
    "ALGORITHM": "HS256",
    "SIGNING_KEY": JWT_ACCESS_TOKEN_SECRET_KEY,
    "VERIFYING_KEY": "",
    # "AUDIENCE": None,  # noqa: E800
    # "ISSUER": None,  # noqa: E800
    # "JSON_ENCODER": None,  # noqa: E800
    # "JWK_URL": None,  # noqa: E800
    # "LEEWAY": 0,  # noqa: E800
    "AUTH_HEADER_TYPES": ("Bearer", "JWT"),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "username",
    "USER_ID_CLAIM": "sub",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": None,
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": None,
    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
}
