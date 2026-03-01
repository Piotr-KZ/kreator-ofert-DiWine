"""
Walidacja siły hasła.

Zasady:
- Minimum 8 znaków
- Co najmniej 1 wielka litera
- Co najmniej 1 mała litera
- Co najmniej 1 cyfra
- Opcjonalnie: 1 znak specjalny (konfigurowalny)

Zwraca listę błędów (pusta = hasło OK).
"""

import re
from typing import List, Optional


class PasswordValidator:
    """
    Walidator siły hasła.

    Użycie:
        validator = PasswordValidator()
        errors = validator.validate("abc")
        # errors = ["Minimum 8 znaków (masz 3)", "Co najmniej 1 wielka litera (A-Z)", "Co najmniej 1 cyfra (0-9)"]

        errors = validator.validate("SecurePass123")
        # errors = [] (OK)
    """

    def __init__(
        self,
        min_length: int = 8,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digit: bool = True,
        require_special: bool = False,
        max_length: int = 128,
    ):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit = require_digit
        self.require_special = require_special
        self.max_length = max_length

    def validate(self, password: str) -> List[str]:
        """
        Waliduj hasło. Zwraca listę błędów.
        Pusta lista = hasło spełnia wymagania.
        """
        errors = []

        if len(password) < self.min_length:
            errors.append(f"Minimum {self.min_length} znaków (masz {len(password)})")

        if len(password) > self.max_length:
            errors.append(f"Maximum {self.max_length} znaków")

        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Co najmniej 1 wielka litera (A-Z)")

        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Co najmniej 1 mała litera (a-z)")

        if self.require_digit and not re.search(r'\d', password):
            errors.append("Co najmniej 1 cyfra (0-9)")

        if self.require_special and not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
            errors.append("Co najmniej 1 znak specjalny (!@#$%...)")

        return errors

    def get_strength(self, password: str) -> str:
        """
        Ocena siły hasła: 'weak', 'medium', 'strong'.
        Informacyjna — nie blokuje.
        """
        score = 0
        if len(password) >= 8: score += 1
        if len(password) >= 12: score += 1
        if re.search(r'[A-Z]', password): score += 1
        if re.search(r'[a-z]', password): score += 1
        if re.search(r'\d', password): score += 1
        if re.search(r'[!@#$%^&*]', password): score += 1

        if score <= 2: return "weak"
        if score <= 4: return "medium"
        return "strong"


# === SINGLETON — domyślna instancja ===

_default_validator: Optional[PasswordValidator] = None


def get_password_validator() -> PasswordValidator:
    """Zwraca domyślny walidator"""
    global _default_validator
    if _default_validator is None:
        _default_validator = PasswordValidator()
    return _default_validator


def validate_password(password: str) -> List[str]:
    """Convenience function — waliduj hasło domyślnym walidatorem"""
    return get_password_validator().validate(password)
