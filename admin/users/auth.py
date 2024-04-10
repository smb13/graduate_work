import http
import logging
import uuid
from collections.abc import Callable

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.db.migrations.operations.base import Operation

import jwt
import requests

User = get_user_model()


class CustomBackend(BaseBackend):
    @staticmethod
    def _request_external_auth(
        method: Callable,
        url: str,
        resp_status: int = http.HTTPStatus.OK,
        headers: dict | None = None,
        data: dict | None = None,
        json: dict | None = None,
    ) -> dict | None:
        """
        Функция для отправки запросов в стороний auth сервис.
        """
        response: requests.Response = method(url=url, headers=headers, data=data, json=json)
        if not response and response.status_code != resp_status:
            return None
        return response.json()

    @staticmethod
    def __get_bearer_token(request: WSGIRequest) -> str | None:
        """
        Извлекает токен Bearer из заголовка запроса.
        """
        auth = request.headers.get("authorization", "")
        if auth.startswith("Bearer "):
            return auth[7:]
        return None

    @staticmethod
    def __decode_access_token(access_token: str | None) -> dict | None:
        """
        Декодирует токен и извлекает из него информацию по пользователю.
        """
        if access_token:
            try:
                return jwt.decode(access_token, key=settings.JWT_ACCESS_TOKEN_SECRET_KEY, algorithms=["HS256"])
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                return None
        return None

    @staticmethod
    def get_user(user_id: uuid.UUID) -> Operation | None:
        """Переопределение функции получения пользователя."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, request: WSGIRequest, username: str = None, password: str = None) -> Operation | None:
        """
        Аутентифицирует пользователя и создает его в Django, если его нет в БД.
        """
        url_login = f"{settings.SERVICE_AUTH_API_BASE_PATH}/auth/token"
        payload_login = {"username": username, "password": password}

        access_token = self.__get_bearer_token(request)

        if not access_token:
            response_login = self._request_external_auth(
                requests.post,
                url=url_login,
                data=payload_login,
                resp_status=http.HTTPStatus.OK,
            )
            if not response_login:
                raise PermissionDenied

            logging.warning(f"{response_login=}")
            access_token = response_login.get("access_token")

        payload = self.__decode_access_token(access_token)

        url_user_info = f"{settings.SERVICE_AUTH_API_BASE_PATH}/account/details"
        user_info = self._request_external_auth(
            requests.get,
            url=url_user_info,
            resp_status=http.HTTPStatus.OK,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_info:
            try:
                user, _ = User.objects.get_or_create(id=user_info.get("id"))
                user.login = user_info.get("login")
                user.first_name = user_info.get("first_name")
                user.last_name = user_info.get("last_name")
                if payload:
                    roles = payload.get("roles")
                    if roles:
                        user.is_admin = "admin" in roles
                else:
                    user.is_admin = False
                user.is_active = True
                user.save()
            except Exception as exc:
                logging.exception(f"Except {repr(exc)}")

                return None

        return user
