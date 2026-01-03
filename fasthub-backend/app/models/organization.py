"""
Organization model
Represents organizations in multi-tenant architecture
"""

from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Organization(BaseModel):
    """
    Organization model for multi-tenancy
    Each organization has multiple users and subscriptions
    """

    __tablename__ = "organizations"

    # Basic fields
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)

    # Organization details
    type = Column(String(50), nullable=True)  # 'business' or 'individual'
    nip = Column(String(50), nullable=True)  # Tax ID
    phone = Column(String(50), nullable=True)

    # Billing address
    billing_street = Column(String(255), nullable=True)
    billing_city = Column(String(100), nullable=True)
    billing_postal_code = Column(String(20), nullable=True)
    billing_country = Column(String(100), nullable=True)

    # Onboarding status
    is_complete = Column(Boolean, default=False, nullable=False)

    # Owner (nullable to break circular dependency)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)

    # Stripe integration
    stripe_customer_id = Column(String(255), unique=True, nullable=True)

    # Relationships
    members = relationship("Member", back_populates="organization", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="organization")
    invoices = relationship("Invoice", back_populates="organization")

    def __repr__(self):
        return f"<Organization {self.name}>"
