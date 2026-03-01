"""Pydantic schemas dla Audit API"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime


class AuditLogResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID] = None
    user_email: Optional[str] = None
    impersonated_by: Optional[UUID] = None
    organization_id: Optional[UUID] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    changes_before: Optional[Dict[str, Any]] = None
    changes_after: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogList(BaseModel):
    logs: List[AuditLogResponse]
    total: int
    page: int
    per_page: int


class AuditStatsResponse(BaseModel):
    total_entries: int
    oldest_entry: Optional[str] = None
    entries_last_24h: int


class RetentionResult(BaseModel):
    deleted_count: int
    retention_days: int
