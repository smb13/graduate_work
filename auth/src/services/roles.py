import uuid
from collections.abc import Sequence
from copy import copy
from functools import lru_cache
from http import HTTPStatus

from fastapi import Depends, HTTPException
from fastapi_pagination.cursor import CursorPage
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.enums import ActionEnum, SystemRolesEnum
from db.alchemy import get_session
from models import Role, RoleBinding, User
from models.role import Permission
from schemas import role_permissions as role_schemas
from services.base import BaseService


class RolesService(BaseService):
    async def retrieve(self, *, code: str | None = None, role_id: uuid.UUID | None = None) -> Role | None:
        """Retrieves Role from PostgreSQL using SQLAlchemy"""
        if code:
            role = await self.session.scalars(select(Role).where(Role.code == code))
            return role.first()
        if role_id:
            role = await self.session.scalars(select(Role).where(Role.id == role_id))
            return role.first()
        return None

    async def create(self, role_create: role_schemas.RoleCreate) -> Role:
        """Creates Role with Permissions in PostgreSQL using SQLAlchemy"""
        role = await self.retrieve(code=role_create.code)
        if role:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Role with this code already exists")

        role_dict = role_create.model_dump()
        role_dict.pop("permissions")
        role = Role(**role_dict)
        for permission in role_create.permissions:
            role.permissions.append(Permission(action=permission.action))

        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)

        return role

    async def update(self, role_update: role_schemas.RoleUpdate) -> Role:
        """Updates Role with Permissions in PostgreSQL using SQLAlchemy"""
        role = await self.retrieve(role_id=role_update.id)
        if not role:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Role not found")

        duplicate_code_role = await self.retrieve(code=role_update.code)
        if duplicate_code_role and duplicate_code_role.id != role.id:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Role with this code already exists")

        permission_set = {(permission.scope_id, permission.action) for permission in role.permissions}

        for permission in copy(role.permissions):
            if (permission.scope_id, permission.action) not in permission_set:
                role.permissions.remove(permission)
            else:
                permission_set.remove((permission.scope_id, permission.action))

        for scope_id, action in permission_set:
            role.permissions.append(Permission(role_id=role.id, scope_id=scope_id, action=action))

        role.code = role_update.code
        role.name = role_update.name

        await self.session.commit()
        await self.session.refresh(role)

        return role

    async def delete(self, role_delete: role_schemas.RoleDelete) -> None:
        """Delete Role in PostgreSQL using SQLAlchemy"""
        role = await self.retrieve(role_id=role_delete.id)
        if not role:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Role not found")

        await self.session.delete(role)
        await self.session.commit()

    async def list(self) -> CursorPage[Role]:
        """Lists Roles from PostgreSQL using SQLAlchemy"""
        return await paginate(self.session, select(Role).order_by(Role.created_at.desc()))

    async def check_permissions(self, user: User, required_actions: Sequence[str]) -> bool:
        """Check if user has all scopes in their roles permissions"""
        permissions = await self.get_permissions(user)
        existing_actions = {p.action for p in permissions}
        return all(action in existing_actions for action in required_actions)

    async def get_roles_by_user(self, user: User) -> Sequence[Role]:
        """Retrieves Roles from PostgreSQL using SQLAlchemy"""
        roles = await self.session.scalars(select(Role).join(Role.role_bindings).where(RoleBinding.user_id == user.id))
        return roles.all()

    async def get_role_codes(self, user: User) -> Sequence[Role]:
        """Retrieves Role codes from PostgreSQL using SQLAlchemy"""
        role_codes = await self.session.scalars(
            select(Role.code).join(Role.role_bindings).where(RoleBinding.user_id == user.id),
        )
        return role_codes.all()

    async def get_permissions(self, user: User) -> Sequence[Permission]:
        """List Scopes and Actions from User's Roles Permissions"""
        permissions = await self.session.scalars(
            select(Permission).join(Permission.role).join(Role.role_bindings).where(RoleBinding.user_id == user.id),
        )
        return permissions.all()

    async def add_roles_to_user(self, user: User, role_ids: Sequence[uuid.UUID]) -> Sequence[Role]:
        """Add Roles to User in PostgreSQL using SQLAlchemy"""
        bound_role_ids = await self.session.scalars(
            select(RoleBinding.role_id).where(RoleBinding.role_id.in_(role_ids), RoleBinding.user_id == user.id),
        )

        self.session.add_all(
            RoleBinding(user_id=user.id, role_id=role_id) for role_id in set(role_ids) - set(bound_role_ids)
        )

        role_bindings = await self.session.scalars(
            select(Role).join(Role.role_bindings).where(RoleBinding.user_id == user.id),
        )
        await self.session.commit()
        return role_bindings.all()

    async def remove_roles_from_user(self, user: User, role_ids: Sequence[uuid.UUID]) -> Sequence[Role]:
        """Remove Roles from User in PostgreSQL using SQLAlchemy"""
        role_bindings = await self.session.scalars(
            select(RoleBinding).where(RoleBinding.role_id.in_(role_ids), RoleBinding.user_id == user.id),
        )

        for role_binding in role_bindings:
            await self.session.delete(role_binding)

        role_bindings = await self.session.scalars(
            select(Role).join(Role.role_bindings).where(RoleBinding.user_id == user.id),
        )
        await self.session.commit()
        return role_bindings.all()

    async def get_or_create_user_role(self) -> Role:
        """Retrieves User system role or creates it if it doesn't exist"""
        role = await self.retrieve(code=SystemRolesEnum.user)
        if role:
            return role

        new_role = role_schemas.RoleCreate(
            code=SystemRolesEnum.user,
            name="User",
            permissions=[role_schemas.PermissionAdd(action=action) for action in ActionEnum.me_actions()],
        )

        return await self.create(new_role)

    async def get_or_create_admin_role(self) -> Role:
        """Retrieves Admin system role or creates it if it doesn't exist"""
        role = await self.retrieve(code=SystemRolesEnum.admin)
        if role:
            return role

        new_role = role_schemas.RoleCreate(
            code=SystemRolesEnum.admin,
            name="Admin",
            permissions=[
                role_schemas.PermissionAdd(action=action)
                for action in ActionEnum.user_actions() + ActionEnum.role_actions()
            ],
        )

        return await self.create(new_role)


@lru_cache
def get_roles_service(
    alchemy: AsyncSession = Depends(get_session),
) -> RolesService:
    return RolesService(session=alchemy, redis=None)
