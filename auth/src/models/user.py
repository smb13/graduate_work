import datetime as dt
import uuid
from typing import TYPE_CHECKING

from argon2 import PasswordHasher
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.alchemy import Base
from models.access_log import AccessLogEntry

if TYPE_CHECKING:
    from models.refresh_token import RefreshToken
    from models.role_binding import RoleBinding


ph = PasswordHasher(time_cost=4)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    login: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[dt.datetime] = mapped_column(default=dt.datetime.utcnow)

    role_bindings: Mapped[list["RoleBinding"]] = relationship(back_populates="user")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user")

    def __init__(self, login: str, password: str, first_name: str, last_name: str) -> None:
        self.login = login
        self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name

    access_log: Mapped[list["AccessLogEntry"]] = relationship(back_populates="user")

    def set_password(self, password: str) -> None:
        self.password = ph.hash(password)

    def check_password(self, password: str) -> bool:
        return ph.verify(self.password, password)

    def __repr__(self) -> str:
        return f"<User username={self.login!r}, first_name={self.first_name!r}, last_name={self.last_name!r}>"

    def need_rehash(self) -> bool:
        return ph.check_needs_rehash(self.password)
