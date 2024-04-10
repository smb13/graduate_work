import logging
import os

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from core.config import settings

# Инициализация Sentry SDK если есть env SENTRY_DSN
if SENTRY_DSN := os.getenv("SENTRY_DSN"):
    sentry_logging = LoggingIntegration(
        level=logging.WARNING,  # Захват логов уровня WARNING и выше
        event_level=logging.ERROR,  # Отправка событий в Sentry начиная с уровня ERROR
    )

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[sentry_logging],
        traces_sample_rate=float(os.getenv("TRACES_SAMPLE_RATE", 0.01)),
        profiles_sample_rate=float(os.getenv("PROFILES_SAMPLE_RATE", 0.01)),
        attach_stacktrace=True,  # прикрепляет стек вызовов к логам для ошибок, не являющихся исключениями
        send_default_pii=True,  # данные, позволяющие идентифицировать запись
    )

# Базовая конфигурация логгирования
logger = logging.getLogger("worker_logger")
loglevel = logging.DEBUG if settings.debug else logging.INFO
logger.setLevel(loglevel)

# Настойки логов для вывода в консоль
terminal = logging.StreamHandler()
format_terminal = logging.Formatter(settings.log_format, datefmt="[%Y-%m-%d %H:%M:%S %z]")
terminal.setFormatter(format_terminal)
logger.addHandler(terminal)
