"""
Audit Service
Helper for logging SuperAdmin actions
"""

from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.user import User


class AuditService:
    """Service for creating audit logs"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_action(
        self,
        user: User,
        action: str,
        resource_type: str,
        resource_id: Optional[UUID] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """
        Log a SuperAdmin action

        Args:
            user: User who performed the action
            action: Action name (e.g., 'user.delete', 'user.update')
            resource_type: Type of resource (e.g., 'user', 'organization')
            resource_id: ID of the affected resource
            extra_data: Additional context (what changed, etc.)
            request: FastAPI request object (for IP and user agent)

        Returns:
            Created AuditLog instance
        """
        # Extract IP address and user agent from request
        ip_address = None
        user_agent = None
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")

        # Create audit log
        audit_log = AuditLog(
            user_id=user.id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            extra_data=extra_data,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.db.add(audit_log)
        await self.db.flush()  # Flush to get ID but don't commit yet

        return audit_log
