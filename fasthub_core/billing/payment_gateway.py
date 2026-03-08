"""
Payment Gateway Contract — interfejs dla wszystkich bramek platniczych.

Implementacje:
- StripeGateway     -> Brief 16 (ten brief)
- PayUGateway       -> Brief 20 (przyszlosc)
- TpayGateway       -> Brief 20
- PayPalGateway     -> Brief 20

Bramki dzialaja JEDNOCZESNIE — PaymentGatewayRegistry trzyma wszystkie aktywne.
Klient koncowy widzi metody platnosci ze WSZYSTKICH aktywnych bramek.

Uzycie:
    from fasthub_core.billing.payment_gateway import PaymentGatewayRegistry

    registry = PaymentGatewayRegistry.from_config()
    methods = registry.get_available_methods()
    result = await registry.create_payment(
        gateway_id="stripe", amount=19900, currency="PLN",
        description="Plan Pro", return_url="https://app.example.com/billing/success",
    )
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class PaymentStatus(str, Enum):
    """Status platnosci — ujednolicony dla wszystkich bramek."""
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    canceled = "canceled"
    refunded = "refunded"


@dataclass
class PaymentMethod:
    """Metoda platnosci dostepna w bramce."""
    id: str             # "blik", "card", "transfer", "google_pay", "apple_pay", "paypal"
    name: str           # "BLIK", "Karta platnicza", "Przelew", "Google Pay"
    gateway_id: str     # "stripe", "payu", "tpay"
    icon: str = ""      # URL ikony lub emoji


@dataclass
class PaymentResult:
    """Wynik utworzenia platnosci."""
    success: bool
    payment_id: Optional[str] = None
    payment_url: Optional[str] = None
    gateway_id: str = ""
    raw_response: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class WebhookResult:
    """Wynik przetworzenia webhooka."""
    status: str             # "processed", "duplicate", "ignored", "error"
    event_type: str = ""
    payment_id: str = ""
    payment_status: Optional[PaymentStatus] = None
    tenant_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class PaymentGateway(ABC):
    """
    Kontrakt bramki platniczej.

    Kazda bramka implementuje te metody.
    Bramki rejestrowane w PaymentGatewayRegistry.
    """

    @property
    @abstractmethod
    def gateway_id(self) -> str:
        """Unikalny identyfikator bramki: "stripe", "payu", "tpay", "paypal"."""
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Nazwa wyswietlana: "Stripe", "PayU", "Tpay"."""
        ...

    @abstractmethod
    def get_payment_methods(self) -> List[PaymentMethod]:
        """Jakie metody platnosci obsluguje ta bramka."""
        ...

    @abstractmethod
    async def create_payment(
        self,
        amount: int,
        currency: str,
        description: str,
        return_url: str,
        cancel_url: str = "",
        method: Optional[str] = None,
        metadata: Dict[str, Any] = None,
    ) -> PaymentResult:
        """
        Utworz platnosc.

        Args:
            amount: kwota w GROSZACH (19900 = 199.00 PLN)
            currency: "PLN", "EUR", "USD"
            description: opis platnosci
            return_url: URL po udanej platnosci
            cancel_url: URL po anulowaniu
            method: metoda platnosci ("blik", "card") — None = bramka pokaze wybor
            metadata: dane do zwrocenia w webhooku (tenant_id, plan_slug, itp.)
        """
        ...

    @abstractmethod
    async def verify_payment(self, payment_id: str) -> PaymentStatus:
        """Sprawdz status platnosci."""
        ...

    @abstractmethod
    async def handle_webhook(
        self, payload: bytes, headers: Dict[str, str],
    ) -> WebhookResult:
        """Przetwoz webhook/callback z bramki."""
        ...

    @abstractmethod
    async def create_subscription(
        self,
        plan_id: str,
        amount: int,
        currency: str,
        interval: str,
        metadata: Dict[str, Any] = None,
        return_url: str = "",
        cancel_url: str = "",
    ) -> PaymentResult:
        """Utworz subskrypcje (recurring payment)."""
        ...

    @abstractmethod
    async def cancel_subscription(self, subscription_id: str) -> bool:
        """Anuluj subskrypcje. True = sukces."""
        ...

    @abstractmethod
    async def refund_payment(self, payment_id: str, amount: Optional[int] = None) -> bool:
        """Zwrot platnosci. amount=None -> pelny zwrot."""
        ...

    def is_configured(self) -> bool:
        """Czy bramka jest skonfigurowana (ma klucze API)."""
        return False
