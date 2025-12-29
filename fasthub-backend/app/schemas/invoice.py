"""
Invoice schemas (DTOs)
Pydantic models for invoice data
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class InvoiceBase(BaseModel):
    """Base invoice schema"""

    amount: float
    currency: str
    status: str


class InvoiceResponse(InvoiceBase):
    """Schema for invoice response"""

    id: int
    organization_id: int
    stripe_invoice_id: Optional[str]
    stripe_customer_id: Optional[str]
    invoice_number: Optional[str]
    invoice_date: datetime
    due_date: Optional[datetime]
    paid_at: Optional[datetime]
    invoice_pdf_url: Optional[str]
    hosted_invoice_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvoiceListResponse(BaseModel):
    """Schema for invoice list response"""

    invoices: list[InvoiceResponse]
    total: int
    skip: int
    limit: int
