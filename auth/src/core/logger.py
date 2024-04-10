import logging
import os
import sys

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

log = logging.getLogger("authlib")
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)

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

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DEFAULT_HANDLERS = ["console"]

# В логгере настраивается логгирование uvicorn-сервера.
# Про логирование в Python можно прочитать в документации
# https://docs.python.org/3/howto/logging.html
# https://docs.python.org/3/howto/logging-cookbook.html

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": LOG_FORMAT,
        },
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": "%(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s",
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
        "uvicorn.error": {
            "level": "INFO",
        },
        "uvicorn.access": {
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
