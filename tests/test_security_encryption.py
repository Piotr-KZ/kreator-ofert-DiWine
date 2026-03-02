"""
Testy modułu Encryption (fasthub_core.security.encryption).
"""

import pytest
import os


def test_encryption_imports():
    from fasthub_core.security.encryption import (
        encrypt_credentials, decrypt_credentials,
        rotate_encryption_key, generate_key,
        mask_credentials, is_encryption_available
    )
    assert callable(encrypt_credentials)
    assert callable(decrypt_credentials)


def test_generate_key():
    from fasthub_core.security.encryption import generate_key
    key = generate_key()
    assert isinstance(key, str)
    assert len(key) > 20  # Fernet key jest ~44 chars base64


def test_encrypt_decrypt_roundtrip():
    from fasthub_core.security.encryption import (
        encrypt_credentials, decrypt_credentials, generate_key
    )
    os.environ["FASTHUB_SECRET_KEY"] = generate_key()
    try:
        original = {"api_key": "sk-test-123", "webhook_secret": "whsec_abc"}
        encrypted = encrypt_credentials(original)
        assert encrypted.startswith("ENC:")
        assert "sk-test-123" not in encrypted

        decrypted = decrypt_credentials(encrypted)
        assert decrypted == original
    finally:
        del os.environ["FASTHUB_SECRET_KEY"]


def test_encrypt_without_key_returns_json():
    from fasthub_core.security.encryption import encrypt_credentials, decrypt_credentials
    # Tymczasowo wyczyść klucze z env
    old_key = os.environ.pop("FASTHUB_SECRET_KEY", None)
    old_secret = os.environ.pop("SECRET_KEY", None)
    try:
        # Reset singleton settings
        import fasthub_core.config
        fasthub_core.config._settings = None

        original = {"token": "test"}
        result = encrypt_credentials(original)
        # Powinien być plain JSON (nie zaszyfrowany) — ale nie crash
        decrypted = decrypt_credentials(result)
        assert decrypted == original
    finally:
        if old_key:
            os.environ["FASTHUB_SECRET_KEY"] = old_key
        if old_secret:
            os.environ["SECRET_KEY"] = old_secret
        fasthub_core.config._settings = None


def test_mask_credentials():
    from fasthub_core.security.encryption import mask_credentials
    creds = {"api_key": "sk-very-secret-key-123", "name": "My Integration"}
    masked = mask_credentials(creds)
    assert "sk-very-secret-key-123" not in str(masked)
    # Nazwa nie powinna być zamaskowana
    assert masked.get("name") == "My Integration"


def test_mask_short_value():
    from fasthub_core.security.encryption import mask_credentials
    creds = {"token": "ab"}
    masked = mask_credentials(creds)
    assert masked["token"] == "***"


def test_rotate_key():
    from fasthub_core.security.encryption import (
        encrypt_credentials, rotate_encryption_key, decrypt_credentials, generate_key
    )
    old_key = generate_key()
    new_key = generate_key()

    # Szyfruj z jawnie podanym kluczem (nie z env)
    encrypted = encrypt_credentials({"secret": "data"}, secret_key=old_key)
    assert encrypted.startswith("ENC:")

    # Rotate
    re_encrypted = rotate_encryption_key(old_key, new_key, encrypted)
    assert re_encrypted.startswith("ENC:")

    # Decrypt z nowym kluczem
    decrypted = decrypt_credentials(re_encrypted, secret_key=new_key)
    assert decrypted["secret"] == "data"


def test_no_autoflow_references():
    import inspect
    from fasthub_core.security import encryption
    source = inspect.getsource(encryption)
    assert "AUTOFLOW" not in source


def test_security_init_exports():
    """Security __init__ powinien eksportować kluczowe funkcje"""
    from fasthub_core.security import (
        encrypt_credentials, decrypt_credentials,
        generate_key, mask_credentials, is_encryption_available,
    )
    assert callable(encrypt_credentials)
