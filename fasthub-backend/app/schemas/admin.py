"""
Admin schemas (DTOs)
Pydantic models for admin operations
"""

from typing import List, Optional

from pydantic import BaseModel


class BroadcastMessageRequest(BaseModel):
    model_config = {"strict": True}
    """Schema for broadcast message request"""

    title: str
    message: str
    target_user_ids: Optional[List[int]] = None
    url: Optional[str] = None
    emoji_icon: Optional[str] = None


class BroadcastMessageResponse(BaseModel):
    model_config = {"strict": True}
    """Schema for broadcast message response"""

    status: str
    users_notified: int
    target_emails: List[str]
    message: dict


class SystemStatsResponse(BaseModel):
    model_config = {"strict": True}
    """Schema for system statistics response"""

    users: dict
    organizations: dict
    subscriptions: dict
    invoices: dict
