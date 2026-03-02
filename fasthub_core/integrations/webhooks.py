"""
FastHub Core — Webhook Base.

Registration, signature verification, deduplication.
Generic webhook infrastructure for any SaaS application.

Usage:
    from fasthub_core.integrations.webhooks import SignatureVerifier, SignatureMethod

    sig = SignatureVerifier.compute_signature(payload, secret, SignatureMethod.HMAC_SHA256)
    is_valid = SignatureVerifier.verify_signature(payload, secret, sig, SignatureMethod.HMAC_SHA256)
"""

import hashlib
import hmac
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("fasthub.webhooks")


# === ENUMS ===


class WebhookStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    FAILED = "failed"


class SignatureMethod(str, Enum):
    HMAC_SHA256 = "hmac_sha256"
    HMAC_SHA1 = "hmac_sha1"
    HMAC_MD5 = "hmac_md5"


# === DATA CLASSES ===


@dataclass
class WebhookConfig:
    """Configuration for a webhook endpoint."""
    url: str
    events: List[str]
    secret: Optional[str] = None
    signature_method: SignatureMethod = SignatureMethod.HMAC_SHA256
    headers: Dict[str, str] = field(default_factory=dict)
    retry_policy: Dict[str, Any] = field(default_factory=lambda: {
        "max_retries": 3,
        "backoff_factor": 2,
        "initial_delay": 1,
    })


@dataclass
class WebhookEvent:
    """A webhook delivery event."""
    id: str
    webhook_id: str
    event_type: str
    payload: Dict[str, Any]
    status: str = "pending"  # pending, delivered, failed
    attempts: int = 0
    last_attempt_at: Optional[datetime] = None
    response_code: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    @staticmethod
    def new_id() -> str:
        return str(uuid.uuid4())


@dataclass
class WebhookRegistration:
    """A registered webhook endpoint."""
    id: str
    config: WebhookConfig
    status: WebhookStatus = WebhookStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_triggered_at: Optional[datetime] = None
    total_deliveries: int = 0
    total_failures: int = 0


# === SIGNATURE VERIFICATION ===


class SignatureVerifier:
    """Compute and verify webhook payload signatures."""

    @staticmethod
    def compute_signature(
        payload: bytes, secret: str, method: SignatureMethod
    ) -> str:
        """Compute HMAC signature for payload."""
        hash_func = {
            SignatureMethod.HMAC_SHA256: hashlib.sha256,
            SignatureMethod.HMAC_SHA1: hashlib.sha1,
            SignatureMethod.HMAC_MD5: hashlib.md5,
        }.get(method, hashlib.sha256)

        signature = hmac.new(
            secret.encode(), payload, hash_func
        ).hexdigest()
        return signature

    @staticmethod
    def verify_signature(
        payload: bytes, secret: str, signature: str, method: SignatureMethod
    ) -> bool:
        """Verify HMAC signature against payload."""
        expected = SignatureVerifier.compute_signature(payload, secret, method)
        return hmac.compare_digest(expected, signature)


# === STORAGE ===


class WebhookStorage(ABC):
    """Abstract base for webhook data persistence."""

    @abstractmethod
    async def save_registration(self, registration: WebhookRegistration) -> None:
        ...

    @abstractmethod
    async def get_registration(self, webhook_id: str) -> Optional[WebhookRegistration]:
        ...

    @abstractmethod
    async def list_registrations(self, entity_id: str) -> List[WebhookRegistration]:
        ...

    @abstractmethod
    async def delete_registration(self, webhook_id: str) -> None:
        ...

    @abstractmethod
    async def save_event(self, event: WebhookEvent) -> None:
        ...

    @abstractmethod
    async def get_event(self, event_id: str) -> Optional[WebhookEvent]:
        ...

    @abstractmethod
    async def check_duplicate(self, event_id: str) -> bool:
        ...

    @abstractmethod
    async def get_pending_events(self, limit: int = 100) -> List[WebhookEvent]:
        ...


class MemoryWebhookStorage(WebhookStorage):
    """In-memory webhook storage — for testing and development."""

    def __init__(self):
        self._registrations: Dict[str, WebhookRegistration] = {}
        self._events: Dict[str, WebhookEvent] = {}

    async def save_registration(self, registration: WebhookRegistration) -> None:
        self._registrations[registration.id] = registration

    async def get_registration(self, webhook_id: str) -> Optional[WebhookRegistration]:
        return self._registrations.get(webhook_id)

    async def list_registrations(self, entity_id: str) -> List[WebhookRegistration]:
        # In memory, return all registrations (entity_id filtering is app-specific)
        return list(self._registrations.values())

    async def delete_registration(self, webhook_id: str) -> None:
        self._registrations.pop(webhook_id, None)

    async def save_event(self, event: WebhookEvent) -> None:
        self._events[event.id] = event

    async def get_event(self, event_id: str) -> Optional[WebhookEvent]:
        return self._events.get(event_id)

    async def check_duplicate(self, event_id: str) -> bool:
        """Returns True if event already exists (is duplicate)."""
        return event_id in self._events

    async def get_pending_events(self, limit: int = 100) -> List[WebhookEvent]:
        pending = [e for e in self._events.values() if e.status == "pending"]
        return pending[:limit]
