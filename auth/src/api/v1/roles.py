from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination.cursor import CursorPage

from core.enums import ActionEnum
from models import User
from schemas import role_permissions as role_schemas
from schemas.user import UserResponse
from services.auth import check_permissions
from services.roles import RolesService, get_roles_service

router = APIRouter()


@router.get(
    "/{role_id}",
    response_model=role_schemas.RoleResponse,
    summary="Retrieve a role",
)
async def role_details(
    role_id: UUID,
    roles_service: RolesService = Depends(check_permissions(ActionEnum.role_read)),
) -> role_schemas.RoleResponse:
    """Retrieve an item with all the information."""

    role: User | None = await roles_service.retrieve(role_id=role_id)
    if not role:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Role not found")

    return role


@router.post(
    "",
    summary="Create role",
    response_model=role_schemas.RoleResponse,
    status_code=HTTPStatus.CREATED,
)
async def create_role(
    role_create: role_schemas.RoleCreate,
    current_user: Annotated[User, Depends(check_permissions(ActionEnum.role_create))],
    roles_service: RolesService = Depends(get_roles_service),
) -> role_schemas.RoleResponse:
    """Create role."""

    return await roles_service.create(role_create)


@router.get(
    "",
    response_model=CursorPage[role_schemas.RoleResponse],
    summary="List roles",
)
async def roles_list(
    current_user: Annotated[User, Depends(check_permissions(ActionEnum.role_read))],
    roles_service: RolesService = Depends(get_roles_service),
) -> CursorPage[UserResponse]:
    """List roles with brief information."""

    return await roles_service.list()


@router.put(
    "",
    response_model=role_schemas.RoleResponse,
    summary="Update roles to user",
)
async def update_roles(
    role_update: role_schemas.RoleUpdate,
    current_user: Annotated[User, Depends(check_permissions(ActionEnum.role_update))],
    roles_service: RolesService = Depends(get_roles_service),
) -> role_schemas.RoleResponse:
    """Update roles to user."""

    return await roles_service.update(role_update)


@router.delete(
    "",
    summary="Deleting a role with Role bindings",
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_role(
    role_delete: role_schemas.RoleDelete,
    current_user: Annotated[User, Depends(check_permissions(ActionEnum.role_delete))],
    roles_service: RolesService = Depends(get_roles_service),
) -> None:
    """Deleting a role for all users."""

    return await roles_service.delete(role_delete)
