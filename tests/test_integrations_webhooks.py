"""
Testy modułu Webhook Base (fasthub_core.integrations.webhooks).
"""

import pytest
import asyncio


def test_webhook_imports():
    from fasthub_core.integrations.webhooks import (
        WebhookStatus, SignatureMethod, WebhookConfig,
        WebhookEvent, WebhookRegistration,
        WebhookStorage, MemoryWebhookStorage,
        SignatureVerifier
    )
    assert WebhookStatus.ACTIVE == "active"
    assert SignatureMethod.HMAC_SHA256 == "hmac_sha256"


def test_signature_verifier_hmac_sha256():
    from fasthub_core.integrations.webhooks import SignatureVerifier, SignatureMethod

    payload = b'{"event": "test"}'
    secret = "my_webhook_secret"

    sig = SignatureVerifier.compute_signature(payload, secret, SignatureMethod.HMAC_SHA256)
    assert isinstance(sig, str)
    assert len(sig) > 0

    # Verify
    assert SignatureVerifier.verify_signature(payload, secret, sig, SignatureMethod.HMAC_SHA256) == True

    # Wrong secret
    assert SignatureVerifier.verify_signature(payload, "wrong_secret", sig, SignatureMethod.HMAC_SHA256) == False


def test_signature_verifier_hmac_sha1():
    from fasthub_core.integrations.webhooks import SignatureVerifier, SignatureMethod
    payload = b"test"
    secret = "secret"
    sig = SignatureVerifier.compute_signature(payload, secret, SignatureMethod.HMAC_SHA1)
    assert SignatureVerifier.verify_signature(payload, secret, sig, SignatureMethod.HMAC_SHA1) == True


def test_signature_verifier_hmac_md5():
    from fasthub_core.integrations.webhooks import SignatureVerifier, SignatureMethod
    payload = b"md5test"
    secret = "md5secret"
    sig = SignatureVerifier.compute_signature(payload, secret, SignatureMethod.HMAC_MD5)
    assert SignatureVerifier.verify_signature(payload, secret, sig, SignatureMethod.HMAC_MD5) == True


def test_memory_webhook_storage():
    from fasthub_core.integrations.webhooks import (
        MemoryWebhookStorage, WebhookRegistration, WebhookConfig,
        WebhookStatus, SignatureMethod
    )

    storage = MemoryWebhookStorage()
    config = WebhookConfig(
        url="https://example.com/webhook",
        events=["user.created"],
        secret="secret123",
        signature_method=SignatureMethod.HMAC_SHA256,
    )
    reg = WebhookRegistration(id="wh-1", config=config, status=WebhookStatus.ACTIVE)

    asyncio.get_event_loop().run_until_complete(
        storage.save_registration(reg)
    )
    result = asyncio.get_event_loop().run_until_complete(
        storage.get_registration("wh-1")
    )
    assert result is not None
    assert result.config.url == "https://example.com/webhook"


def test_webhook_event_deduplication():
    from fasthub_core.integrations.webhooks import MemoryWebhookStorage, WebhookEvent

    storage = MemoryWebhookStorage()
    event = WebhookEvent(
        id="evt-1", webhook_id="wh-1",
        event_type="user.created", payload={"user_id": "123"},
        status="pending", attempts=0
    )

    asyncio.get_event_loop().run_until_complete(storage.save_event(event))

    is_dup = asyncio.get_event_loop().run_until_complete(storage.check_duplicate("evt-1"))
    assert is_dup == True

    is_new = asyncio.get_event_loop().run_until_complete(storage.check_duplicate("evt-999"))
    assert is_new == False


def test_webhook_event_new_id():
    from fasthub_core.integrations.webhooks import WebhookEvent
    id1 = WebhookEvent.new_id()
    id2 = WebhookEvent.new_id()
    assert id1 != id2
    assert len(id1) == 36  # UUID format


def test_webhook_storage_delete():
    from fasthub_core.integrations.webhooks import (
        MemoryWebhookStorage, WebhookRegistration, WebhookConfig,
        WebhookStatus, SignatureMethod
    )
    storage = MemoryWebhookStorage()
    config = WebhookConfig(url="https://test.com/wh", events=["test"])
    reg = WebhookRegistration(id="wh-del", config=config)

    asyncio.get_event_loop().run_until_complete(storage.save_registration(reg))
    asyncio.get_event_loop().run_until_complete(storage.delete_registration("wh-del"))
    result = asyncio.get_event_loop().run_until_complete(storage.get_registration("wh-del"))
    assert result is None


def test_pending_events():
    from fasthub_core.integrations.webhooks import MemoryWebhookStorage, WebhookEvent

    storage = MemoryWebhookStorage()
    for i in range(3):
        event = WebhookEvent(
            id=f"evt-{i}", webhook_id="wh-1",
            event_type="test", payload={},
            status="pending" if i < 2 else "delivered",
        )
        asyncio.get_event_loop().run_until_complete(storage.save_event(event))

    pending = asyncio.get_event_loop().run_until_complete(storage.get_pending_events())
    assert len(pending) == 2


def test_no_autoflow_references():
    import inspect
    from fasthub_core.integrations import webhooks
    source = inspect.getsource(webhooks)
    assert "process_id" not in source
    assert "autoflow" not in source.lower()
