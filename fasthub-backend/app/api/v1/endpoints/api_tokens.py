"""
API Tokens endpoints
API routes for API token management
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.core.rate_limit import RateLimits, limiter
from app.db.session import get_db
from app.models.user import User
from app.schemas.api_token import APITokenCreate, APITokenCreateResponse, APITokenResponse
from app.services.api_token_service import APITokenService

router = APIRouter()


@router.post("/", response_model=APITokenCreateResponse)
async def create_api_token(
    request: APITokenCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create new API token

    Firebase equivalent: CreateApiTokenUseCase

    **⚠️ Important:** The plaintext token is only shown once!
    Save it immediately - you won't be able to see it again.

    Args:
        name: Friendly name for the token
        expires_in_days: Optional expiration in days (None = never expires)

    Returns:
        Token details and plaintext token
    """
    token_service = APITokenService(db)
    api_token, plaintext_token = await token_service.create_token(
        user_id=current_user.id, name=request.name, expires_in_days=request.expires_in_days
    )

    return APITokenCreateResponse(token=api_token, plaintext_token=plaintext_token)


@router.get("/", response_model=List[APITokenResponse])
async def list_api_tokens(
    current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
):
    """
    List all API tokens for current user

    Returns list of tokens (without plaintext values).
    """
    token_service = APITokenService(db)
    tokens = await token_service.list_tokens(user_id=current_user.id)

    return tokens


@router.delete("/{token_id}")
async def delete_api_token(
    token_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete API token

    Firebase equivalent: DeleteApiTokenUseCase

    Revokes the token immediately.
    """
    token_service = APITokenService(db)
    deleted = await token_service.delete_token(token_id=token_id, user_id=current_user.id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found")

    return {"status": "deleted", "token_id": token_id}
