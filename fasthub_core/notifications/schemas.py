"""Pydantic schemas dla Notifications API"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: UUID
    type: str
    title: str
    message: str
    link: Optional[str] = None
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    triggered_by: Optional[UUID] = None

    class Config:
        from_attributes = True


class NotificationList(BaseModel):
    notifications: List[NotificationResponse]
    total: int
    unread_count: int
    page: int
    per_page: int


class UnreadCountResponse(BaseModel):
    unread_count: int


class PreferenceResponse(BaseModel):
    type: str
    inapp: bool
    email: bool
    forced: bool = False


class PreferenceUpdateRequest(BaseModel):
    notification_type: str
    channel_inapp: Optional[bool] = None
    channel_email: Optional[bool] = None
