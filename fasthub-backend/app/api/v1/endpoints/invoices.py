"""
Invoices endpoints
API routes for invoice operations
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.invoice import InvoiceListResponse, InvoiceResponse
from app.services.invoice_service import InvoiceService

router = APIRouter()


@router.get("/", response_model=List[InvoiceResponse])
async def list_invoices(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all invoices for current user's organization

    Returns paginated list of invoices.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User has no organization"
        )

    invoice_service = InvoiceService(db)
    invoices = await invoice_service.list_invoices_by_organization(
        organization_id=current_user.organization_id, skip=skip, limit=limit
    )

    return invoices


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get invoice by ID

    Returns invoice details.
    """
    invoice_service = InvoiceService(db)
    invoice = await invoice_service.get_invoice_by_id(invoice_id)

    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    # Check if user has access to this invoice
    if invoice.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this invoice"
        )

    return invoice


@router.get("/{invoice_id}/pdf")
async def download_invoice_pdf(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Download invoice as PDF

    Generates and returns PDF file.
    """
    invoice_service = InvoiceService(db)
    invoice = await invoice_service.get_invoice_by_id(invoice_id)

    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    # Check if user has access to this invoice
    if invoice.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this invoice"
        )

    # Generate PDF
    pdf_bytes = await invoice_service.generate_invoice_pdf(invoice_id)

    # Return PDF as response
    filename = f"invoice_{invoice.invoice_number or invoice.id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
