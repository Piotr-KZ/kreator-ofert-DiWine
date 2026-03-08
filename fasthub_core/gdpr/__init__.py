"""
GDPR module — data export, anonymization, account deletion.

RODO compliance: Art. 15 (access), Art. 17 (erasure), Art. 20 (portability).
"""

from fasthub_core.gdpr.export_registry import DataExporter, ExportRegistry
from fasthub_core.gdpr.export_service import ExportService
from fasthub_core.gdpr.anonymize_service import AnonymizeService
from fasthub_core.gdpr.deletion_service import DeletionService
from fasthub_core.gdpr.models import DeletionRequest

# Register built-in exporters
from fasthub_core.gdpr.exporters import (
    UserExporter,
    BillingExporter,
    AuditExporter,
    NotificationExporter,
)

ExportRegistry.register(UserExporter())
ExportRegistry.register(BillingExporter())
ExportRegistry.register(AuditExporter())
ExportRegistry.register(NotificationExporter())

__all__ = [
    "DataExporter",
    "ExportRegistry",
    "ExportService",
    "AnonymizeService",
    "DeletionService",
    "DeletionRequest",
]
