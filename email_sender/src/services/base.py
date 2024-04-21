import abc
from functools import lru_cache
from typing import Any, Self

from async_fastapi_jwt_auth import AuthJWT  # noqa
from fastapi import Depends
from src.core.config import settings
from src.core.logger import logger
from src.db.abstract import AbstractAccessor
from src.db.sendgrid.get_sendgrid import get_sendgrid
from src.schemas.email import EmailNotification


class AbstractService(metaclass=abc.ABCMeta):
    def __init__(self, jwt: AuthJWT, sendgrid_client: AbstractAccessor) -> None:
        self.jwt = jwt
        self.sendgrid_client = sendgrid_client

    @abc.abstractmethod
    def send(self, *args, **kwargs) -> Any:
        pass

    @staticmethod
    @abc.abstractmethod
    def check_to_resend(notice: EmailNotification) -> EmailNotification | None:
        if notice.retries == settings.email.max_retries_to_send:
            logger.debug("Закончилось кол-во попыток для отправки email")
            # TODO - можно добавить отправку в очередь, для повторной отправки через какое-то время
            return None
        notice.retries += 1
        logger.debug("Повторная попытка отправки email")
        return notice

    @classmethod
    @lru_cache
    @abc.abstractmethod
    def get_service(cls, jwt: AuthJWT = Depends()) -> Self:
        """
        Метод-инициализатор для Dependency Injections.
        """
        return cls(jwt, get_sendgrid())
