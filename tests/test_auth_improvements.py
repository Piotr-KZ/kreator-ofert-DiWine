"""Testy Auth Improvements — blacklist, password, email verification"""

# === TOKEN BLACKLIST ===

def test_blacklist_module_exists():
    """Moduł blacklist musi być importowalny"""
    from fasthub_core.auth.blacklist import (
        BlacklistBackend, RedisBlacklist, InMemoryBlacklist,
        blacklist_token, is_token_blacklisted, get_blacklist,
    )
    assert callable(blacklist_token)
    assert callable(is_token_blacklisted)


import pytest


@pytest.mark.asyncio
async def test_in_memory_blacklist():
    """InMemoryBlacklist musi dodawać i sprawdzać tokeny"""
    from fasthub_core.auth.blacklist import InMemoryBlacklist
    bl = InMemoryBlacklist()

    # Nowy token — nie na liście
    assert await bl.is_blacklisted("token-123") == False

    # Dodaj do blacklisty
    await bl.add("token-123", expires_in=3600)

    # Teraz jest na liście
    assert await bl.is_blacklisted("token-123") == True

    # Inny token — nie na liście
    assert await bl.is_blacklisted("token-456") == False


@pytest.mark.asyncio
async def test_in_memory_blacklist_cleanup():
    """InMemoryBlacklist musi czyścić wygasłe tokeny"""
    from fasthub_core.auth.blacklist import InMemoryBlacklist
    bl = InMemoryBlacklist()

    # Dodaj token z TTL 0 (natychmiast wygasa)
    await bl.add("expired-token", expires_in=0)

    # Po cleanup powinien zniknąć
    import asyncio
    await asyncio.sleep(0.1)
    assert await bl.is_blacklisted("expired-token") == False


# === PASSWORD VALIDATION ===

def test_password_validator_exists():
    """Moduł password_validation musi być importowalny"""
    from fasthub_core.auth.password_validation import (
        PasswordValidator, validate_password, get_password_validator,
    )
    assert callable(validate_password)


def test_weak_password():
    """Słabe hasło musi mieć błędy"""
    from fasthub_core.auth.password_validation import validate_password
    errors = validate_password("abc")
    assert len(errors) > 0
    assert any("Minimum" in e for e in errors)


def test_strong_password():
    """Silne hasło nie powinno mieć błędów"""
    from fasthub_core.auth.password_validation import validate_password
    errors = validate_password("SecurePass123")
    assert len(errors) == 0


def test_password_missing_uppercase():
    """Hasło bez wielkiej litery powinno mieć błąd"""
    from fasthub_core.auth.password_validation import validate_password
    errors = validate_password("securepass123")
    assert any("wielka litera" in e for e in errors)


def test_password_missing_digit():
    """Hasło bez cyfry powinno mieć błąd"""
    from fasthub_core.auth.password_validation import validate_password
    errors = validate_password("SecurePassword")
    assert any("cyfra" in e for e in errors)


def test_password_missing_lowercase():
    """Hasło bez małej litery powinno mieć błąd"""
    from fasthub_core.auth.password_validation import validate_password
    errors = validate_password("SECUREPASS123")
    assert any("mała litera" in e for e in errors)


def test_password_strength():
    """get_strength musi oceniać siłę hasła"""
    from fasthub_core.auth.password_validation import PasswordValidator
    v = PasswordValidator()
    assert v.get_strength("ab") == "weak"
    assert v.get_strength("SecurePass123!") == "strong"


def test_password_max_length():
    """Za długie hasło powinno mieć błąd"""
    from fasthub_core.auth.password_validation import validate_password
    long_password = "A1" + "a" * 200
    errors = validate_password(long_password)
    assert any("Maximum" in e for e in errors)


def test_password_custom_validator():
    """PasswordValidator z własnymi parametrami"""
    from fasthub_core.auth.password_validation import PasswordValidator
    v = PasswordValidator(min_length=4, require_uppercase=False, require_digit=False)
    errors = v.validate("abcd")
    assert len(errors) == 0


