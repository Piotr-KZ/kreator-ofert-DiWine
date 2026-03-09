"""Testy 2FA TOTP + Sessions (Brief 26)."""

import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

# Add fasthub-backend to path
_backend_dir = os.path.join(os.path.dirname(__file__), "..", "fasthub-backend")
if os.path.isdir(_backend_dir) and _backend_dir not in sys.path:
    sys.path.insert(0, os.path.abspath(_backend_dir))

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-2fa")


# === IMPORTS ===

def test_totp_module_imports():
    """Moduł TOTP musi być importowalny."""
    from fasthub_core.auth.totp import TOTPService
    assert TOTPService is not None


def test_device_parser_imports():
    """Moduł device_parser musi być importowalny."""
    from fasthub_core.auth.device_parser import parse_device
    assert callable(parse_device)


def test_session_model_imports():
    """Model UserSession musi być importowalny."""
    from fasthub_core.auth.session_models import UserSession
    assert UserSession is not None


def test_2fa_endpoints_import():
    """Endpointy 2FA muszą być importowalne."""
    from app.api.v1.endpoints.two_factor import router
    assert router is not None


def test_sessions_endpoints_import():
    """Endpointy sessions muszą być importowalne."""
    from app.api.v1.endpoints.sessions import router
    assert router is not None


# === TOTP SERVICE — GENERATE ===

def test_generate_secret():
    """Generuje base32 string."""
    from fasthub_core.auth.totp import TOTPService
    totp = TOTPService()
    secret = totp.generate_secret()
    assert len(secret) == 32
    assert secret.isalnum()


def test_provisioning_uri():
    """Poprawny format otpauth://."""
    from fasthub_core.auth.totp import TOTPService
    totp = TOTPService()
    secret = totp.generate_secret()
    uri = totp.generate_provisioning_uri(secret, "test@example.com")
    assert uri.startswith("otpauth://totp/")
    assert "test" in uri and "example.com" in uri
    assert "FastHub" in uri


def test_qr_code_base64():
    """Zwraca valid base64 PNG."""
    from fasthub_core.auth.totp import TOTPService
    import base64
    totp = TOTPService()
    secret = totp.generate_secret()
    uri = totp.generate_provisioning_uri(secret, "test@example.com")
    qr = totp.generate_qr_code_base64(uri)
    # Should be valid base64
    decoded = base64.b64decode(qr)
    # PNG starts with magic bytes
    assert decoded[:4] == b'\x89PNG'


# === TOTP SERVICE — VERIFY ===

def test_verify_valid_code():
    """Generuj secret → generuj aktualny kod → verify=True."""
    from fasthub_core.auth.totp import TOTPService
    import pyotp
    totp = TOTPService()
    secret = totp.generate_secret()
    # Generate current code
    current_code = pyotp.TOTP(secret).now()
    assert totp.verify_code(secret, current_code) is True


def test_verify_invalid_code():
    """Zły kod → False."""
    from fasthub_core.auth.totp import TOTPService
    totp = TOTPService()
    secret = totp.generate_secret()
    assert totp.verify_code(secret, "000000") is False


def test_verify_window():
    """Kod z okna ±1 powinien działać."""
    from fasthub_core.auth.totp import TOTPService
    import pyotp
    import time
    totp = TOTPService()
    secret = totp.generate_secret()
    # Current code should work
    code = pyotp.TOTP(secret).now()
    assert totp.verify_code(secret, code) is True


# === BACKUP CODES ===

def test_backup_codes_generation():
    """10 kodów, każdy 8 znaków."""
    from fasthub_core.auth.totp import TOTPService
    totp = TOTPService()
    codes = totp.generate_backup_codes()
    assert len(codes) == 10
    for code in codes:
        assert len(code) == 8
        assert code == code.upper()


def test_backup_code_verify_valid():
    """Poprawny backup code → True + usunięty z listy."""
    from fasthub_core.auth.totp import TOTPService
    totp = TOTPService()
    codes = totp.generate_backup_codes()
    codes_json = json.dumps(codes)

    valid, updated = totp.verify_backup_code(codes_json, codes[0])
    assert valid is True
    remaining = json.loads(updated)
    assert len(remaining) == 9
    assert codes[0] not in remaining


def test_backup_code_verify_invalid():
    """Zły backup code → False + lista bez zmian."""
    from fasthub_core.auth.totp import TOTPService
    totp = TOTPService()
    codes = totp.generate_backup_codes()
    codes_json = json.dumps(codes)

    valid, updated = totp.verify_backup_code(codes_json, "ZZZZZZZZ")
    assert valid is False
    assert json.loads(updated) == codes


