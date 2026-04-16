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
    APP_NAME: str = "WebCreator"
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
    SENDGRID_FROM_NAME: str = "WebCreator"

    # Frontend URL for email links
    FRONTEND_URL: str = "http://localhost:3000"

    # Redis cache (optional)
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_KEY_PREFIX: str = "fasthub"  # Prefix for all Redis keys (override per app)

    # Celery (optional)
    CELERY_BROKER_URL: Optional[str] = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: Optional[str] = "redis://localhost:6379/0"

    # Fakturownia
    FAKTUROWNIA_API_TOKEN: Optional[str] = None
    FAKTUROWNIA_ACCOUNT: Optional[str] = None

    # OAuth Social Login
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    GITHUB_REDIRECT_URI: Optional[str] = None
    MICROSOFT_CLIENT_ID: Optional[str] = None
    MICROSOFT_CLIENT_SECRET: Optional[str] = None
    MICROSOFT_REDIRECT_URI: Optional[str] = None

    # Backend URL (for OAuth callbacks)
    BACKEND_URL: str = "http://localhost:8000"

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
    SMTP_FROM_EMAIL: str = "noreply@webcreator.app"

    # Sentry (monitoring)
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1  # 10% of transactions

    # Email templates + branding
    EMAIL_BACKEND: Optional[str] = None  # "smtp", "sendgrid", "console" (auto-detect if None)
    EMAIL_TEMPLATE_DIR: Optional[str] = None  # app override folder for templates
    EMAIL_BRAND_COLOR: str = "#4F46E5"
    EMAIL_BRAND_LOGO_URL: str = ""
    EMAIL_COMPANY_NAME: str = "WebCreator"
    EMAIL_COMPANY_ADDRESS: str = ""

    # Invitations
    INVITATION_EXPIRE_DAYS: int = 7
    INVITATION_MAX_PENDING: int = 50

    # PayU
    PAYU_POS_ID: Optional[str] = None
    PAYU_MD5_KEY: Optional[str] = None
    PAYU_CLIENT_ID: Optional[str] = None
    PAYU_CLIENT_SECRET: Optional[str] = None
    PAYU_SANDBOX: bool = True

    # Tpay (Autopay)
    TPAY_CLIENT_ID: Optional[str] = None
    TPAY_CLIENT_SECRET: Optional[str] = None
    TPAY_SECURITY_CODE: Optional[str] = None
    TPAY_SANDBOX: bool = True

    # Przelewy24
    P24_MERCHANT_ID: Optional[str] = None
    P24_POS_ID: Optional[str] = None
    P24_CRC_KEY: Optional[str] = None
    P24_SANDBOX: bool = True

    # PayPal
    PAYPAL_CLIENT_ID: Optional[str] = None
    PAYPAL_CLIENT_SECRET: Optional[str] = None
    PAYPAL_SANDBOX: bool = True

    # Recurring (polskie bramki bez natywnych subskrypcji)
    RECURRING_GRACE_DAYS: int = 14
    RECURRING_REMINDER_DAYS: str = "1,3,7"

    # Task Queue (Background Tasks)
    TASK_BACKEND: str = "arq"  # "arq" | "celery" | "sync"
    ARQ_REDIS_URL: Optional[str] = None  # None = użyj REDIS_URL
    ARQ_MAX_JOBS: int = 10
    ARQ_JOB_TIMEOUT: int = 120  # sekundy
    ARQ_MAX_TRIES: int = 3

    # KSeF (Krajowy System e-Faktur)
    KSEF_NIP: Optional[str] = None
    KSEF_AUTH_METHOD: str = "token"  # "token" or "certificate"
    KSEF_AUTH_TOKEN: Optional[str] = None
    KSEF_CERTIFICATE_BASE64: Optional[str] = None
    KSEF_PRIVATE_KEY_BASE64: Optional[str] = None
    KSEF_ENVIRONMENT: str = "test"  # test|demo|prod

    # Invoice backend — wybor systemu fakturowania
    INVOICE_BACKEND: str = "none"  # none|fakturownia|ksef
    INVOICE_SELLER_NAME: str = ""
    INVOICE_SELLER_ADDRESS: str = ""
    INVOICE_BANK_ACCOUNT: str = ""

    # GUS REGON API
    GUS_API_KEY: Optional[str] = None  # Brak = sandbox mode (do testów)

    # 2FA (Brief 26)
    TOTP_ISSUER_NAME: str = "WebCreator"
    TOTP_TEMP_TOKEN_EXPIRE_MINUTES: int = 5

    # Sessions (Brief 26)
    SESSION_CLEANUP_DAYS: int = 30

    # GDPR
    GDPR_DELETION_GRACE_DAYS: int = 14
    GDPR_EXPORT_FORMAT: str = "json"  # json (csv planned)
    GDPR_AUTO_EXPORT_ON_DELETE: bool = True

    # File Storage
    STORAGE_BACKEND: str = "local"  # "local" or "s3"
    STORAGE_LOCAL_DIR: str = "./uploads"
    STORAGE_MAX_FILE_SIZE_MB: float = 50.0

    # S3 (opcjonalnie)
    AWS_S3_BUCKET: Optional[str] = None
    AWS_S3_REGION: str = "eu-central-1"
    AWS_S3_ENDPOINT_URL: Optional[str] = None  # MinIO, Wasabi, DigitalOcean Spaces

    # Stock Photos (Brief 34)
    UNSPLASH_ACCESS_KEY: Optional[str] = None
    PEXELS_API_KEY: Optional[str] = None

    # AI / Anthropic (Brief 31)
    ANTHROPIC_API_KEY: Optional[str] = None
    AI_MODEL_FAST: str = "claude-haiku-4-5-20251001"
    AI_MODEL_SMART: str = "claude-sonnet-4-20250514"
    AI_VISION_MAX_ITERATIONS: int = 3

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

# Module-level singleton — used by `from fasthub_core.config import settings`
settings = get_settings()
