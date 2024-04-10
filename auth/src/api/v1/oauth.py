from authlib.integrations.starlette_client import OAuth, StarletteOAuth2App
from fastapi import APIRouter, Depends, Request
from starlette.responses import RedirectResponse

from core.config import settings
from schemas.auth import TokenResponse
from services.providers.google import GoogleProvider
from services.providers.yandex import YA_ACCESS_TKN_URL, YA_API_BASE_URL, YA_AUTHORIZE_URL, YandexProvider

router = APIRouter()

oauth = OAuth()


oauth.register(
    name="yandex",
    client_id=settings.yandex_client_id,
    client_secret=settings.yandex_client_secret,
    access_token_url=YA_ACCESS_TKN_URL,
    access_token_params=None,
    authorize_url=YA_AUTHORIZE_URL,
    authorize_params=None,
    api_base_url=YA_API_BASE_URL,
    client_kwargs={
        "scope": "login:email login:info login:avatar",
        "force_confirm": "yes",
    },
)


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


@router.get("/authorize/yandex")
async def login_via_yandex(request: Request) -> RedirectResponse:
    redirect_uri = request.url_for("auth_via_yandex")
    return await oauth.yandex.authorize_redirect(
        request,
        redirect_uri,
        scope="login:email login:info login:avatar",
        force_confirm="yes",
    )


@router.get(path="/verification_code/yandex")
async def auth_via_yandex(
    request: Request,
    provider_service: YandexProvider = Depends(YandexProvider.get_provider_service),
) -> TokenResponse:
    return await provider_service.get_auth_provider(request)


@router.get("/authorize/google")
async def login_via_google(request: Request) -> RedirectResponse:
    google: StarletteOAuth2App = oauth.google

    redirect_uri = request.url_for("auth_via_google")
    return await google.authorize_redirect(
        request,
        redirect_uri,
        scope="openid profile email",
        prompt="consent",
        access_type="offline",
    )


@router.get("/verification_code/google")
async def auth_via_google(
    request: Request,
    provider_service: GoogleProvider = Depends(GoogleProvider.get_provider_service),
) -> TokenResponse:
    return await provider_service.get_auth_provider(request)
