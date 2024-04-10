from collections.abc import Sequence
from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination.cursor import CursorPage

from core.enums import ActionEnum
from models import User
from schemas.role_permissions import RoleResponse
from schemas.user import UserCreate, UserResponse
from services.auth import check_permissions
from services.roles import RolesService, get_roles_service
from services.users import UsersService, get_users_service

router = APIRouter()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Retrieve a user",
)
async def user_details(
    user_id: UUID,
    current_user: Annotated[User, Depends(check_permissions(ActionEnum.user_read))],
    users_service: UsersService = Depends(get_users_service),
) -> UserResponse:
    """Retrieve an item with all the information."""

    user: User | None = await users_service.retrieve(user_id=user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

    return user


@router.get(
    "/{user_id}/roles",
    response_model=list[RoleResponse],
    summary="Show user roles",
)
async def user_roles(
    user_id: UUID,
    current_user: Annotated[User, Depends(check_permissions(ActionEnum.role_binding_read))],
    users_service: UsersService = Depends(get_users_service),
    roles_service: RolesService = Depends(get_roles_service),
) -> Sequence[RoleResponse]:
    """List user roles"""

    user: User | None = await users_service.retrieve(user_id=user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="user not found")

    return await roles_service.get_roles_by_user(user=user)


@router.put(
    "/{user_id}/add_roles",
    response_model=list[RoleResponse],
    summary="Add roles to user",
)
async def add_roles(
    user_id: UUID,
    role_ids: list[UUID],
    current_user: Annotated[User, Depends(check_permissions(ActionEnum.role_binding_create))],
    users_service: UsersService = Depends(get_users_service),
    roles_service: RolesService = Depends(get_roles_service),
) -> Sequence[RoleResponse]:
    """Add user Roles"""

    user: User | None = await users_service.retrieve(user_id=user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="user not found")

    return await roles_service.add_roles_to_user(user=user, role_ids=role_ids)


@router.delete(
    "/{user_id}/remove_roles",
    response_model=list[RoleResponse],
    summary="Remove roles to user",
)
async def remove_roles(
    user_id: UUID,
    role_ids: list[UUID],
    current_user: Annotated[User, Depends(check_permissions(ActionEnum.role_binding_delete))],
    users_service: UsersService = Depends(get_users_service),
    roles_service: RolesService = Depends(get_roles_service),
) -> Sequence[RoleResponse]:
    """Remove user Roles"""

    user: User | None = await users_service.retrieve(user_id=user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="user not found")

    return await roles_service.remove_roles_from_user(user=user, role_ids=role_ids)


@router.post(
    "",
    response_model=UserResponse,
    status_code=HTTPStatus.CREATED,
    summary="Create the new user",
)
async def create_user(
    user_create: UserCreate,
    current_user: Annotated[User, Depends(check_permissions(ActionEnum.user_create))],
    users_service: UsersService = Depends(get_users_service),
) -> UserResponse:
    """Create the new user."""

    return await users_service.create(user_create)


@router.get(
    "",
    response_model=CursorPage[UserResponse],
    summary="Show the list of users",
)
async def users_list(
    current_user: Annotated[User, Depends(check_permissions(ActionEnum.user_read))],
    users_service: UsersService = Depends(get_users_service),
) -> CursorPage[UserResponse]:
    """List users with brief information."""

    return await users_service.list()
