"""
Core configuration — re-export from fasthub_core
Backend uses the same Settings class as fasthub_core.
"""

from fasthub_core.config import Settings, get_settings

# Backward compatibility — many backend files do:
#   from app.core.config import settings
settings = get_settings()

__all__ = ["Settings", "get_settings", "settings"]
