"""
FastHub Core — Encryption Service.

AES-128 Fernet encryption for credentials (API keys, OAuth tokens).
Lazy initialization — works without cryptography in dev mode (plain JSON fallback).

Prefix "ENC:" indicates encrypted data — backward compatible with AutoFlow.

Usage:
    from fasthub_core.security.encryption import encrypt_credentials, decrypt_credentials

    encrypted = encrypt_credentials({"api_key": "sk-test-123"})
    # "ENC:gAAAAABh..."

    original = decrypt_credentials(encrypted)
    # {"api_key": "sk-test-123"}
"""

import base64
import hashlib
import json
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger("fasthub.encryption")

# Encryption prefix — marks data as encrypted
ENC_PREFIX = "ENC:"

# Sensitive field patterns for masking
SENSITIVE_PATTERNS = [
    "key", "secret", "token", "password", "credential",
    "auth", "bearer", "api_key", "apikey", "webhook_secret",
]


def _get_secret_key() -> Optional[str]:
    """Get encryption key from config or environment."""
    try:
        from fasthub_core.config import get_settings
        settings = get_settings()
        key = getattr(settings, "SECRET_KEY", None)
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("FASTHUB_SECRET_KEY") or os.environ.get("SECRET_KEY")


def _derive_fernet_key(secret: str) -> bytes:
    """Derive a valid Fernet key from any string secret."""
    key_bytes = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(key_bytes)


def _get_fernet(secret_key: Optional[str] = None):
    """Get Fernet cipher instance. Returns None if unavailable."""
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        logger.warning("cryptography not installed — encryption unavailable")
        return None

    key = secret_key or _get_secret_key()
    if not key:
        return None

    fernet_key = _derive_fernet_key(key)
    return Fernet(fernet_key)


def generate_key() -> str:
    """Generate a new Fernet-compatible encryption key."""
    try:
        from cryptography.fernet import Fernet
        return Fernet.generate_key().decode()
    except ImportError:
        # Fallback: generate a base64-encoded random key
        return base64.urlsafe_b64encode(os.urandom(32)).decode()


def is_encryption_available() -> bool:
    """Check if encryption is configured and available."""
    return _get_fernet() is not None


def encrypt_credentials(credentials: Dict[str, Any], secret_key: Optional[str] = None) -> str:
    """
    Encrypt credentials dict to string.
    Returns "ENC:{encrypted_data}" if key available.
    Falls back to plain JSON (with warning) if no key.
    """
    json_data = json.dumps(credentials)

    fernet = _get_fernet(secret_key)
    if fernet is None:
        logger.warning("No encryption key — storing credentials as plain JSON")
        return json_data

    encrypted = fernet.encrypt(json_data.encode())
    return f"{ENC_PREFIX}{encrypted.decode()}"


def decrypt_credentials(encrypted_data: str, secret_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Decrypt credentials string back to dict.
    Handles both encrypted ("ENC:...") and plain JSON data.
    """
    if not encrypted_data:
        return {}

    if encrypted_data.startswith(ENC_PREFIX):
        fernet = _get_fernet(secret_key)
        if fernet is None:
            logger.error("Cannot decrypt — no encryption key available")
            return {}
        try:
            encrypted_bytes = encrypted_data[len(ENC_PREFIX):].encode()
            decrypted = fernet.decrypt(encrypted_bytes)
            return json.loads(decrypted.decode())
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return {}
    else:
        # Plain JSON (not encrypted)
        try:
            return json.loads(encrypted_data)
        except json.JSONDecodeError:
            logger.error("Failed to parse credentials as JSON")
            return {}


def rotate_encryption_key(
    old_key: str, new_key: str, encrypted_data: str
) -> str:
    """
    Re-encrypt data with a new key.
    Decrypts with old_key, encrypts with new_key.
    """
    decrypted = decrypt_credentials(encrypted_data, secret_key=old_key)
    if not decrypted:
        raise ValueError("Failed to decrypt with old key")
    return encrypt_credentials(decrypted, secret_key=new_key)


def mask_credentials(credentials: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mask sensitive values in credentials dict for logging.
    Non-sensitive fields (like 'name', 'label') are preserved.

    Example:
        {"api_key": "sk-very-long-key"} → {"api_key": "sk-***"}
    """
    if not isinstance(credentials, dict):
        return credentials

    masked = {}
    for key, value in credentials.items():
        key_lower = key.lower()
        is_sensitive = any(pattern in key_lower for pattern in SENSITIVE_PATTERNS)

        if is_sensitive and isinstance(value, str) and len(value) > 3:
            masked[key] = value[:3] + "***"
        elif is_sensitive and isinstance(value, str):
            masked[key] = "***"
        else:
            masked[key] = value
    return masked
