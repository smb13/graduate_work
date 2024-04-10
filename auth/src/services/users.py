import uuid
from functools import lru_cache
from http import HTTPStatus

from fastapi import Depends, HTTPException
from fastapi_pagination.cursor import CursorPage
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.alchemy import get_session
from models import User
from schemas.user import ChangePassword, UserCreate, UserUpdate
from services.base import BaseService


class UsersService(BaseService):
    async def retrieve(self, *, username: str | None = None, user_id: uuid.UUID | None = None) -> User | None:
        """Retrieves User from PostgreSQL using SQLAlchemy"""
        if username:
            user = await self.session.scalars(select(User).where(User.login == username))
            return user.first()
        if user_id:
            user = await self.session.scalars(select(User).where(User.id == user_id))
            return user.first()
        return None

    async def create(self, user_create: UserCreate) -> User:
        """Creates User in PostgreSQL using SQLAlchemy"""
        user = await self.retrieve(username=user_create.login)
        if user:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User with this login already exists")

        user = User(**user_create.model_dump())
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def update(self, user: User, user_update: UserUpdate) -> User:
        """Updates User in PostgreSQL using SQLAlchemy"""
        user.first_name = user_update.first_name
        user.last_name = user_update.last_name
        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def change_password(self, user: User, passwords: ChangePassword) -> bool:
        """Updates User in PostgreSQL using SQLAlchemy"""
        if not user.check_password(passwords.old):
            return False

        user.set_password(passwords.new)
        await self.session.commit()
        return True

    async def list(self) -> CursorPage[User]:
        """Lists Users from PostgreSQL using SQLAlchemy"""
        return await paginate(self.session, select(User).order_by(User.created_at.desc()))

    async def authenticate(self, login: str, password: str) -> User | None:
        """Authenticates User in PostgreSQL using SQLAlchemy"""
        user = await self.session.scalars(select(User).where(User.login == login))
        user = user.first()
        if not user or not user.check_password(password):
            return None

        # Если изменились параметры хэширования и хэш не соответствует новым параметрам - пересохраняем хэш пароля
        if user.need_rehash():
            user.set_password(password)
            await self.session.commit()

        return user


@lru_cache
def get_users_service(
    alchemy: AsyncSession = Depends(get_session),
) -> UsersService:
    return UsersService(session=alchemy, redis=None)
