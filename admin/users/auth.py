import http
import uuid
from collections.abc import Callable
from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.core.validators import validate_email
from django.db.migrations.operations.base import Operation

import jwt
import requests

if TYPE_CHECKING:
    from users.models import User as UserModel


User: "type[UserModel]" = get_user_model()


class CustomBackend(BaseBackend):
    @staticmethod
    def _request_external_auth(
        method: Callable,
        url: str,
        headers: dict | None = None,
        data: dict | None = None,
    ) -> dict | None:
        """Отправка запросов в Auth сервис."""
        response: requests.Response = method(url=url, headers=headers, data=data)
        if not response and response.status_code != http.HTTPStatus.OK:
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
        validate_email(username)

        login_url = f"{settings.SERVICE_AUTH_API_BASE_PATH}/auth/token"
        payload_login = {"username": username, "password": password}

        access_token = self.__get_bearer_token(request)
        refresh_token = None

        if not access_token:
            oauth_tokens = self._request_external_auth(
                requests.post,
                url=login_url,
                data=payload_login,
            )
            if not oauth_tokens:
                raise PermissionDenied

            access_token = oauth_tokens.get("access_token")
            refresh_token = oauth_tokens.get("refresh_token")
            if not access_token:
                raise PermissionDenied

        payload = self.__decode_access_token(access_token)
        if not payload:
            raise PermissionDenied

        user_info_url = f"{settings.SERVICE_AUTH_API_BASE_PATH}/account/details"
        user_info = self._request_external_auth(
            requests.get,
            url=user_info_url,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_info:
            user, _ = User.objects.update_or_create(
                id=user_info.get("id"),
                defaults=dict(
                    login=user_info.get("login"),
                    first_name=user_info.get("first_name"),
                    last_name=user_info.get("last_name"),
                ),
            )

            user.is_admin = "admin" in payload.get("roles", [])
            user.is_active = True
            user.access_token = access_token
            user.refresh_token = refresh_token
            user.save()

            return user

        return None
