import logging
from logging import config as logging_config
from typing import Any

from src.core.config import settings

LEVEL_STRING = logging.getLevelName(int(settings.app.log_level))

LOGGING_SETTINGS: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": settings.app.log_format, "datefmt": "%Y-%m-%dT%H:%M:%S%Z"},
    },
    "handlers": {
        "simple_console_handler": {
            "level": LEVEL_STRING,
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "simple": {
            "disabled": False,
            "handlers": ["simple_console_handler"],
            "formatter": "verbose",
            "level": LEVEL_STRING,
            "propagate": False,
        },
        "uvicorn": {
            "level": LEVEL_STRING,
            "handlers": ["simple_console_handler"],
            "formatter": "verbose",
            "propagate": False,
        },
    },
    "root": {
        "disabled": True,
        "level": logging.getLevelName(logging.INFO),
        "formatter": "verbose",
        "handlers": ["simple_console_handler"],
    },
}


def logging_init() -> None:
    """Инициализация логгера."""
    if int(settings.app.log_level) < logging.INFO:
        LOGGING_SETTINGS["root"]["level"] = logging.DEBUG
    logging_config.dictConfig(LOGGING_SETTINGS)


logger = logging.getLogger(__name__)
