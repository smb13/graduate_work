from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from core.enums import ActionEnum
from models import User
from schemas.user import ChangePassword, UserCreate, UserResponse, UserUpdate
from services.auth import check_permissions
from services.roles import RolesService, get_roles_service
from services.users import UsersService, get_users_service
from utils.responses import invalid_credentials

router = APIRouter()


@router.get(
    "/details",
    response_model=UserResponse,
    summary="Get detail information about user",
)
async def get_user(
    current_user: Annotated[User, Depends(check_permissions(ActionEnum.me_read))],
) -> UserResponse:
    return current_user


@router.put(
    "/details",
    summary="Update detail information for user",
)
async def update_user(
    user: UserUpdate,
    current_user: Annotated[User, Depends(check_permissions(ActionEnum.me_update))],
    user_service: UsersService = Depends(get_users_service),
) -> None:
    """Update information for user."""

    await user_service.update(current_user, user)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=HTTPStatus.CREATED,
    summary="Register the user",
)
async def register_user(
    user_create: UserCreate,
    users_service: UsersService = Depends(get_users_service),
    roles_service: RolesService = Depends(get_roles_service),
) -> UserResponse:
    """Register new user."""

    user = await users_service.retrieve(username=user_create.login)
    if user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User with this login already exists")

    user = await users_service.create(user_create)
    user_role = await roles_service.get_or_create_user_role()
    if user_role:
        await roles_service.add_roles_to_user(user, [user_role.id])

    return user


@router.post(
    "/password",
    summary="Change the user password",
)
async def change_password(
    passwords: ChangePassword,
    current_user: Annotated[User, Depends(check_permissions(ActionEnum.me_change_password))],
    user_service: UsersService = Depends(get_users_service),
) -> None:
    """Change password in the authenticated user."""

    if not await user_service.change_password(current_user, passwords):
        raise invalid_credentials
