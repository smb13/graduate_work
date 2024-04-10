import logging
from logging import config as logging_config

from src.core.config import settings

LEVEL_STRING = logging.getLevelName(int(settings.app.log_level))

LOGGING_SETTINGS = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple_fmt": {
            "format": settings.app.log_format,
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
        },
    },
    "handlers": {
        "simple_console_handler": {
            "level": LEVEL_STRING,
            "class": "logging.StreamHandler",
            "formatter": "simple_fmt",
        },
    },
    "root": {
        "level": LEVEL_STRING,
        "handlers": ["simple_console_handler"],
        "formatter": "simple_fmt",
    },
}


def logging_init():
    """Инициализация логгера."""
    if int(settings.app.log_level) < logging.INFO:
        LOGGING_SETTINGS["root"]["level"] = logging.DEBUG
    logging_config.dictConfig(LOGGING_SETTINGS)


logging_init()
logger = logging.getLogger(__name__)
