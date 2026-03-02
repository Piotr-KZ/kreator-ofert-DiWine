"""
FastHub Core — Database Token Storage for OAuth.

Generic storage that works with any SQLAlchemy model.
Encrypts tokens before persisting (via fasthub_core.security.encryption).

Usage:
    storage = DatabaseTokenStorage(
        db_session=db,
        model_class=Integration,
        id_field="id",
        credentials_field="credentials",
    )
"""

import logging
from typing import Any, Optional, Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fasthub_core.integrations.oauth import OAuthTokens, TokenStorage

logger = logging.getLogger("fasthub.oauth")


class DatabaseTokenStorage(TokenStorage):
    """
    Persist OAuth tokens in database.

    Generic — works with any SQLAlchemy model that has:
      - An ID field (configurable)
      - A credentials field (JSON/Text, configurable)

    Tokens are encrypted with Fernet before storage.
    """

    def __init__(
        self,
        db_session: AsyncSession,
        model_class: Type[Any],
        id_field: str = "id",
        credentials_field: str = "credentials",
    ):
        self.db = db_session
        self.model_class = model_class
        self.id_field = id_field
        self.credentials_field = credentials_field

    async def save_tokens(self, provider: str, entity_id: str, tokens: OAuthTokens) -> None:
        """Save encrypted tokens to database."""
        from fasthub_core.security.encryption import encrypt_credentials

        id_col = getattr(self.model_class, self.id_field)
        result = await self.db.execute(
            select(self.model_class).where(id_col == entity_id)
        )
        entity = result.scalar_one_or_none()
        if entity is None:
            logger.error(f"Entity not found: {entity_id}")
            return

        token_data = tokens.to_dict()
        token_data["_provider"] = provider
        encrypted = encrypt_credentials(token_data)

        setattr(entity, self.credentials_field, encrypted)
        await self.db.flush()
        logger.info(f"Tokens saved for {provider}:{entity_id}")

    async def get_tokens(self, provider: str, entity_id: str) -> Optional[OAuthTokens]:
        """Load and decrypt tokens from database."""
        from fasthub_core.security.encryption import decrypt_credentials

        id_col = getattr(self.model_class, self.id_field)
        result = await self.db.execute(
            select(self.model_class).where(id_col == entity_id)
        )
        entity = result.scalar_one_or_none()
        if entity is None:
            return None

        encrypted = getattr(entity, self.credentials_field, None)
        if not encrypted:
            return None

        data = decrypt_credentials(encrypted)
        if not data or "access_token" not in data:
            return None

        return OAuthTokens.from_dict(data)

    async def delete_tokens(self, provider: str, entity_id: str) -> None:
        """Remove tokens from database."""
        id_col = getattr(self.model_class, self.id_field)
        result = await self.db.execute(
            select(self.model_class).where(id_col == entity_id)
        )
        entity = result.scalar_one_or_none()
        if entity is None:
            return

        setattr(entity, self.credentials_field, None)
        await self.db.flush()
        logger.info(f"Tokens deleted for {provider}:{entity_id}")
