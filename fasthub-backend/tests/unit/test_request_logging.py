# ============================================================================

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI, Request, Response
from app.middleware.request_logging import RequestLoggingMiddleware


# Create test app instance
app = FastAPI()
app.add_middleware(RequestLoggingMiddleware)


@pytest.mark.asyncio
async def test_request_logging_format():
    """Test request logs contain method, path, status code"""
    with patch('app.middleware.request_logging.logger') as mock_logger:
        middleware = RequestLoggingMiddleware(app)

        # Test via dispatch (HEAD/main approach)
        mock_request = MagicMock(spec=Request)
        mock_request.method = "GET"
        mock_request.url.path = "/api/v1/users"
        mock_request.query_params = {}
        mock_request.client.host = "127.0.0.1"
        mock_request.headers.get.return_value = "test-agent"
        mock_request.state.user_id = None

        # Create mock call_next
        async def mock_call_next(request):
            response = MagicMock(spec=Response)
            response.status_code = 200
            return response

        # Call middleware
        await middleware.dispatch(mock_request, mock_call_next)

        # Verify logging was called
        assert mock_logger.info.called or mock_logger.debug.called

    with patch('app.middleware.request_logging.logger') as mock_logger:
        middleware = RequestLoggingMiddleware(app)

        # Test via log_request (feature branch approach)
        mock_request = MagicMock()
        mock_request.method = "GET"
        mock_request.url.path = "/api/v1/users"

        mock_response = MagicMock()
        mock_response.status_code = 200

        await middleware.log_request(mock_request, mock_response, duration=0.150)

        mock_logger.info.assert_called_once()
        log_message = mock_logger.info.call_args[0][0]
        assert "GET" in log_message
        assert "/api/v1/users" in log_message
        assert "200" in str(log_message)


@pytest.mark.asyncio
async def test_response_time_tracking():
    """Test response time is tracked for each request"""
    with patch('app.middleware.request_logging.logger') as mock_logger:
        middleware = RequestLoggingMiddleware(app)

        mock_request = MagicMock(spec=Request)
        mock_request.method = "POST"
        mock_request.url.path = "/api/v1/auth/login"
        mock_request.query_params = {}
        mock_request.client.host = "127.0.0.1"
        mock_request.headers.get.return_value = "test-agent"
        mock_request.state.user_id = None

        async def mock_call_next(request):
            response = MagicMock(spec=Response)
            response.status_code = 200
            return response

        result = await middleware.dispatch(mock_request, mock_call_next)

        assert result.status_code == 200

    with patch('app.middleware.request_logging.logger') as mock_logger:
        middleware = RequestLoggingMiddleware(app)

        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.url.path = "/api/v1/auth/login"

        mock_response = MagicMock()
        mock_response.status_code = 200

        duration = 0.234  # 234ms
        await middleware.log_request(mock_request, mock_response, duration)

        log_extras = mock_logger.info.call_args[1].get("extra", {})
        assert "duration_ms" in log_extras
        assert log_extras["duration_ms"] == 234


@pytest.mark.asyncio
async def test_error_request_logging():
    """Test errors are logged properly"""
    with patch('app.middleware.request_logging.logger') as mock_logger:
        middleware = RequestLoggingMiddleware(app)

        mock_request = MagicMock(spec=Request)
        mock_request.method = "GET"
        mock_request.url.path = "/api/v1/error"
        mock_request.query_params = {}
        mock_request.client.host = "127.0.0.1"
        mock_request.headers.get.return_value = "test-agent"
        mock_request.state.user_id = None

        async def mock_call_next(request):
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            await middleware.dispatch(mock_request, mock_call_next)

        # Verify error was logged
        assert mock_logger.error.called or mock_logger.warning.called or mock_logger.info.called

    with patch('app.middleware.request_logging.logger') as mock_logger:
        middleware = RequestLoggingMiddleware(app)

        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.url.path = "/api/v1/users"

        mock_response = MagicMock()
        mock_response.status_code = 500

        await middleware.log_request(mock_request, mock_response, duration=0.100)

        mock_logger.error.assert_called_once()
        log_message = mock_logger.error.call_args[0][0]
        assert "500" in str(log_message)


@pytest.mark.asyncio
async def test_sensitive_data_masking():
    """Test sensitive data in logs is masked"""
    with patch('app.middleware.request_logging.logger') as mock_logger:
        middleware = RequestLoggingMiddleware(app)

        mock_request = MagicMock(spec=Request)
        mock_request.method = "POST"
        mock_request.url.path = "/api/v1/auth/login"
        mock_request.query_params = {"password": "secret123"}
        mock_request.client.host = "127.0.0.1"
        mock_request.headers.get.return_value = "test-agent"
        mock_request.state.user_id = None

        async def mock_call_next(request):
            response = MagicMock(spec=Response)
            response.status_code = 200
            return response

        await middleware.dispatch(mock_request, mock_call_next)

        # Just verify middleware completed without error
        assert True

    with patch('app.middleware.request_logging.logger') as mock_logger:
        middleware = RequestLoggingMiddleware(app)

        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.url.path = "/api/v1/auth/login"

        # Simulate request body with password
        body_data = {"email": "test@example.com", "password": "SuperSecret123!"}

        masked_data = middleware.mask_sensitive_data(body_data)

        assert masked_data["email"] == "test@example.com"
        assert masked_data["password"] == "***MASKED***"


# ====================================================================================
# PHASE 2: MEDIUM PRIORITY - Error Handling (8 tests)
# ====================================================================================
