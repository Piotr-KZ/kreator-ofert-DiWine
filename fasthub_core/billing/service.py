"""
Invoice service
Business logic for invoice operations and PDF generation
"""

import io
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fasthub_core.billing.models import Invoice
from fasthub_core.users.models import Organization


class InvoiceService:
    """Service for invoice management operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_invoice_from_stripe(
        self, stripe_invoice_data: dict, organization_id: int
    ) -> Invoice:
        """
        Create invoice from Stripe invoice data
        """
        # Check if invoice already exists
        result = await self.db.execute(
            select(Invoice).where(Invoice.stripe_invoice_id == stripe_invoice_data["id"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            return existing

        # Create new invoice
        invoice = Invoice(
            organization_id=organization_id,
            stripe_invoice_id=stripe_invoice_data["id"],
            stripe_customer_id=stripe_invoice_data.get("customer"),
            amount=stripe_invoice_data.get("amount_due", 0) / 100,
            currency=stripe_invoice_data.get("currency", "usd"),
            status=stripe_invoice_data.get("status", "draft"),
            invoice_number=stripe_invoice_data.get("number"),
            invoice_date=datetime.fromtimestamp(stripe_invoice_data["created"]),
            due_date=datetime.fromtimestamp(
                stripe_invoice_data.get("due_date", stripe_invoice_data["created"])
            ),
            paid_at=(
                datetime.fromtimestamp(stripe_invoice_data["status_transitions"]["paid_at"])
                if stripe_invoice_data.get("status_transitions", {}).get("paid_at")
                else None
            ),
            invoice_pdf_url=stripe_invoice_data.get("invoice_pdf"),
            hosted_invoice_url=stripe_invoice_data.get("hosted_invoice_url"),
        )

        self.db.add(invoice)
        await self.db.commit()
        await self.db.refresh(invoice)

        return invoice

    async def get_invoice_by_id(self, invoice_id: int) -> Optional[Invoice]:
        """Get invoice by ID"""
        result = await self.db.execute(select(Invoice).where(Invoice.id == invoice_id))
        return result.scalar_one_or_none()

    async def list_invoices_by_organization(
        self, organization_id: int, skip: int = 0, limit: int = 100
    ) -> List[Invoice]:
        """List all invoices for organization"""
        result = await self.db.execute(
            select(Invoice)
            .where(Invoice.organization_id == organization_id)
            .order_by(Invoice.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def generate_invoice_pdf(self, invoice_id: int) -> bytes:
        """
        Generate PDF for invoice
        Returns PDF as bytes
        """
        invoice = await self.get_invoice_by_id(invoice_id)
        if not invoice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

        # Get organization details
        result = await self.db.execute(
            select(Organization).where(Organization.id == invoice.organization_id)
        )
        organization = result.scalar_one_or_none()

        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
            )

        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)

        elements = []
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#1a1a1a"),
            spaceAfter=30,
        )

        elements.append(Paragraph("INVOICE", title_style))
        elements.append(Spacer(1, 0.3 * inch))

        invoice_info = [
            ["Invoice Number:", invoice.invoice_number or f"INV-{invoice.id}"],
            ["Invoice Date:", invoice.invoice_date.strftime("%Y-%m-%d")],
            ["Due Date:", invoice.due_date.strftime("%Y-%m-%d") if invoice.due_date else "N/A"],
            ["Status:", invoice.status.upper()],
        ]

        invoice_table = Table(invoice_info, colWidths=[2 * inch, 3 * inch])
        invoice_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ]
            )
        )
        elements.append(invoice_table)
        elements.append(Spacer(1, 0.5 * inch))

        elements.append(Paragraph("<b>Bill To:</b>", styles["Normal"]))
        elements.append(Spacer(1, 0.1 * inch))
        elements.append(Paragraph(organization.name, styles["Normal"]))
        elements.append(Spacer(1, 0.5 * inch))

        items_data = [
            ["Description", "Amount"],
            ["Subscription", f"${invoice.amount:.2f} {invoice.currency.upper()}"],
        ]

        items_table = Table(items_data, colWidths=[4 * inch, 2 * inch])
        items_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        elements.append(items_table)
        elements.append(Spacer(1, 0.5 * inch))

        total_data = [
            ["Total:", f"${invoice.amount:.2f} {invoice.currency.upper()}"],
        ]
        total_table = Table(total_data, colWidths=[4 * inch, 2 * inch])
        total_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 14),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ]
            )
        )
        elements.append(total_table)

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    async def mark_invoice_as_paid(
        self, invoice_id: int, paid_at: Optional[datetime] = None
    ) -> Invoice:
        """Mark invoice as paid"""
        invoice = await self.get_invoice_by_id(invoice_id)
        if not invoice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

        invoice.status = "paid"
        invoice.paid_at = paid_at or datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(invoice)

        return invoice
