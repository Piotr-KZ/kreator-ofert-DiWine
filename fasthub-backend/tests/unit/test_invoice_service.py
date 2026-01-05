import pytest
from app.services.invoice_service import InvoiceService
from app.models.invoice import Invoice, InvoiceStatus

@pytest.fixture
def invoice_service():
    return InvoiceService()

@pytest.mark.asyncio
async def test_create_invoice(db_session, invoice_service, test_organization, test_subscription):
    """Test invoice creation"""
    invoice = await invoice_service.create(
        db_session,
        organization_id=test_organization.id,
        subscription_id=test_subscription.id,
        amount=99.00,
        currency="USD"
    )
    assert invoice.amount == 99.00
    assert invoice.status == InvoiceStatus.PENDING

@pytest.mark.asyncio
async def test_mark_invoice_paid(db_session, invoice_service, test_invoice):
    """Test marking invoice as paid"""
    paid = await invoice_service.mark_paid(
        db_session,
        test_invoice.id,
        stripe_payment_intent_id="pi_123"
    )
    assert paid.status == InvoiceStatus.PAID
    assert paid.stripe_payment_intent_id == "pi_123"

@pytest.mark.asyncio
async def test_mark_invoice_failed(db_session, invoice_service, test_invoice):
    """Test marking invoice as failed"""
    failed = await invoice_service.mark_failed(db_session, test_invoice.id)
    assert failed.status == InvoiceStatus.FAILED

@pytest.mark.asyncio
async def test_get_invoices_by_organization(db_session, invoice_service, test_organization):
    """Test fetching organization invoices"""
    # Create 3 invoices
    await invoice_service.create(db_session, test_organization.id, None, 10.00, "USD")
    await invoice_service.create(db_session, test_organization.id, None, 20.00, "USD")
    await invoice_service.create(db_session, test_organization.id, None, 30.00, "USD")
    
    invoices = await invoice_service.get_by_organization(db_session, test_organization.id)
    assert len(invoices) == 3

@pytest.mark.asyncio
async def test_generate_invoice_pdf(invoice_service, test_invoice):
    """Test PDF generation (mock)"""
    # Mock PDF generation
    pdf_bytes = await invoice_service.generate_pdf(test_invoice)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
