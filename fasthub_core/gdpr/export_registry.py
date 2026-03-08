"""
Export Registry — pluggable data exporters for GDPR Art. 15/20.

Each module registers its exporter. Apps (AutoFlow etc.) add their own.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from uuid import UUID


class DataExporter(ABC):
    """Base class for per-module data exporters."""

    @abstractmethod
    async def export_user_data(self, user_id: UUID, db) -> Dict[str, Any]:
        """Return all data for this user from this module."""
        ...

    @abstractmethod
    async def get_export_name(self) -> str:
        """File name in ZIP (e.g. 'audit_log')."""
        ...


class ExportRegistry:
    """Singleton registry of data exporters."""

    _exporters: List[DataExporter] = []

    @classmethod
    def register(cls, exporter: DataExporter) -> None:
        """Register a new exporter (idempotent by class name)."""
        existing = {type(e).__name__ for e in cls._exporters}
        if type(exporter).__name__ not in existing:
            cls._exporters.append(exporter)

    @classmethod
    def get_exporters(cls) -> List[DataExporter]:
        return list(cls._exporters)

    @classmethod
    def clear(cls) -> None:
        """Clear all exporters (for testing)."""
        cls._exporters = []
