from uuid import uuid4

from fastapi_jwt_auth2 import AuthJWT

from core.config import authjwt_settings


@AuthJWT.load_config
def get_config():
    return authjwt_settings


class JWTGetter:
    def __init__(self):
        self.headers = self.get_new_headers()

    def get_headers(self) -> dict:
        return self.headers

    def get_new_headers(self) -> dict:
        """
        В целях выполнения учебного проекта, создается токен на фейкового пользователя. В продакшене метод должен быть
        заменен на получение токена через сервис auth c авторизацией через сервисную учетную запись.
        """
        jwt = AuthJWT()
        access_token = jwt.create_access_token(
            subject=str(uuid4()),
            user_claims={"sub": "username:user@yandex.ru", "roles": ["admin"]},
        )
        return {"Authorization": "Bearer " + access_token.decode()}


jwt_getter = JWTGetter()
