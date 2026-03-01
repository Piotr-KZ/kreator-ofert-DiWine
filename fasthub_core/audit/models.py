"""
Rozbudowany AuditLog — pełna historia zmian z before/after.

Śledzi: kto, co, kiedy, skąd, i co dokładnie się zmieniło.
Wspiera: impersonation tracking, IP/User-Agent, retention policy.
"""

from sqlalchemy import Column, String, Text, DateTime, JSON, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from fasthub_core.db.session import Base


class AuditLog(Base):
    """
    Jeden wpis w logu audytu.

    Przykład wpisu:
    {
        user_id: "uuid-jan-kowalski",
        organization_id: "uuid-budimex",
        action: "update",
        resource_type: "subscription",
        resource_id: "uuid-sub-123",
        changes_before: {"plan": "pro", "seats": 10},
        changes_after: {"plan": "enterprise", "seats": 50},
        summary: "Zmieniono plan: pro -> enterprise; seats: 10 -> 50",
        ip_address: "192.168.1.50",
        user_agent: "Mozilla/5.0 ...",
        extra_data: {"reason": "upgrade request from CEO"},
    }
    """
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # KTO
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    user_email = Column(String(255), nullable=True)
    impersonated_by = Column(UUID(as_uuid=True), nullable=True)

    # GDZIE
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)

    # CO
    action = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)
    resource_id = Column(String(255), nullable=True)

    # CO SIĘ ZMIENIŁO
    changes_before = Column(JSON, nullable=True)
    changes_after = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)

    # SKĄD
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # DODATKOWE
    extra_data = Column("metadata", JSON, nullable=True)

    # KIEDY
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Indeksy dla szybkiego wyszukiwania
    __table_args__ = (
        Index("ix_audit_org_created", "organization_id", "created_at"),
        Index("ix_audit_user_created", "user_id", "created_at"),
        Index("ix_audit_resource", "resource_type", "resource_id"),
    )

    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_id}>"
