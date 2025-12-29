"""
Admin service
Business logic for admin operations
"""

from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invoice import Invoice
from app.models.organization import Organization
from app.models.subscription import Subscription
from app.models.user import User


class AdminService:
    """Service for admin operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def broadcast_message(
        self,
        title: str,
        message: str,
        target_user_ids: Optional[List[int]] = None,
        url: Optional[str] = None,
        emoji_icon: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Broadcast message to all users or specific users
        Firebase equivalent: BroadcastMessageUseCase

        Args:
            title: Message title
            message: Message content
            target_user_ids: Optional list of specific user IDs to target
            url: Optional URL to include in message
            emoji_icon: Optional emoji icon for message

        Returns:
            Dict with status and count of users notified
        """
        # Get target users
        query = select(User).where(User.is_active == True)

        if target_user_ids:
            query = query.where(User.id.in_(target_user_ids))

        result = await self.db.execute(query)
        users = list(result.scalars().all())

        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No users found to notify"
            )

        # TODO: Implement actual notification sending
        # This would integrate with:
        # - Email service (SendGrid)
        # - In-app notifications
        # - Push notifications
        # - Webhook notifications

        # For now, just log the broadcast
        user_emails = [user.email for user in users]

        return {
            "status": "success",
            "users_notified": len(users),
            "target_emails": user_emails,
            "message": {"title": title, "content": message, "url": url, "emoji": emoji_icon},
        }

    async def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system statistics
        Returns overview of users, organizations, subscriptions
        """
        # Count users
        users_result = await self.db.execute(select(func.count(User.id)))
        total_users = users_result.scalar()

        # Count active users
        active_users_result = await self.db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        active_users = active_users_result.scalar()

        # Count organizations
        orgs_result = await self.db.execute(select(func.count(Organization.id)))
        total_organizations = orgs_result.scalar()

        # Count subscriptions by status
        active_subs_result = await self.db.execute(
            select(func.count(Subscription.id)).where(Subscription.status == "active")
        )
        active_subscriptions = active_subs_result.scalar()

        # Count total subscriptions
        total_subs_result = await self.db.execute(select(func.count(Subscription.id)))
        total_subscriptions = total_subs_result.scalar()

        # Count invoices
        invoices_result = await self.db.execute(select(func.count(Invoice.id)))
        total_invoices = invoices_result.scalar()

        # Count paid invoices
        paid_invoices_result = await self.db.execute(
            select(func.count(Invoice.id)).where(Invoice.status == "paid")
        )
        paid_invoices = paid_invoices_result.scalar()

        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "inactive": total_users - active_users,
            },
            "organizations": {"total": total_organizations},
            "subscriptions": {
                "total": total_subscriptions,
                "active": active_subscriptions,
                "inactive": total_subscriptions - active_subscriptions,
            },
            "invoices": {
                "total": total_invoices,
                "paid": paid_invoices,
                "unpaid": total_invoices - paid_invoices,
            },
        }

    async def get_recent_users(self, limit: int = 10) -> List[User]:
        """Get recently registered users"""
        result = await self.db.execute(select(User).order_by(User.created_at.desc()).limit(limit))
        return list(result.scalars().all())

    async def get_recent_subscriptions(self, limit: int = 10) -> List[Subscription]:
        """Get recently created subscriptions"""
        result = await self.db.execute(
            select(Subscription).order_by(Subscription.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())
