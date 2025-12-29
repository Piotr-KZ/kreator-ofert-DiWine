"""
Invoice model
Manages invoices from Stripe and Fakturownia
"""

import enum

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class InvoiceStatus(str, enum.Enum):
    """Invoice status enum"""

    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"


class Invoice(BaseModel):
    """
    Invoice model
    Can be generated from Stripe or manually created
    """

    __tablename__ = "invoices"

    # Organization relationship
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="invoices")

    # Invoice details
    invoice_number = Column(String(255), unique=True, nullable=False)

    # External IDs
    stripe_invoice_id = Column(String(255), unique=True, nullable=True)
    fakturownia_id = Column(String(255), unique=True, nullable=True)

    # Status
    status = Column(SQLEnum(InvoiceStatus), nullable=False, default=InvoiceStatus.DRAFT)

    # Amount
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)

    # Description
    description = Column(Text, nullable=True)

    # PDF
    pdf_url = Column(Text, nullable=True)

    # Dates
    due_date = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Invoice {self.invoice_number} - {self.status}>"
