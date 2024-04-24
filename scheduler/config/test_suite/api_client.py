import json
import random
import string
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.test import APIClient

from mixer.backend.django import mixer


class DRFClient(APIClient):
    def __init__(
        self,
        user: str = None,
        god_mode: bool = False,
        anon: bool = False,
        auth: str = "token",
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.god_mode = god_mode
        self.password, self.user, self.employee = None, None, None

        if not anon:
            self.password = "".join([random.choice(string.hexdigits) for _ in range(6)])
            self.user, self.employee = self.auth(user, god_mode, auth)

    def auth(self, user: User = None, god_mode: bool = False, auth: str = "token") -> tuple:
        user: User = user or self._create_user(god_mode=god_mode)
        employee = None

        if auth == "token":
            employee = user.self_employee_set.first()
            token = getattr(user, "auth_token", None) or Token.objects.create(user=user)
            self.credentials(HTTP_AUTHORIZATION=f"Token {token.key}", HTTP_X_CLIENT="testing")

        elif auth == "basic":
            self.login(username=user.email, password=self.password)

        return user, employee

    def _create_user(self, *, god_mode: bool = False) -> Any:
        user_opts = {"is_staff": True, "is_superuser": True} if god_mode else {}
        user = mixer.blend(get_user_model(), username=mixer.RANDOM, **user_opts)
        user.set_password(self.password)
        user.save()
        return user

    @staticmethod
    def _create_employee(user: Any) -> Any:
        # noqa - уточнить модель HQPartyChoices   party=HQPartyChoices.AGENCY,
        hq = mixer.blend(
            "outsource.Headquarter",
            code=mixer.RANDOM,
        )
        agency = mixer.blend("outsource.Agency", headquater=hq, code=mixer.RANDOM, address="")
        return mixer.blend("employees.AgencyEmployee", user=user, agency=agency, headquarter=hq)

    def logout(self) -> None:
        self.credentials()
        super().logout()

    def get(self, *args, **kwargs) -> dict[str, Any] | None:
        return self._api_call("get", kwargs.get("expected_status_code", 200), *args, **kwargs)

    def post(self, *args, **kwargs) -> dict[str, Any] | None:
        return self._api_call("post", kwargs.get("expected_status_code", 201), *args, **kwargs)

    def put(self, *args, **kwargs) -> dict[str, Any] | None:
        return self._api_call("put", kwargs.get("expected_status_code", 200), *args, **kwargs)

    def patch(self, *args, **kwargs) -> dict[str, Any] | None:
        return self._api_call("patch", kwargs.get("expected_status_code", 200), *args, **kwargs)

    def delete(self, *args, **kwargs) -> dict[str, Any] | None:
        return self._api_call("delete", kwargs.get("expected_status_code", 204), *args, **kwargs)

    def _api_call(self, method: str, expected: str, *args, **kwargs) -> dict[str, Any] | None:
        kwargs["format"] = kwargs.get("format", "json")  # by default submit all data in JSON
        as_response = kwargs.pop("as_response", False)

        method = getattr(super(), method)
        response: Response = method(*args, **kwargs)

        if as_response:
            return response

        content = self._decode(response)

        # content нужен, чтобы получить текст ошибки в with pytest.raises
        assert response.status_code == expected, content

        return content

    @staticmethod
    def _decode(response: Any) -> dict[str, Any] | None:
        if not response.content:
            return None

        content = response.content.decode("utf-8", errors="ignore")
        if "application/json" in response.headers["content-type"]:
            return json.loads(content)
        return content
