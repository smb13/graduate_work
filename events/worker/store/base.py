from abc import ABCMeta, abstractmethod


class BaseAccessor(metaclass=ABCMeta):
    """Абстрактный класс для управления соединением."""

    @abstractmethod
    def __enter__(self) -> None:
        """Запросить соединение."""

    @abstractmethod
    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: Exception) -> None:
        """Завершить и закрыть соединение."""


class BadResponse(Exception):
    """Неподходящий ответ"""

    def __init__(self, *args, **kwargs) -> None:
        pass
