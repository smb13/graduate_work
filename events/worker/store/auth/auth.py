from http import HTTPStatus

import backoff
import requests
from store.base import BadResponse
from store.security import jwt_getter

from core.config import settings
from core.logger import logger


class AuthRequest:
    def __init__(self):
        self.url = f"http://{settings.auth_host}:{settings.auth_port}" + f"{settings.auth_get_users_endpoint}/"
        self.headers = jwt_getter.get_headers()

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        logger=logger,
        max_tries=settings.external_api_backoff_max_tries,
    )
    def get_user_details(self, user_id: str) -> [str, str, str]:
        # убрать моковое поведение для теста
        return "user@yandex.ru", "Вася", "Пупкин"
        response = requests.get(url=self.url + user_id, headers=self.headers)
        if response.status_code == HTTPStatus.OK:
            return response.content["login"], response.content["first_name"], response.content["last_name"]
        elif response.status_code == HTTPStatus.UNAUTHORIZED | HTTPStatus.FORBIDDEN:
            self.headers = jwt_getter.get_new_headers()
            raise requests.exceptions.RequestException
        else:
            raise BadResponse("response.status_code")
