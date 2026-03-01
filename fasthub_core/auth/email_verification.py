"""
Weryfikacja emaila po rejestracji.

Przepływ:
1. User rejestruje się -> konto tworzone z is_email_verified=False
2. System generuje token weryfikacyjny (JWT, 24h ważność)
3. System wysyła email z linkiem: {BASE_URL}/verify-email?token=xxx
4. User klika link -> endpoint verify_email dekoduje token -> ustawia is_email_verified=True
5. (Opcjonalnie) User może poprosić o ponowne wysłanie: resend_verification

WAŻNE: Wysyłka emaila to OSOBNY serwis (notifications).
Ten moduł TYLKO generuje tokeny i weryfikuje — nie wysyła maili.
"""

from datetime import datetime, timedelta
from typing import Optional


class EmailVerificationService:
    """Serwis weryfikacji emaila"""

    def __init__(self, db=None, secret_key: str = "default", base_url: str = "http://localhost:3000"):
        self.db = db
        self.secret_key = secret_key
        self.base_url = base_url
        self.token_expire_hours = 24

    def generate_verification_token(self, user_id: str, email: str) -> str:
        """
        Generuje token JWT do weryfikacji emaila.
        Token zawiera: user_id, email, typ "email_verify", expire 24h.
        """
        from jose import jwt

        payload = {
            "sub": user_id,
            "email": email,
            "type": "email_verify",
            "exp": datetime.utcnow() + timedelta(hours=self.token_expire_hours),
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def decode_verification_token(self, token: str) -> Optional[dict]:
        """
        Dekoduje token weryfikacyjny.
        Zwraca {"sub": user_id, "email": email} lub None jeśli token nieważny.
        """
        from jose import jwt, JWTError

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            if payload.get("type") != "email_verify":
                return None
            return payload
        except JWTError:
            return None

    def get_verification_url(self, token: str) -> str:
        """Zwraca pełny URL do weryfikacji"""
        return f"{self.base_url}/verify-email?token={token}"

    async def verify_email(self, token: str) -> dict:
        """
        Weryfikuje email na podstawie tokenu.

        Zwraca:
        - {"status": "verified", "email": "..."} — sukces
        - {"status": "invalid_token"} — token nieważny/wygasły
        - {"status": "already_verified"} — email już zweryfikowany
        - {"status": "user_not_found"} — user nie istnieje
        """
        payload = self.decode_verification_token(token)
        if not payload:
            return {"status": "invalid_token"}

        user_id = payload.get("sub")
        email = payload.get("email")

        from sqlalchemy import select
        from fasthub_core.users.models import User

        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return {"status": "user_not_found"}

        if getattr(user, 'is_email_verified', False):
            return {"status": "already_verified", "email": email}

        user.is_email_verified = True
        user.email_verified_at = datetime.utcnow()
        await self.db.commit()

        return {"status": "verified", "email": email}

    async def resend_verification(self, email: str) -> Optional[str]:
        """
        Generuje nowy token dla usera z podanym emailem.
        Zwraca URL lub None jeśli user nie istnieje / już zweryfikowany.
        """
        from sqlalchemy import select
        from fasthub_core.users.models import User

        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None
        if getattr(user, 'is_email_verified', False):
            return None

        token = self.generate_verification_token(str(user.id), email)
        return self.get_verification_url(token)
