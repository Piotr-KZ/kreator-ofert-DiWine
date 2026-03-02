"""
Testy Production Infrastructure.
Structured logging, monitoring, rate limiting, subscription check, health.
"""

import pytest
import os

# ============================================================================
# STRUCTURED LOGGING
# ============================================================================

class TestStructuredLogging:

    def test_configure_logging_dev(self):
        from fasthub_core.logging import configure_logging
        configure_logging(debug=True)  # Nie powinno rzucić wyjątku

    def test_configure_logging_production(self):
        from fasthub_core.logging import configure_logging
        configure_logging(debug=False)

    def test_get_logger(self):
        from fasthub_core.logging import get_logger
        logger = get_logger("test.module")
        assert logger is not None

    def test_logger_has_standard_methods(self):
        from fasthub_core.logging import get_logger
        logger = get_logger("test")
        assert callable(getattr(logger, "info", None))
        assert callable(getattr(logger, "error", None))
        assert callable(getattr(logger, "warning", None))
        assert callable(getattr(logger, "debug", None))

    def test_structlog_imported(self):
        import structlog
        assert structlog is not None


# ============================================================================
# MONITORING (SENTRY)
# ============================================================================

class TestMonitoring:

    def test_init_monitoring_without_dsn(self):
        """Bez SENTRY_DSN — graceful skip."""
        os.environ.pop("SENTRY_DSN", None)
        from fasthub_core.monitoring import init_monitoring
        result = init_monitoring()
        assert result == False  # Pominięty

    def test_capture_exception_without_sentry(self):
        """capture_exception nie rzuca błędu nawet bez Sentry."""
        from fasthub_core.monitoring import capture_exception
        try:
            raise ValueError("test error")
        except ValueError as e:
            capture_exception(e, context={"test": True})
        # Nie powinno rzucić wyjątku

    def test_capture_message_without_sentry(self):
        from fasthub_core.monitoring import capture_message
        capture_message("test message", level="warning")

    def test_set_user_context_without_sentry(self):
        from fasthub_core.monitoring import set_user_context, clear_user_context
        set_user_context("user-123", email="test@test.com")
        clear_user_context()

    def test_monitoring_module_imports(self):
        from fasthub_core.monitoring import (
            init_monitoring, capture_exception, capture_message,
            set_user_context, clear_user_context,
        )
        assert callable(init_monitoring)
        assert callable(capture_exception)

    def test_before_send_filter(self):
        from fasthub_core.monitoring.sentry import _before_send_filter
        event = {
            "request": {
                "headers": {"Authorization": "Bearer secret123", "Content-Type": "application/json"},
                "query_string": "token=abc123&page=1",
            }
        }
        filtered = _before_send_filter(event, {})
        assert filtered["request"]["headers"]["Authorization"] == "[Filtered]"
        assert filtered["request"]["query_string"] == "[Filtered]"
        assert filtered["request"]["headers"]["Content-Type"] == "application/json"


# ============================================================================
# RATE LIMITING
# ============================================================================

class TestRateLimiting:

    def test_rate_limits_constants(self):
        from fasthub_core.rate_limiting import RateLimits
        assert RateLimits.AUTH_LOGIN == "5/minute"
        assert RateLimits.AUTH_REGISTER == "3/hour"
        assert RateLimits.WEBHOOK == "1000/hour"
        assert RateLimits.DEFAULT == "200/hour"

    def test_rate_limits_customizable(self):
        from fasthub_core.rate_limiting import RateLimits
        original = RateLimits.AUTH_LOGIN
        RateLimits.AUTH_LOGIN = "10/minute"
        assert RateLimits.AUTH_LOGIN == "10/minute"
        RateLimits.AUTH_LOGIN = original  # Przywróć

    def test_create_limiter_memory_backend(self):
        from fasthub_core.rate_limiting import create_limiter
        limiter = create_limiter(redis_url=None)
        assert limiter is not None

    def test_create_limiter_with_custom_limits(self):
        from fasthub_core.rate_limiting import create_limiter
        limiter = create_limiter(default_limits=["50/minute"])
        assert limiter is not None

    def test_get_rate_limit_handler(self):
        from fasthub_core.rate_limiting import get_rate_limit_handler
        handler = get_rate_limit_handler()
        assert callable(handler)

    def test_slowapi_imported(self):
        from slowapi import Limiter
        assert Limiter is not None


# ============================================================================
# SUBSCRIPTION CHECK
# ============================================================================

class TestSubscriptionCheck:

    def test_subscription_checker_class(self):
        from fasthub_core.billing.subscription_check import SubscriptionChecker
        assert hasattr(SubscriptionChecker, "check_subscription")
        assert hasattr(SubscriptionChecker, "is_subscription_active")
        assert hasattr(SubscriptionChecker, "configure")

    def test_default_grace_period(self):
        from fasthub_core.billing.subscription_check import SubscriptionChecker
        assert SubscriptionChecker.GRACE_PERIOD_DAYS == 7

    def test_configure_grace_period(self):
        from fasthub_core.billing.subscription_check import SubscriptionChecker
        original = SubscriptionChecker.GRACE_PERIOD_DAYS
        SubscriptionChecker.configure(grace_period_days=14)
        assert SubscriptionChecker.GRACE_PERIOD_DAYS == 14
        SubscriptionChecker.configure(grace_period_days=original)

    def test_exempt_paths_include_auth_and_billing(self):
        from fasthub_core.billing.subscription_check import SubscriptionChecker
        paths = SubscriptionChecker.EXEMPT_PATHS
        assert any("/auth" in p for p in paths)
        assert any("/billing" in p or "/subscriptions" in p for p in paths)
        assert any("/health" in p for p in paths)

    def test_is_exempt_path(self):
        from fasthub_core.billing.subscription_check import SubscriptionChecker
        assert SubscriptionChecker._is_exempt_path("/api/v1/auth/login") == True
        assert SubscriptionChecker._is_exempt_path("/health") == True
        assert SubscriptionChecker._is_exempt_path("/api/processes") == False

    def test_require_active_subscription_factory(self):
        from fasthub_core.billing.subscription_check import require_active_subscription
        dep = require_active_subscription()
        assert callable(dep)


# ============================================================================
# HEALTH CHECK
# ============================================================================

class TestHealthCheck:

    def test_health_checker_class(self):
        from fasthub_core.health import HealthChecker
        checker = HealthChecker()
        assert hasattr(checker, "add_check")
        assert hasattr(checker, "run_all")
        assert hasattr(checker, "configure")

    def test_health_checker_configure(self):
        from fasthub_core.health import HealthChecker
        checker = HealthChecker()
        checker.configure(app_name="test-app", version="1.2.3")
        assert checker._app_name == "test-app"
        assert checker._version == "1.2.3"

    def test_add_custom_check(self):
        from fasthub_core.health import HealthChecker
        checker = HealthChecker()

        async def mock_check():
            return {"status": "ok", "detail": "all good"}

        checker.add_check("custom_service", mock_check)
        assert "custom_service" in checker._checks

    def test_health_router_exists(self):
        from fasthub_core.health import health_router
        routes = [r.path for r in health_router.routes]
        assert "/health" in routes
        assert "/ready" in routes

    def test_get_health_checker_singleton(self):
        from fasthub_core.health.checker import get_health_checker
        c1 = get_health_checker()
        c2 = get_health_checker()
        assert c1 is c2
