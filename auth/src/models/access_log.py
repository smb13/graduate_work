import datetime as dt
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.alchemy import Base

if TYPE_CHECKING:
    from models.user import User


class AccessLogEntry(Base):
    __tablename__ = "access_log"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=False)
    user_agent: Mapped[str] = mapped_column(nullable=False)
    origin: Mapped[str] = mapped_column(nullable=False)
    created: Mapped[dt.datetime] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship(back_populates="access_log")

    def __repr__(self) -> str:
        return f"<AccessLog user_id={self.user_id!r}, ip_address={self.ip_address!r}>"
