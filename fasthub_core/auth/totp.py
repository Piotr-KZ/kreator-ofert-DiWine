"""
TOTP (Time-based One-Time Password) — RFC 6238.

Kompatybilny z: Google Authenticator, Authy, Microsoft Authenticator, 1Password.
"""

import io
import json
import base64
import secrets
import logging
from typing import List, Optional, Tuple

import pyotp

logger = logging.getLogger(__name__)


class TOTPService:
    """Serwis obsługi 2FA TOTP."""

    BACKUP_CODE_COUNT = 10
    BACKUP_CODE_LENGTH = 8
    ISSUER_NAME = "WebCreator"

    def __init__(self, issuer_name: str = None):
        if issuer_name:
            self.ISSUER_NAME = issuer_name

    def generate_secret(self) -> str:
        """Generuj nowy TOTP secret (base32, 32 znaki)."""
        return pyotp.random_base32()

    def generate_provisioning_uri(self, secret: str, user_email: str) -> str:
        """Generuj URI do QR code (otpauth://totp/...)."""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=user_email,
            issuer_name=self.ISSUER_NAME,
        )

    def generate_qr_code_base64(self, provisioning_uri: str) -> str:
        """Generuj QR code jako base64 PNG."""
        import qrcode

        qr = qrcode.QRCode(version=1, box_size=6, border=2)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")

        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def verify_code(self, secret: str, code: str) -> bool:
        """Weryfikuj 6-cyfrowy kod TOTP (±1 window = 30s tolerance)."""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)

    def generate_backup_codes(self) -> List[str]:
        """Generuj 10 jednorazowych kodów zapasowych (8 znaków, uppercase hex)."""
        return [
            secrets.token_hex(self.BACKUP_CODE_LENGTH // 2).upper()
            for _ in range(self.BACKUP_CODE_COUNT)
        ]

    def verify_backup_code(self, stored_codes_json: str, code: str) -> Tuple[bool, str]:
        """
        Weryfikuj backup code. Jeśli poprawny — usuń z listy.

        Returns:
            (is_valid, updated_codes_json)
        """
        try:
            codes = json.loads(stored_codes_json)
        except (json.JSONDecodeError, TypeError):
            return False, stored_codes_json or "[]"

        clean_code = code.strip().upper().replace("-", "").replace(" ", "")

        if clean_code in codes:
            codes.remove(clean_code)
            return True, json.dumps(codes)

        return False, stored_codes_json
