from uuid import UUID

from pydantic import BaseModel, ConfigDict

from core.types import EmailType


class UserCreate(BaseModel):
    login: EmailType
    password: str
    first_name: str
    last_name: str


class UserUpdate(BaseModel):
    first_name: str
    last_name: str


class ChangePassword(BaseModel):
    old: str
    new: str


class UserResponse(BaseModel):
    id: UUID
    login: str
    first_name: str
    last_name: str

    model_config = ConfigDict(from_attributes=True)
