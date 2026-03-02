"""
FastHub Core — Kontrakt API v2.0

Ten plik definiuje interfejsy które FastHub GWARANTUJE dostarczyć.
Aplikacje (AutoFlow, FastCRM, etc.) polegają na tych interfejsach.

ZASADY:
1. Nie zmieniaj sygnatur funkcji bez podniesienia MAJOR version (v3.0)
2. Nowe funkcje DODAWAJ — nie zmieniaj istniejących
3. Usuwanie funkcji — minimum 1 wersja z deprecation warning
"""

from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Set, Dict, Any
from uuid import UUID
from datetime import datetime


class AuthContract(ABC):
    """
    Kontrakt autentykacji — logowanie, tokeny, hasła.
    AutoFlow potrzebuje tego żeby wiedzieć kto jest zalogowany.
    """

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Zamienia hasło na bezpieczny hash (bcrypt)"""
        ...

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Sprawdza czy podane hasło zgadza się z hashem"""
        ...

    @abstractmethod
    def create_access_token(self, user_id: str, organization_id: Optional[str] = None, extra_data: Optional[Dict] = None) -> str:
        """Tworzy krótkotrwały token dostępu (JWT). Czas życia: ~30 min."""
        ...

    @abstractmethod
    def create_refresh_token(self, user_id: str) -> str:
        """Tworzy długotrwały token odświeżania. Czas życia: ~7 dni."""
        ...

    @abstractmethod
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Dekoduje token JWT. Zwraca payload z user_id, exp, type albo None."""
        ...

    @abstractmethod
    async def blacklist_token(self, token: str, expires_at: datetime) -> bool:
        """Unieważnia token (dodaje do czarnej listy w Redis)"""
        ...

    @abstractmethod
    async def is_token_blacklisted(self, token: str) -> bool:
        """Sprawdza czy token jest na czarnej liście"""
        ...


class UserContract(ABC):
    """
    Kontrakt użytkowników — informacje o ludziach i firmach.
    AutoFlow potrzebuje tego do: dropdown akceptacji, identyfikacja usera.
    """

    @abstractmethod
    async def get_current_user(self, token: str, db) -> Any:
        """
        Zwraca dane zalogowanego użytkownika na podstawie tokenu.
        Zwraca: obiekt User z polami id, email, full_name, is_active
        """
        ...

    @abstractmethod
    async def get_user(self, user_id: str, db) -> Optional[Any]:
        """Zwraca dane użytkownika po ID"""
        ...

    @abstractmethod
    async def list_organization_users(self, organization_id: str, db) -> List[Dict[str, Any]]:
        """
        Lista wszystkich użytkowników w organizacji.
        AutoFlow używa do: dropdown "kto ma zatwierdzić proces"
        Zwraca: [{id, email, full_name, role}, ...]
        """
        ...

    @abstractmethod
    async def get_user_role(self, user_id: str, organization_id: str, db) -> Optional[str]:
        """Zwraca rolę użytkownika w organizacji (np. 'admin', 'viewer')"""
        ...


class PermissionContract(ABC):
    """
    Kontrakt uprawnień — RBAC z rolami i granularnymi permissions.
    Zaimplementowany w Fazie 1.2 (Advanced RBAC).
    AutoFlow potrzebuje: sprawdzanie czy user może edytować/wykonać proces.
    """

    @abstractmethod
    async def check_permission(self, user_id: str, organization_id: str, permission: str, db) -> bool:
        """
        Sprawdza czy user ma dane uprawnienie w organizacji.
        Przykłady permission: "processes.edit", "processes.execute", "billing.view"
        """
        ...

    @abstractmethod
    async def get_user_permissions(self, user_id: str, organization_id: str, db) -> Set[str]:
        """Zwraca zestaw wszystkich uprawnień usera w organizacji"""
        ...

    @abstractmethod
    async def assign_role(self, user_id: str, role_id: str, organization_id: str, db) -> None:
        """Przypisuje rolę użytkownikowi w organizacji"""
        ...

    @abstractmethod
    async def create_custom_role(self, organization_id: str, name: str, permissions: List[str], db) -> Any:
        """Tworzy nową rolę custom w organizacji z podanymi uprawnieniami"""
        ...

    @abstractmethod
    async def register_app_permissions(self, permissions: Dict[str, List[tuple]], db) -> None:
        """Aplikacja (AutoFlow) rejestruje swoje permissions przy starcie"""
        ...


class BillingContract(ABC):
    """
    Kontrakt rozliczeń — plany, limity, zużycie.
    AutoFlow potrzebuje: sprawdzanie limitów (ile procesów może mieć firma).
    """

    @abstractmethod
    async def get_subscription(self, organization_id: str, db) -> Optional[Dict[str, Any]]:
        """
        Zwraca aktualną subskrypcję organizacji.
        Zwraca: {plan_name, status, current_period_start, current_period_end}
        """
        ...

    @abstractmethod
    async def check_limit(self, organization_id: str, resource: str, current_usage: int, db) -> bool:
        """
        Sprawdza czy organizacja nie przekroczyła limitu.
        resource: "processes", "ai_calls", "integrations", "members"
        Zwraca: True jeśli OK (nie przekroczono), False jeśli limit osiągnięty
        """
        ...

    @abstractmethod
    async def record_usage(self, organization_id: str, resource: str, amount: int, db) -> None:
        """
        Zapisuje zużycie zasobu (np. +1 wywołanie AI, +1 wykonanie procesu).
        Używane do mierzenia zużycia i egzekwowania limitów.
        """
        ...


class AuditContract(ABC):
    """
    Kontrakt audytu — historia zmian.
    AutoFlow potrzebuje: logowanie zmian w procesach.
    """

    @abstractmethod
    async def log_action(
        self,
        user_id: str,
        organization_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None,
        before: Optional[Dict[str, Any]] = None,
        after: Optional[Dict[str, Any]] = None,
        db=None,
    ) -> None:
        """
        Zapisuje akcję w logu audytu.
        action: "create", "update", "delete", "execute", "approve", "reject"
        resource_type: "process", "integration", "user", "subscription"
        before/after: stan zasobu PRZED i PO zmianie (opcjonalne)
        """
        ...

    @abstractmethod
    async def get_audit_logs(
        self,
        organization_id: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        db=None,
    ) -> List[Dict[str, Any]]:
        """Pobiera logi audytu z filtrami"""
        ...


class NotificationContract(ABC):
    """
    Kontrakt powiadomień — wysyłanie powiadomień do użytkowników.
    AutoFlow potrzebuje: informowanie o zakończeniu procesu, oczekującej akceptacji.
    UWAGA: Ten kontrakt będzie DODANY w FastHub v2.0 (jeszcze nie zaimplementowany).
    """

    @abstractmethod
    async def send_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Wysyła powiadomienie do użytkownika (in-app + opcjonalnie email).
        notification_type: "info", "success", "warning", "error", "approval_request"
        """
        ...

    @abstractmethod
    async def send_email(
        self,
        to_email: str,
        template: str,
        variables: Dict[str, Any],
    ) -> None:
        """
        Wysyła email na podstawie szablonu.
        template: "welcome", "password_reset", "approval_request", "execution_complete"
        """
        ...


