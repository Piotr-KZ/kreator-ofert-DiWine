"""
Maintenance Tasks — automatyczne czyszczenie (cron).

Zarejestrowane w BaseWorkerSettings.cron_jobs:
- cleanup_expired_tokens: co godzinę
- reset_monthly_usage: 1-szego o 0:05
- cleanup_old_audit_entries: co tydzień
- cleanup_old_notifications: co tydzień

Każdy task jest odporny na brak modułów (ImportError -> skip).
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict

logger = logging.getLogger(__name__)


async def cleanup_expired_tokens(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """Wyczyść wygasłe tokeny JWT z blacklisty."""
    deleted = 0
    try:
        from fasthub_core.db.session import async_session_maker
        from fasthub_core.auth.models import TokenBlacklist
        from sqlalchemy import delete

        async with async_session_maker() as db:
            result = await db.execute(
                delete(TokenBlacklist).where(TokenBlacklist.expires_at < datetime.utcnow())
            )
            deleted = result.rowcount
            await db.commit()
    except ImportError:
        logger.debug("[MAINT] TokenBlacklist not available — skip")
    except Exception as e:
        logger.error(f"[MAINT] cleanup_expired_tokens: {e}")

    logger.info(f"[MAINT] cleanup_expired_tokens: {deleted} removed")
    return {"deleted": deleted}


async def reset_monthly_usage(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """Reset miesięcznych counterów billing (nowy okres, stary zostaje jako historia)."""
    reset_count = 0
    try:
        from fasthub_core.db.session import async_session_maker
        from fasthub_core.billing.service import BillingService

        async with async_session_maker() as db:
            service = BillingService(db)
            reset_count = await service.reset_monthly_usage()
            await db.commit()
    except ImportError:
        logger.debug("[MAINT] BillingService not available — skip")
    except Exception as e:
        logger.error(f"[MAINT] reset_monthly_usage: {e}")

    logger.info(f"[MAINT] reset_monthly_usage: {reset_count} tenants reset")
    return {"reset_count": reset_count}


async def cleanup_old_audit_entries(ctx: Dict[str, Any], days: int = 180) -> Dict[str, Any]:
    """Usuń stare wpisy audytu (level=info). Error/critical zachowaj dłużej."""
    deleted = 0
    try:
        from fasthub_core.db.session import async_session_maker
        from fasthub_core.audit.models import AuditEntry
        from sqlalchemy import delete, and_

        cutoff = datetime.utcnow() - timedelta(days=days)
        async with async_session_maker() as db:
            result = await db.execute(
                delete(AuditEntry).where(
                    and_(
                        AuditEntry.created_at < cutoff,
                        AuditEntry.action_type.notin_(["error", "security", "critical"]),
                    )
                )
            )
            deleted = result.rowcount
            await db.commit()
    except ImportError:
        logger.debug("[MAINT] AuditEntry not available — skip")
    except Exception as e:
        logger.error(f"[MAINT] cleanup_old_audit_entries: {e}")

    logger.info(f"[MAINT] cleanup_old_audit_entries: {deleted} removed (>{days} days)")
    return {"deleted": deleted, "cutoff_days": days}


async def cleanup_old_notifications(ctx: Dict[str, Any], days: int = 90) -> Dict[str, Any]:
    """Usuń przeczytane powiadomienia starsze niż N dni."""
    deleted = 0
    try:
        from fasthub_core.db.session import async_session_maker
        from fasthub_core.notifications.models import Notification
        from sqlalchemy import delete, and_

        cutoff = datetime.utcnow() - timedelta(days=days)
        async with async_session_maker() as db:
            result = await db.execute(
                delete(Notification).where(
                    and_(
                        Notification.created_at < cutoff,
                        Notification.is_read == True,
                    )
                )
            )
            deleted = result.rowcount
            await db.commit()
    except ImportError:
        logger.debug("[MAINT] Notification model not available — skip")
    except Exception as e:
        logger.error(f"[MAINT] cleanup_old_notifications: {e}")

    logger.info(f"[MAINT] cleanup_old_notifications: {deleted} removed (>{days} days)")
    return {"deleted": deleted, "cutoff_days": days}
