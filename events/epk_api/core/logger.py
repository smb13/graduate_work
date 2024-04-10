import os

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

# noinspection SpellCheckingInspection
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DEFAULT_HANDLERS = ["console"]

# Инициализация Sentry SDK если есть env SENTRY_DSN
if SENTRY_DSN := os.getenv("SENTRY_DSN"):
    # Используем и FastApiIntegration и StarletteIntegration, тк они тесно связаны
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        enable_tracing=True,
        environment=os.getenv("SENTRY_ENVIRONMENT"),  # Позволяет идентифицировать конкретный инстанс если их несколько
        integrations=[
            StarletteIntegration(
                transaction_style="url",  # если `endpoint` - будет отображать название самого метода
            ),
            FastApiIntegration(
                transaction_style="url",  # если `endpoint` - будет отображать название самого метода
            ),
        ],
        traces_sample_rate=float(os.getenv("TRACES_SAMPLE_RATE", 0.01)),
        profiles_sample_rate=float(os.getenv("PROFILES_SAMPLE_RATE", 0.01)),
        attach_stacktrace=True,  # прикрепляет стек вызовов к логам для ошибок, не являющихся исключениями
        send_default_pii=True,  # данные, позволяющие идентифицировать запись
    )

# В логгере настраивается логгирование gunicorn-сервера.
# Про логирование в Python можно прочитать в документации
# https://docs.python.org/3/howto/logging.html
# https://docs.python.org/3/howto/logging-cookbook.html

# noinspection SpellCheckingInspection
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": LOG_FORMAT,
        },
        "default": {
            "format": "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter",
        },
        "access": {
            "format": "%(message)s",
            "class": "logging.Formatter",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {
            "handlers": LOG_DEFAULT_HANDLERS,
            "level": "INFO",
        },
        "gunicorn.error": {
            "level": "INFO",
        },
        "gunicorn.access": {
            "handlers": ["access"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "level": "INFO",
        "formatter": "verbose",
        "handlers": LOG_DEFAULT_HANDLERS,
    },
}
