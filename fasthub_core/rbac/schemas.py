"""Pydantic schemas dla RBAC API"""

from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class PermissionResponse(BaseModel):
    id: UUID
    name: str
    category: str
    description: Optional[str] = None
    is_system: bool

    class Config:
        from_attributes = True


class RoleResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    is_system: bool
    is_default: bool
    permissions: List[str] = []

    class Config:
        from_attributes = True


class RoleCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str]


class RoleUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


class AssignRoleRequest(BaseModel):
    user_id: UUID
    role_id: UUID


class UserPermissionsResponse(BaseModel):
    user_id: UUID
    organization_id: UUID
    roles: List[RoleResponse]
    permissions: List[str]
