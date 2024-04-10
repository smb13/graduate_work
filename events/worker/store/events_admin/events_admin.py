from http import HTTPStatus

import backoff
import requests
from store.base import BadResponse
from store.security import jwt_getter

from core.config import settings
from core.logger import logger


class EventsAdminRequest:
    def __init__(self):
        self.get_template_url = (
            f"http://{settings.events_admin_host}:{settings.events_admin_port}"
            + f"{settings.events_admin_get_template_endpoint}/"
        )
        self.get_subscribers_url = (
            f"http://{settings.events_admin_host}:{settings.events_admin_port}"
            + f"{settings.events_admin_subscribers_endpoint}/"
        )
        self.headers = jwt_getter.get_headers()
        self.default_template = """
        Привет {{ first_name }} {{ last_name }}!

            {{ text }}

        C наилучшими пожеланиями, твой сайт!
        """

    def get_default_template(self):
        return self.default_template

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        logger=logger,
        max_tries=settings.external_api_backoff_max_tries,
    )
    def get_template(self, template_id: str) -> str:
        response = requests.get(url=self.get_template_url + template_id, headers=self.headers)
        if response.status_code == HTTPStatus.OK:
            return response.content.decode()
        elif response.status_code == HTTPStatus.UNAUTHORIZED | HTTPStatus.FORBIDDEN:
            self.headers = jwt_getter.get_new_headers()
            raise requests.exceptions.RequestException
        else:
            raise BadResponse("response.status_code")

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        logger=logger,
        max_tries=settings.external_api_backoff_max_tries,
    )
    def get_subscribers(self) -> list[str]:
        # убрать моковое поведение для теста
        return ["1ee9882a-5f12-4988-8c22-5e5c04601ad1"]
        response = requests.get(url=self.get_subscribers_url, headers=self.headers)
        if response.status_code == HTTPStatus.OK:
            user_ids = response.content.json()
            return user_ids
        elif response.status_code == HTTPStatus.UNAUTHORIZED | HTTPStatus.FORBIDDEN:
            self.headers = jwt_getter.get_new_headers()
            raise requests.exceptions.RequestException
        else:
            raise BadResponse("response.status_code")