# === EMAIL VERIFICATION ===

def test_email_verification_module_exists():
    """EmailVerificationService musi być importowalny"""
    from fasthub_core.auth.email_verification import EmailVerificationService
    assert EmailVerificationService is not None
    assert hasattr(EmailVerificationService, 'generate_verification_token')
    assert hasattr(EmailVerificationService, 'decode_verification_token')
    assert hasattr(EmailVerificationService, 'verify_email')
    assert hasattr(EmailVerificationService, 'resend_verification')
    assert hasattr(EmailVerificationService, 'get_verification_url')


def test_verification_token_generation():
    """Token weryfikacyjny musi być generowany"""
    from fasthub_core.auth.email_verification import EmailVerificationService
    service = EmailVerificationService(
        db=None,
        secret_key="test-secret-key-12345",
        base_url="http://localhost:3000",
    )
    token = service.generate_verification_token("user-123", "test@example.com")
    assert isinstance(token, str)
    assert len(token) > 20


def test_verification_token_decode():
    """Token weryfikacyjny musi być poprawnie dekodowany"""
    from fasthub_core.auth.email_verification import EmailVerificationService
    service = EmailVerificationService(
        db=None,
        secret_key="test-secret-key-12345",
    )
    token = service.generate_verification_token("user-123", "test@example.com")
    payload = service.decode_verification_token(token)
    assert payload is not None
    assert payload["sub"] == "user-123"
    assert payload["email"] == "test@example.com"
    assert payload["type"] == "email_verify"


def test_verification_token_wrong_secret():
    """Token z innym secret musi być odrzucony"""
    from fasthub_core.auth.email_verification import EmailVerificationService
    service1 = EmailVerificationService(db=None, secret_key="secret-1")
    service2 = EmailVerificationService(db=None, secret_key="secret-2")

    token = service1.generate_verification_token("user-123", "test@example.com")
    payload = service2.decode_verification_token(token)
    assert payload is None


def test_verification_url():
    """URL weryfikacyjny musi zawierać token"""
    from fasthub_core.auth.email_verification import EmailVerificationService
    service = EmailVerificationService(
        db=None,
        secret_key="test-secret",
        base_url="https://myapp.com",
    )
    token = service.generate_verification_token("user-123", "test@example.com")
    url = service.get_verification_url(token)
    assert url.startswith("https://myapp.com/verify-email?token=")


# === AUTH ROUTES ===

def test_auth_routes_have_logout():
    """Endpoint /logout powinien istnieć"""
    from fasthub_core.auth.routes import router
    route_paths = [r.path for r in router.routes]
    assert any("logout" in p for p in route_paths)


def test_auth_routes_have_verify_email():
    """Endpoint /verify-email powinien istnieć"""
    from fasthub_core.auth.routes import router
    route_paths = [r.path for r in router.routes]
    assert any("verify-email" in p for p in route_paths)


def test_auth_routes_have_resend_verification():
    """Endpoint /resend-verification powinien istnieć"""
    from fasthub_core.auth.routes import router
    route_paths = [r.path for r in router.routes]
    assert any("resend-verification" in p for p in route_paths)


# === JTI IN TOKENS ===

def test_access_token_has_jti():
    """create_access_token musi dodawać JTI do tokenu"""
    import os
    os.environ.setdefault("SECRET_KEY", "test-secret-key-for-jti-test-1234567890")
    from fasthub_core.auth.service import create_access_token, decode_access_token
    token = create_access_token({"sub": "user-123"})
    payload = decode_access_token(token)
    assert "jti" in payload
    assert len(payload["jti"]) > 10  # UUID jest długi


# === USER MODEL ===

def test_user_has_email_verified_fields():
    """User musi mieć pola is_email_verified i email_verified_at"""
    from fasthub_core.users.models import User
    assert hasattr(User, 'is_email_verified')
    assert hasattr(User, 'email_verified_at')
