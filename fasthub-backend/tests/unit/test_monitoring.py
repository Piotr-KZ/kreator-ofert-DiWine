# ============================================================================

import pytest
from unittest.mock import MagicMock, patch
from app.core.monitoring import (
    collect_metric,
    track_error,
    monitor_performance,
    get_health_metrics
)


def test_metric_collection():
    """Test metrics are collected and stored"""
    with patch('app.core.monitoring.metrics_client') as mock_client:
        collect_metric("http_requests_total", 1, tags={"endpoint": "/api/users"})
        
        mock_client.increment.assert_called_once_with(
            "http_requests_total",
            1,
            tags={"endpoint": "/api/users"}
        )


def test_error_tracking():
    """Test errors are tracked with context"""
    with patch('app.core.monitoring.error_tracker') as mock_tracker:
        error = ValueError("Test error")
        context = {"user_id": str(uuid4()), "endpoint": "/api/organizations"}
        
        track_error(error, context)
        
        mock_tracker.capture_exception.assert_called_once()
        call_args = mock_tracker.capture_exception.call_args
        assert call_args[0][0] == error
        assert "user_id" in call_args[1]["extra"]


def test_performance_monitoring():
    """Test request duration is monitored"""
    with patch('app.core.monitoring.metrics_client') as mock_client:
        duration_ms = 150
        endpoint = "/api/v1/users"
        
        monitor_performance(endpoint, duration_ms)
        
        mock_client.timing.assert_called_once_with(
            "http_request_duration",
            duration_ms,
            tags={"endpoint": endpoint}
        )


def test_health_metrics():
    """Test health check metrics are collected"""
    with patch('app.core.monitoring.get_system_metrics') as mock_system:
        mock_system.return_value = {
            "cpu_percent": 45.2,
            "memory_percent": 60.5,
            "disk_usage_percent": 55.0
        }
        
        metrics = get_health_metrics()
        
        assert "cpu_percent" in metrics
        assert "memory_percent" in metrics
        assert metrics["cpu_percent"] < 100
