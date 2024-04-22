import abc
from typing import Any

import sendgrid


class AbstractAccessor(metaclass=abc.ABCMeta):
    """Абстрактный интерфейс для работы с Sendgrid."""

    @property
    @abc.abstractmethod
    def connect(self, *args, **kwargs) -> sendgrid.SendGridAPIClient:
        """Получить клиент."""
        ...

    @abc.abstractmethod
    def setup(self, *args, **kwargs) -> Any:
        """Настройка сервиса."""
        ...