class EventBusContract(ABC):
    """
    Kontrakt Event Bus — komunikacja eventowa między modułami.
    AutoFlow potrzebuje: pub/sub z wildcard handlers.
    Planowany: FastHub v2.1. Implementacja przyjdzie z migracją AutoFlow.
    """

    @abstractmethod
    async def emit(self, event_type: str, data: dict) -> None:
        """
        Emituje event do wszystkich subskrybentów.
        event_type: "user.created", "process.completed", "billing.updated"
        data: payload eventu (dict)
        """
        ...

    @abstractmethod
    async def on(self, event_pattern: str, handler: Callable) -> None:
        """
        Rejestruje handler na wzorzec eventu.
        event_pattern: "user.*", "process.completed", "billing.*"
        handler: async callable(event_type, data)
        Obsługuje wildcard matching (np. "user.*" łapie "user.created", "user.deleted").
        """
        ...

    @abstractmethod
    async def off(self, event_pattern: str, handler: Callable) -> None:
        """Wyrejestrowuje handler z wzorca eventu."""
        ...


class DatabaseContract(ABC):
    """
    Kontrakt bazy danych — sesja, engine.
    Każda aplikacja potrzebuje dostępu do bazy danych.
    """

    @abstractmethod
    async def get_db_session(self):
        """
        Zwraca async session do bazy danych.
        Używane jako FastAPI dependency: Depends(get_db)
        """
        ...

    @abstractmethod
    def get_engine(self):
        """Zwraca SQLAlchemy async engine"""
        ...
