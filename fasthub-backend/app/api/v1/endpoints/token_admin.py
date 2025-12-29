"""
Token Administration Endpoints
Admin endpoints for managing token blacklist
"""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_admin_user
from app.core.token_blacklist import TokenBlacklist
from app.models.user import User

router = APIRouter()


@router.get("/blacklist/stats")
async def get_blacklist_stats(current_user: User = Depends(get_current_admin_user)):
    """
    Get token blacklist statistics

    Requires admin privileges.

    Returns:
        - status: Blacklist service status
        - count: Number of blacklisted tokens
        - redis_connected: Redis connection status
    """
    stats = await TokenBlacklist.get_stats()
    return stats


@router.post("/blacklist/clear")
async def clear_blacklist(current_user: User = Depends(get_current_admin_user)):
    """
    Clear all blacklisted tokens

    Requires admin privileges.
    Use with caution - this will allow all previously revoked tokens to be used again.

    Returns:
        - message: Success message
        - cleared: Whether clearing was successful
    """
    success = await TokenBlacklist.clear_all()

    if success:
        return {"message": "Token blacklist cleared successfully", "cleared": True}
    else:
        return {
            "message": "Failed to clear token blacklist (Redis unavailable)",
            "cleared": False,
        }


@router.post("/revoke-token")
async def revoke_token(token: str, current_user: User = Depends(get_current_admin_user)):
    """
    Manually revoke a specific token

    Requires admin privileges.

    Args:
        token: JWT token to revoke

    Returns:
        - message: Success message
        - revoked: Whether token was revoked successfully
    """
    from datetime import datetime, timedelta

    # Add token to blacklist with default TTL
    expires_at = datetime.utcnow() + timedelta(days=7)
    success = await TokenBlacklist.add_token(token, expires_at)

    if success:
        return {"message": "Token revoked successfully", "revoked": True}
    else:
        return {
            "message": "Failed to revoke token (Redis unavailable)",
            "revoked": False,
        }
