"""
Payment Gateway Registry — rejestr aktywnych bramek (wiele jednoczesnie).

Config:
    STRIPE_SECRET_KEY=sk_xxx       <- klucze per bramka
    PAYU_POS_ID=xxx                <- (przyszlosc Brief 20)

Uzycie:
    registry = PaymentGatewayRegistry()
    registry.register(StripeGateway())

    # Albo automatycznie z config:
    registry = PaymentGatewayRegistry.from_config()

    methods = registry.get_available_methods()
    result = await registry.create_payment("stripe", amount=19900, ...)
    result = await registry.handle_webhook("stripe", payload, headers)
"""

import logging
from typing import Dict, List, Optional

from fasthub_core.billing.payment_gateway import (
    PaymentGateway, PaymentMethod, PaymentResult, WebhookResult,
)

logger = logging.getLogger(__name__)


class PaymentGatewayRegistry:
    """Rejestr bramek platniczych — wiele jednoczesnie."""

    def __init__(self):
        self._gateways: Dict[str, PaymentGateway] = {}

    def register(self, gateway: PaymentGateway) -> None:
        """Zarejestruj bramke. Tylko jesli skonfigurowana (ma klucze API)."""
        if gateway.is_configured():
            self._gateways[gateway.gateway_id] = gateway
            logger.info(f"Payment gateway registered: {gateway.gateway_id} ({gateway.display_name})")
        else:
            logger.debug(f"Payment gateway skipped (not configured): {gateway.gateway_id}")

    def get_gateway(self, gateway_id: str) -> Optional[PaymentGateway]:
        """Pobierz bramke po ID."""
        return self._gateways.get(gateway_id)

    def get_active_gateways(self) -> List[PaymentGateway]:
        """Lista aktywnych (skonfigurowanych) bramek."""
        return list(self._gateways.values())

    def get_available_methods(self) -> List[PaymentMethod]:
        """
        Wszystkie metody platnosci ze WSZYSTKICH aktywnych bramek.

        Deduplikacja — jesli BLIK jest i w PayU i w Stripe,
        pokaz tylko raz (z pierwszej zarejestrowanej bramki).
        """
        methods = []
        seen_ids = set()

        for gateway in self._gateways.values():
            for method in gateway.get_payment_methods():
                if method.id not in seen_ids:
                    methods.append(method)
                    seen_ids.add(method.id)

        return methods

    def get_methods_with_gateways(self) -> List[Dict]:
        """
        Metody platnosci z informacja ktora bramka obsluguje.

        Dla frontendu — zeby wiedziec do ktorej bramki wyslac platnosc.
        Returns:
            [{"method": PaymentMethod, "gateways": ["payu", "stripe"]}]
        """
        method_map: Dict[str, Dict] = {}

        for gateway in self._gateways.values():
            for method in gateway.get_payment_methods():
                if method.id not in method_map:
                    method_map[method.id] = {
                        "method": method,
                        "gateways": [],
                    }
                method_map[method.id]["gateways"].append(gateway.gateway_id)

        return list(method_map.values())

    async def create_payment(
        self, gateway_id: str, **kwargs,
    ) -> PaymentResult:
        """Stworz platnosc przez wskazana bramke."""
        gateway = self._gateways.get(gateway_id)
        if not gateway:
            return PaymentResult(
                success=False,
                error=f"Gateway '{gateway_id}' not available. Active: {list(self._gateways.keys())}",
            )
        return await gateway.create_payment(**kwargs)

    async def handle_webhook(
        self, gateway_id: str, payload: bytes, headers: Dict[str, str],
    ) -> WebhookResult:
        """Route webhook do wlasciwej bramki."""
        gateway = self._gateways.get(gateway_id)
        if not gateway:
            return WebhookResult(status="ignored", event_type=f"unknown_gateway:{gateway_id}")
        return await gateway.handle_webhook(payload, headers)

    @classmethod
    def from_config(cls) -> "PaymentGatewayRegistry":
        """
        Stworz registry z konfiguracji.
        Automatycznie rejestruje bramki ktore maja klucze API w env.
        """
        registry = cls()

        try:
            from fasthub_core.billing.gateways.stripe_gateway import StripeGateway
            registry.register(StripeGateway())
        except ImportError:
            pass

        # Przyszle bramki (Brief 20):
        # try:
        #     from fasthub_core.billing.gateways.payu_gateway import PayUGateway
        #     registry.register(PayUGateway())
        # except ImportError:
        #     pass

        active = [g.gateway_id for g in registry.get_active_gateways()]
        logger.info(f"Payment gateways active: {active}")

        return registry


# Singleton
_registry: Optional[PaymentGatewayRegistry] = None


def get_payment_registry() -> PaymentGatewayRegistry:
    """Singleton — zwroc globalny registry."""
    global _registry
    if _registry is None:
        _registry = PaymentGatewayRegistry.from_config()
    return _registry
