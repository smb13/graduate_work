import datetime as dt
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from core.enums import ActionEnum
from db.alchemy import Base

if TYPE_CHECKING:
    from models.role_binding import RoleBinding


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[dt.datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    role_bindings: Mapped[list["RoleBinding"]] = relationship(back_populates="role")
    permissions: Mapped[list["Permission"]] = relationship(back_populates="role", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Role code={self.code!r}, name={self.name!r}>"


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    action: Mapped[ActionEnum] = mapped_column(nullable=False)

    role: Mapped[Role] = relationship(back_populates="permissions")

    def __repr__(self) -> str:
        return f"<Permission role={self.role!r}, action={self.action!r}>"
