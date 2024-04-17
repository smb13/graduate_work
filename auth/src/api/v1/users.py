from collections.abc import Sequence
from http import HTTPStatus
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


user_not_found_exc = HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Retrieve a user",
    dependencies=[Depends(check_permissions(ActionEnum.user_read))],
)
async def user_details(
    user_id: UUID,
    users_service: UsersService = Depends(get_users_service),
) -> UserResponse:
    """Retrieve an item with all the information."""

    user: User | None = await users_service.retrieve(user_id=user_id)
    if not user:
        raise user_not_found_exc

    return user


@router.get(
    "/{user_id}/roles",
    response_model=list[RoleResponse],
    summary="Show user roles",
    dependencies=[Depends(check_permissions(ActionEnum.role_binding_read))],
)
async def user_roles(
    user_id: UUID,
    users_service: UsersService = Depends(get_users_service),
    roles_service: RolesService = Depends(get_roles_service),
) -> Sequence[RoleResponse]:
    """List user roles"""

    user: User | None = await users_service.retrieve(user_id=user_id)
    if not user:
        raise user_not_found_exc

    return await roles_service.get_roles_by_user(user=user)


@router.put(
    "/{user_id}/add_roles",
    response_model=list[RoleResponse],
    summary="Add roles to user",
    dependencies=[Depends(check_permissions(ActionEnum.role_binding_create))],
)
async def add_roles(
    user_id: UUID,
    role_ids: list[UUID],
    users_service: UsersService = Depends(get_users_service),
    roles_service: RolesService = Depends(get_roles_service),
) -> Sequence[RoleResponse]:
    """Add user Roles"""

    user: User | None = await users_service.retrieve(user_id=user_id)
    if not user:
        raise user_not_found_exc

    return await roles_service.add_roles_to_user(user=user, role_ids=role_ids)


@router.delete(
    "/{user_id}/remove_roles",
    response_model=list[RoleResponse],
    summary="Remove roles to user",
    dependencies=[Depends(check_permissions(ActionEnum.role_binding_delete))],
)
async def remove_roles(
    user_id: UUID,
    role_ids: list[UUID],
    users_service: UsersService = Depends(get_users_service),
    roles_service: RolesService = Depends(get_roles_service),
) -> Sequence[RoleResponse]:
    """Remove user Roles"""

    user: User | None = await users_service.retrieve(user_id=user_id)
    if not user:
        raise user_not_found_exc

    return await roles_service.remove_roles_from_user(user=user, role_ids=role_ids)


@router.post(
    "",
    response_model=UserResponse,
    status_code=HTTPStatus.CREATED,
    summary="Create the new user",
    dependencies=[Depends(check_permissions(ActionEnum.user_create))],
)
async def create_user(
    user_create: UserCreate,
    users_service: UsersService = Depends(get_users_service),
) -> UserResponse:
    """Create the new user."""

    return await users_service.create(user_create)


@router.get(
    "",
    response_model=CursorPage[UserResponse],
    summary="Show the list of users",
    dependencies=[Depends(check_permissions(ActionEnum.user_read))],
)
async def users_list(
    users_service: UsersService = Depends(get_users_service),
) -> CursorPage[UserResponse]:
    """List users with brief information."""

    return await users_service.list()
