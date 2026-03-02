"""
FastHub - Universal SaaS Boilerplate
Main FastAPI application entry point
"""

import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi.errors import RateLimitExceeded

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging_config import configure_logging, get_logger
from app.core.monitoring import init_sentry
from app.core.rate_limit import get_rate_limit_exceeded_handler, limiter
from app.middleware.request_logging import RequestLoggingMiddleware
from fasthub_core.middleware import SecurityHeadersMiddleware, RequestIDMiddleware

# Configure structured logging
configure_logging()
logger = get_logger(__name__)

# Initialize Sentry error tracking
init_sentry()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    Universal SaaS Boilerplate with FastAPI
    
    ## Features
    
    * **Authentication** - JWT-based auth with magic links, password reset
    * **User Management** - Complete user CRUD with roles (admin/user)
    * **Organizations** - Multi-tenancy support
    * **Subscriptions** - Stripe integration with webhooks
    * **API Tokens** - Long-lived tokens for API access
    * **Rate Limiting** - Protection against abuse
    * **Monitoring** - Sentry integration with health checks
    
    ## Security
    
    All endpoints require authentication unless marked as public.
    Use Bearer token in Authorization header: `Authorization: Bearer <token>`
    """,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",  # Always enabled
    redoc_url=f"{settings.API_V1_STR}/redoc",  # Always enabled
    contact={
        "name": "FastHub Support",
        "email": "support@fasthub.com",
    },
    license_info={
        "name": "MIT",
    },
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, get_rate_limit_exceeded_handler())

# Security middleware

# ===== 1. CORS (MUST BE FIRST MIDDLEWARE!) =====
# CRITICAL: CORS middleware must be added BEFORE any other middleware
# to properly handle OPTIONS preflight requests

# Use BACKEND_CORS_ORIGINS from settings, fallback to localhost for development
origins = settings.BACKEND_CORS_ORIGINS if settings.BACKEND_CORS_ORIGINS else [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
    "http://127.0.0.1:3003",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
    expose_headers=["X-Total-Count", "X-Page", "X-Per-Page"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Debug: Log CORS origins at startup
logger.info(f"🔧 CORS Origins configured: {origins}")

# 2. Trusted Host (prevent host header attacks)
if not settings.DEBUG and settings.ALLOWED_HOSTS:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# 3. Request logging (before GZip to log uncompressed size)
app.add_middleware(RequestLoggingMiddleware)

# 4. GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# 5. Security headers middleware (from fasthub_core)
app.add_middleware(
    SecurityHeadersMiddleware,
    enable_hsts=settings.ENVIRONMENT == "production",
)

# 6. Request ID middleware (from fasthub_core)
app.add_middleware(RequestIDMiddleware)


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Health check endpoints
# Root-level health endpoint for Render.com and other monitoring services
@app.get("/health")
async def root_health_check():
    """
    Root-level health check endpoint (for Render.com)
    """
    return {
        "status": "healthy",
        "service": "FastHub",
        "version": settings.APP_VERSION,
        "timestamp": time.time(),
    }

# API v1 health endpoint (legacy)
@app.get("/api/v1/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "service": "FastHub",
        "version": settings.APP_VERSION,
        "timestamp": time.time(),
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Actions to perform on application startup
    """
    logger.info("🚀 FastHub Backend started")
    logger.info(f"📍 API Documentation: http://localhost:8000{settings.API_V1_STR}/docs")
    logger.info(f"🔧 CORS Origins: {origins}")
    logger.info(f"🐛 Debug Mode: {settings.DEBUG}")
    
    # Run database migrations automatically
    try:
        logger.info("🔄 Running database migrations...")
        from alembic.config import Config
        from alembic import command
        import os
        
        # Get the alembic.ini path
        alembic_cfg = Config(os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic.ini"))
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        logger.info("✅ Database migrations completed successfully")
    except Exception as e:
        logger.error(f"❌ Failed to run database migrations: {e}")
        logger.warning("⚠️ Application starting without running migrations")

    # Seed RBAC permissions
    try:
        logger.info("🔑 Seeding RBAC permissions...")
        from fasthub_core.rbac.service import RBACService
        from app.db.session import get_db

        async for db in get_db():
            rbac = RBACService(db)
            await rbac.seed_permissions()
            logger.info("✅ RBAC permissions seeded successfully")
            break
    except Exception as e:
        logger.error(f"❌ Failed to seed RBAC permissions: {e}")
        logger.warning("⚠️ RBAC permissions not seeded — endpoints may reject requests")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Actions to perform on application shutdown
    """
    logger.info("👋 FastHub Backend shutting down")
