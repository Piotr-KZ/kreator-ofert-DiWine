"""
Core configuration module
Uses Pydantic Settings for environment variable management
"""

from typing import List, Optional

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "FastHub"
    APP_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # Database
    DATABASE_URL: str = ""

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = []
    ALLOWED_HOSTS: List[str] = ["*"]  # Restrict in production

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Stripe (optional)
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_STARTER_PRICE_ID: Optional[str] = None
    STRIPE_PRO_PRICE_ID: Optional[str] = None
    STRIPE_ENTERPRISE_PRICE_ID: Optional[str] = None

    # SendGrid (optional)
    SENDGRID_API_KEY: Optional[str] = None
    SENDGRID_FROM_EMAIL: str = "noreply@example.com"
    SENDGRID_FROM_NAME: str = "FastHub"

    # Frontend URL for email links
    FRONTEND_URL: str = "http://localhost:3000"

    # Redis cache (optional)
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Celery (optional)
    CELERY_BROKER_URL: Optional[str] = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: Optional[str] = "redis://localhost:6379/0"

    # Fakturownia
    FAKTUROWNIA_API_TOKEN: Optional[str] = None
    FAKTUROWNIA_ACCOUNT: Optional[str] = None

    # Google APIs
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None

    # Outlook IMAP
    OUTLOOK_EMAIL: Optional[str] = None
    OUTLOOK_PASSWORD: Optional[str] = None
    OUTLOOK_IMAP_SERVER: str = "outlook.office365.com"
    OUTLOOK_IMAP_PORT: int = 993

    # SMTP (opcjonalne — bez nich działa console mode)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    SMTP_FROM_EMAIL: str = "noreply@fasthub.app"

    # Sentry (monitoring)
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1  # 10% of transactions

    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = "utf-8"
        extra = "allow"


_settings = None

def get_settings() -> Settings:
    """Lazy load settings to ensure environment variables are available at runtime"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