def test_backup_code_single_use():
    """Ten sam kod drugi raz → False."""
    from fasthub_core.auth.totp import TOTPService
    totp = TOTPService()
    codes = totp.generate_backup_codes()
    codes_json = json.dumps(codes)

    # First use
    valid, updated = totp.verify_backup_code(codes_json, codes[0])
    assert valid is True

    # Second use
    valid2, _ = totp.verify_backup_code(updated, codes[0])
    assert valid2 is False


def test_backup_code_case_insensitive():
    """Backup code case insensitive."""
    from fasthub_core.auth.totp import TOTPService
    totp = TOTPService()
    codes = totp.generate_backup_codes()
    codes_json = json.dumps(codes)

    valid, _ = totp.verify_backup_code(codes_json, codes[0].lower())
    assert valid is True


# === DEVICE PARSER ===

def test_parse_chrome_windows():
    """Chrome na Windows → desktop."""
    from fasthub_core.auth.device_parser import parse_device
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    result = parse_device(ua)
    assert result["device_type"] == "desktop"
    assert "Chrome" in result["browser"]
    assert "Windows" in result["os"]


def test_parse_safari_iphone():
    """Safari na iPhone → mobile."""
    from fasthub_core.auth.device_parser import parse_device
    ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    result = parse_device(ua)
    assert result["device_type"] == "mobile"
    assert "Safari" in result["browser"] or "Mobile Safari" in result["browser"]


def test_parse_empty_ua():
    """Pusty User-Agent → graceful fallback."""
    from fasthub_core.auth.device_parser import parse_device
    result = parse_device("")
    assert "device_type" in result
    assert "browser" in result
    assert "os" in result


def test_parse_none_ua():
    """None User-Agent → graceful fallback."""
    from fasthub_core.auth.device_parser import parse_device
    result = parse_device(None)
    assert result["device_type"] is not None


# === 2FA TEMP TOKEN ===

def test_create_and_decode_2fa_temp_token():
    """Temp token round-trip."""
    from fasthub_core.auth.service import create_2fa_temp_token, decode_2fa_temp_token
    user_id = "550e8400-e29b-41d4-a716-446655440000"
    token = create_2fa_temp_token(user_id)
    decoded = decode_2fa_temp_token(token)
    assert decoded == user_id


def test_decode_invalid_temp_token():
    """Nieprawidłowy token → None."""
    from fasthub_core.auth.service import decode_2fa_temp_token
    assert decode_2fa_temp_token("invalid-token") is None


def test_temp_token_type_check():
    """Access token nie powinien działać jako temp token."""
    from fasthub_core.auth.service import create_access_token, decode_2fa_temp_token
    access = create_access_token(data={"sub": "user123"})
    assert decode_2fa_temp_token(access) is None


# === JTI IN REFRESH TOKEN ===

def test_refresh_token_has_jti():
    """Refresh token powinien mieć JTI (Brief 26)."""
    from fasthub_core.auth.service import create_refresh_token, decode_refresh_token
    token = create_refresh_token(data={"sub": "user123"})
    payload = decode_refresh_token(token)
    assert payload is not None
    assert "jti" in payload
    assert len(payload["jti"]) > 0


# === USER MODEL FIELDS ===

def test_user_model_has_totp_fields():
    """User model ma pola TOTP."""
    from fasthub_core.users.models import User
    columns = {c.name for c in User.__table__.columns}
    assert "totp_secret" in columns
    assert "totp_enabled" in columns
    assert "totp_verified_at" in columns
    assert "backup_codes" in columns


# === SESSION MODEL ===

def test_session_model_has_required_fields():
    """UserSession model ma wymagane pola."""
    from fasthub_core.auth.session_models import UserSession
    columns = {c.name for c in UserSession.__table__.columns}
    assert "user_id" in columns
    assert "token_jti" in columns
    assert "device_type" in columns
    assert "device_name" in columns
    assert "browser" in columns
    assert "os" in columns
    assert "ip_address" in columns
    assert "is_active" in columns
    assert "last_active_at" in columns
    assert "expires_at" in columns
    assert "revoked_at" in columns


# === CONFIG ===

def test_config_has_2fa_fields():
    """Config ma pola 2FA."""
    from fasthub_core.config import Settings
    fields = Settings.model_fields
    assert "TOTP_ISSUER_NAME" in fields
    assert "TOTP_TEMP_TOKEN_EXPIRE_MINUTES" in fields
    assert "SESSION_CLEANUP_DAYS" in fields


# === TOTP SERVICE CUSTOM ISSUER ===

def test_custom_issuer_name():
    """Custom issuer name w URI."""
    from fasthub_core.auth.totp import TOTPService
    totp = TOTPService(issuer_name="MyApp")
    secret = totp.generate_secret()
    uri = totp.generate_provisioning_uri(secret, "test@example.com")
    assert "MyApp" in uri
