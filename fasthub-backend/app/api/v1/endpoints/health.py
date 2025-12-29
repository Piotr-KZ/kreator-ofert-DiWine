"""
Health check endpoints
System health and readiness checks
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

# Store start time for uptime calculation
START_TIME = time.time()


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Basic health check

    Returns 200 if service is running.
    No dependencies checked - use /ready for full readiness check.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Readiness check with dependency validation

    Checks:
    - Database connection
    - Redis connection (if configured)

    Returns 200 if all dependencies are healthy.
    Returns 503 if any dependency is unhealthy.
    """
    checks = {
        "status": "ready",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {},
    }

    # Check database connection
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()  # No await needed - scalar() is not async
        checks["checks"]["database"] = {"status": "healthy", "type": "postgresql"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        checks["checks"]["database"] = {"status": "unhealthy", "error": str(e)}
        checks["status"] = "not_ready"

    # Check Redis connection (if configured)
    if settings.REDIS_URL and settings.REDIS_URL != "memory://":
        try:
            import redis.asyncio as redis

            redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            await redis_client.ping()
            await redis_client.close()
            checks["checks"]["redis"] = {"status": "healthy"}
        except Exception as e:
            logger.warning(f"Redis health check failed: {e}")
            checks["checks"]["redis"] = {"status": "unhealthy", "error": str(e)}
            # Redis is optional, don't mark as not_ready

    # Return 503 if any critical dependency is unhealthy
    if checks["status"] == "not_ready":
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=checks)

    return checks


@router.get("/metrics")
async def metrics() -> Dict[str, Any]:
    """
    Basic metrics endpoint

    Returns simple metrics about the service.
    For production, consider using Prometheus metrics.
    """
    uptime_seconds = int(time.time() - START_TIME)
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": (
            settings.SENTRY_ENVIRONMENT if hasattr(settings, "SENTRY_ENVIRONMENT") else "unknown"
        ),
        "uptime": uptime_seconds,
        "uptime_human": f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m {uptime_seconds % 60}s",
        "timestamp": datetime.utcnow().isoformat(),
    }
