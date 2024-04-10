from abc import ABCMeta, abstractmethod


class BaseAccessor(metaclass=ABCMeta):
    """Абстрактный класс для управления соединением."""

    @abstractmethod
    def __enter__(self):
        """Запросить соединение."""

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Завершить и закрыть соединение."""


class BadResponse(Exception):
    """Неподходящий ответ"""

    def __init__(self, *args, **kwargs):
        pass
