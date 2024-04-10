from http import HTTPStatus

from fastapi import HTTPException, Request

from core.config import settings
from schemas.auth import TokenResponse
from schemas.user import UserCreate
from services.auth import AuthService, get_auth_service
from services.providers.base_oauth import AbstractOAuth, oauth
from services.roles import RolesService, get_roles_service
from services.users import UsersService, get_users_service
from utils.generate_data import generate_password

USER_INFO_YA_URL = "https://login.yandex.ru/info?format=json"


oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    client_kwargs={
        "scope": "openid email profile",
        "prompt": "consent",
    },
    authorize_params={"access_type": "offline"},
)


class GoogleProvider(AbstractOAuth):
    async def __register(self, user_data: dict) -> TokenResponse:
        """
        Registering a new user or returning an existing one.
        """
        users_service: UsersService = get_users_service(alchemy=self.session)
        roles_service: RolesService = get_roles_service(alchemy=self.session)
        auth_service: AuthService = get_auth_service(alchemy=self.session)

        users_role = await roles_service.get_or_create_user_role()

        user_create = UserCreate(
            login=user_data.get("email"),
            password=generate_password(length=20),
            first_name=user_data.get("given_name"),
            last_name=user_data.get("family_name"),
        )
        user = await users_service.retrieve(username=user_create.login)

        if not user:
            user = await users_service.create(user_create)

            await roles_service.add_roles_to_user(
                user=user,
                role_ids=users_role.id,
            )

        role_codes = await roles_service.get_role_codes(user)
        access_token = await auth_service.make_access_token(user, role_codes)
        refresh_token = await auth_service.make_refresh_token(user)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def get_auth_provider(self, request: Request) -> TokenResponse:
        """
        Request to receive user data in the Yandex service.
        """
        token = await oauth.google.authorize_access_token(request)
        if not token:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Token not found")

        return await self.__register(user_data=dict(token).get("userinfo", {}))
