"""
Token Blacklist — unieważnianie tokenów JWT.

Dwa backendy:
1. Redis (produkcja) — szybki, rozproszony, TTL automatyczny
2. In-memory (dev/test) — Dict z ręcznym cleanup

Wybór backendu: automatyczny na podstawie REDIS_URL w settings.
"""

from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime, timedelta


class BlacklistBackend(ABC):
    """Interfejs backendu blacklisty"""

    @abstractmethod
    async def add(self, token_jti: str, expires_in: int) -> None:
        """Dodaj token do blacklisty. expires_in = sekundy do wygaśnięcia."""
        pass

    @abstractmethod
    async def is_blacklisted(self, token_jti: str) -> bool:
        """Sprawdź czy token jest na blackliście."""
        pass


class RedisBlacklist(BlacklistBackend):
    """
    Blacklist oparty na Redis.
    Klucz: "blacklisted:{jti}"
    Wartość: "1"
    TTL: taki sam jak czas życia tokenu (auto-cleanup)
    """

    def __init__(self, redis_client):
        self.redis = redis_client
        self.prefix = "blacklisted:"

    async def add(self, token_jti: str, expires_in: int) -> None:
        key = f"{self.prefix}{token_jti}"
        await self.redis.setex(key, expires_in, "1")

    async def is_blacklisted(self, token_jti: str) -> bool:
        key = f"{self.prefix}{token_jti}"
        result = await self.redis.get(key)
        return result is not None


class InMemoryBlacklist(BlacklistBackend):
    """
    Blacklist in-memory — dla dev/test.
    UWAGA: Nie przetrwa restartu serwera. Nie działa w multi-process.
    """

    def __init__(self):
        self._blacklist: dict = {}  # jti -> expiry_time

    async def add(self, token_jti: str, expires_in: int) -> None:
        expiry = datetime.utcnow() + timedelta(seconds=expires_in)
        self._blacklist[token_jti] = expiry
        self._cleanup()

    async def is_blacklisted(self, token_jti: str) -> bool:
        self._cleanup()
        return token_jti in self._blacklist

    def _cleanup(self):
        """Usuń wygasłe wpisy"""
        now = datetime.utcnow()
        expired = [jti for jti, exp in self._blacklist.items() if exp < now]
        for jti in expired:
            del self._blacklist[jti]


# === SINGLETON ===

_blacklist_instance: Optional[BlacklistBackend] = None


async def get_blacklist() -> BlacklistBackend:
    """
    Zwraca instancję blacklisty.
    Redis jeśli REDIS_URL jest ustawiony, inaczej InMemory.
    """
    global _blacklist_instance
    if _blacklist_instance is None:
        try:
            from fasthub_core.config import get_settings
            settings = get_settings()
            redis_url = getattr(settings, 'REDIS_URL', None)
            if redis_url:
                import redis.asyncio as aioredis
                client = aioredis.from_url(redis_url)
                _blacklist_instance = RedisBlacklist(client)
            else:
                _blacklist_instance = InMemoryBlacklist()
        except Exception:
            _blacklist_instance = InMemoryBlacklist()
    return _blacklist_instance


async def blacklist_token(token_jti: str, expires_in: int = 1800) -> None:
    """Convenience function — dodaj token do blacklisty"""
    bl = await get_blacklist()
    await bl.add(token_jti, expires_in)


async def is_token_blacklisted(token_jti: str) -> bool:
    """Convenience function — sprawdź czy token jest na blackliście"""
    bl = await get_blacklist()
    return await bl.is_blacklisted(token_jti)
