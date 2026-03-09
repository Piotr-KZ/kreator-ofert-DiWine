"""
Payment model — czytelna historia platnosci dla klienta.

Roznica vs BillingEvent: BillingEvent to audit trail (wewnetrzny log).
Payment to historia platnosci widoczna w panelu uzytkownika.
"""

from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from fasthub_core.db.base import BaseModel


class Payment(BaseModel):
    """Pojedyncza platnosc — widoczna dla uzytkownika."""
    __tablename__ = "payments"

    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    subscription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id"),
        nullable=True,
    )

    # Kwota
    amount = Column(Integer, nullable=False)  # W groszach (19900 = 199.00 PLN)
    currency = Column(String(3), default="PLN", nullable=False)

    # Bramka
    gateway_id = Column(String(50), nullable=False)
    gateway_payment_id = Column(String(255), nullable=True)
    payment_method = Column(String(50), nullable=True)
    payment_method_details = Column(String(255), nullable=True)

    # Status
    status = Column(String(50), nullable=False)  # pending, completed, failed, refunded

    # Opis
    description = Column(String(500), nullable=True)

    # Daty
    completed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    refunded_at = Column(DateTime, nullable=True)

    # Powiazanie z faktura
    invoice_id = Column(
        UUID(as_uuid=True),
        ForeignKey("invoices.id"),
        nullable=True,
    )
