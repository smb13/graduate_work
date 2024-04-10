import datetime as dt
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ScopeCreate(BaseModel):
    code: str
    name: str


class ScopeUpdate(ScopeCreate):
    id: UUID


class ScopeResponse(BaseModel):
    id: UUID
    code: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class PermissionAdd(BaseModel):
    action: str


class RoleCreate(BaseModel):
    code: str
    name: str
    permissions: list[PermissionAdd]


class RoleUpdate(RoleCreate):
    id: UUID


class RoleDelete(BaseModel):
    id: UUID


class RoleResponse(BaseModel):
    id: UUID
    code: str
    name: str
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = ConfigDict(from_attributes=True)


class ResponseMessage(BaseModel):
    detail: str
