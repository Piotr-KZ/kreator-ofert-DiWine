"""
FastHub - Universal SaaS Boilerplate
Main FastAPI application entry point
"""

import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi.errors import RateLimitExceeded

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.monitoring import init_sentry
from app.core.rate_limit import get_rate_limit_exceeded_handler, limiter

logger = logging.getLogger(__name__)

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

# Debug: Print CORS origins at startup
print(f"🔧 CORS Origins configured: {origins}")

# 2. Trusted Host (prevent host header attacks)
if not settings.DEBUG and settings.ALLOWED_HOSTS:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# 3. GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# 4. Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    # Security headers (OWASP recommendations)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

    # Content Security Policy
    if not settings.DEBUG:
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
        )

    # Remove server header
    if "Server" in response.headers:
        del response.headers["Server"]

    return response


# 5. Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Health check endpoint
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


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Actions to perform on application shutdown
    """
    logger.info("👋 FastHub Backend shutting down")
