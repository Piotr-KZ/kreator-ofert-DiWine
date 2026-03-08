"""
ExportService — GDPR Art. 15/20 data export.

Collects data from all registered exporters, packages into ZIP.
"""

import io
import json
import zipfile
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from fasthub_core.gdpr.export_registry import ExportRegistry


class ExportService:
    """Collect user data from all exporters and generate ZIP."""

    def __init__(self, db):
        self.db = db

    async def export_user_data(self, user_id: UUID) -> Dict[str, Any]:
        """Collect data from all registered exporters."""
        data = {}
        for exporter in ExportRegistry.get_exporters():
            name = await exporter.get_export_name()
            module_data = await exporter.export_user_data(user_id, self.db)
            data[name] = module_data
        return data

    async def generate_zip(
        self,
        user_id: UUID,
        user_email: Optional[str] = None,
    ) -> bytes:
        """Generate ZIP with all user data as JSON files."""
        data = await self.export_user_data(user_id)

        # Add metadata
        data["metadata"] = {
            "exported_at": datetime.utcnow().isoformat(),
            "user_id": str(user_id),
            "user_email": user_email,
            "format_version": "1.0",
            "modules": list(data.keys()),
        }

        # Build ZIP in memory
        slug = (user_email or str(user_id)).split("@")[0]
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        folder = f"export_{slug}_{date_str}"

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, content in data.items():
                json_bytes = json.dumps(content, indent=2, ensure_ascii=False).encode("utf-8")
                zf.writestr(f"{folder}/{name}.json", json_bytes)

        return buf.getvalue()
