import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.alchemy import Base

if TYPE_CHECKING:
    from models import User
    from models.role import Role


class RoleBinding(Base):
    __tablename__ = "role_bindings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="role_bindings")
    role: Mapped["Role"] = relationship(back_populates="role_bindings")

    __table_args__ = (UniqueConstraint("user_id", "role_id", name="_user_role_uc"),)

    def __repr__(self) -> str:
        return f"<RoleBinding role_id={self.role_id!r}, user_id={self.user_id!r}>"
