"""Pydantic schemas dla Super Admin API"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class OrganizationStats(BaseModel):
    """Statystyki jednej organizacji"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    owner_email: str
    members_count: int
    created_at: datetime
    subscription_plan: Optional[str] = None
    subscription_status: Optional[str] = None
    last_activity: Optional[datetime] = None


class OrganizationList(BaseModel):
    """Lista organizacji z paginacją"""
    organizations: List[OrganizationStats]
    total: int
    page: int
    per_page: int


class UserDetail(BaseModel):
    """Szczegóły użytkownika dla admina"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_superadmin: bool
    created_at: datetime
    organizations: List[dict] = []


class UserList(BaseModel):
    """Lista użytkowników z paginacją"""
    users: List[UserDetail]
    total: int
    page: int
    per_page: int


class ImpersonateRequest(BaseModel):
    """Żądanie zalogowania jako inny user"""
    user_id: UUID
    reason: str  # OBOWIĄZKOWE — dlaczego się logujesz jako ten user


class ImpersonateResponse(BaseModel):
    """Token tymczasowy do impersonation"""
    access_token: str
    token_type: str = "bearer"
    impersonated_user_id: UUID
    impersonated_user_email: str
    expires_in_minutes: int = 30


class SystemStats(BaseModel):
    """Globalne statystyki systemu"""
    total_organizations: int
    total_users: int
    active_users_last_30_days: int
    total_subscriptions_active: int
    organizations_by_plan: dict = {}
