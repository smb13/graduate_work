from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination.cursor import CursorPage

from core.enums import ActionEnum
from models import User
from models.access_log import AccessLogEntry
from schemas.access_log import AccessLogScheme
from schemas.auth import TokenResponse
from services.auth import AuthService, check_permissions, get_auth_service
from services.roles import RolesService, get_roles_service
from services.users import UsersService, get_users_service

router = APIRouter()


@router.post(
    "/token",
    summary="Authenticate to the service",
)
async def authenticate(
    background_tasks: BackgroundTasks,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_agent: Annotated[str, Header()] = "",
    origin: Annotated[str, Header()] = "",
    x_forwarded_for: Annotated[str, Header()] = "",
    users_service: UsersService = Depends(get_users_service),
    auth_service: AuthService = Depends(get_auth_service),
    roles_service: RolesService = Depends(get_roles_service),
) -> TokenResponse:
    """User authentication to the service."""

    user = await users_service.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid login or password")

    role_codes = await roles_service.get_role_codes(user)
    access_token = await auth_service.make_access_token(user, role_codes)
    refresh_token = await auth_service.make_refresh_token(user)

    background_tasks.add_task(
        auth_service.add_access_log,
        user,
        x_forwarded_for=x_forwarded_for,
        user_agent=user_agent,
        origin=origin,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.get(
    "/access-log",
    response_model=CursorPage[AccessLogScheme],
    summary="View the access log for the authentication service.",
)
async def access_log(
    current_user: Annotated[User, Depends(check_permissions(ActionEnum.me_access_log))],
    auth_service: AuthService = Depends(get_auth_service),
) -> CursorPage[AccessLogEntry]:
    """View the history of visits to the service from devices."""

    return await auth_service.get_access_log(current_user)


@router.post(
    "/revoke",
    summary="Revoke the old token and generate a new token",
)
async def revoke_token(
    current_user: Annotated[User, Depends(check_permissions(ActionEnum.me_update))],
    auth_service: AuthService = Depends(get_auth_service),
    users_service: UsersService = Depends(get_users_service),
    refresh_token: str | None = None,
    access_token: str | None = None,
) -> None:
    """Generate new access and refresh tokens."""

    invalid_token_error = HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    if access_token:
        access_token_payload = await auth_service.check_access_token_signature(access_token)
        user = await users_service.retrieve(username=access_token_payload and access_token_payload.username)
        is_valid = await auth_service.check_access_token(access_token_payload, access_token)

        if not access_token_payload or not is_valid or not user or user.id != current_user.id:
            raise invalid_token_error

        await auth_service.revoke_access_token(access_token)

    if refresh_token:
        refresh_token_payload = await auth_service.check_refresh_token_signature(refresh_token)
        user = await users_service.retrieve(username=refresh_token_payload and refresh_token_payload.username)
        is_valid = await auth_service.check_refresh_token_payload(refresh_token_payload, user and user.id)

        if not refresh_token_payload or not is_valid or not user or user.id != current_user.id:
            raise invalid_token_error

        await auth_service.revoke_refresh_token(refresh_token_payload and refresh_token_payload.jwt_id)


@router.post(
    "/refresh",
    summary="Refresh the token",
)
async def refresh(
    refresh_token: str,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UsersService = Depends(get_users_service),
    roles_service: RolesService = Depends(get_roles_service),
) -> TokenResponse:
    """Refresh token."""

    payload = await auth_service.check_refresh_token_signature(refresh_token)
    user = await user_service.retrieve(username=payload and payload.username)
    is_valid = await auth_service.check_refresh_token_payload(payload, user and user.id)

    if not payload or not is_valid or not user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    role_codes = await roles_service.get_role_codes(user)
    new_access_token = await auth_service.make_access_token(user, role_codes)
    new_refresh_token = await auth_service.make_refresh_token(user)

    background_tasks.add_task(auth_service.revoke_refresh_token, payload.jwt_id)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )
