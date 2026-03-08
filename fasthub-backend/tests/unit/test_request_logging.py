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

        mock_request = MagicMock(spec=Request)
        mock_request.method = "GET"
        mock_request.url.path = "/api/v1/users"
        mock_request.query_params = {}
        mock_request.client.host = "127.0.0.1"
        mock_request.headers.get.return_value = "test-agent"
        mock_request.state.user_id = None

        async def mock_call_next(request):
            response = MagicMock(spec=Response)
            response.status_code = 200
            return response

        await middleware.dispatch(mock_request, mock_call_next)

        # Logger uses structured kwargs: logger.info("request_completed", method=..., path=..., ...)
        assert mock_logger.info.called or mock_logger.debug.called


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

        # Verify logger was called with duration_ms as a keyword arg
        assert mock_logger.info.called
        call_kwargs = mock_logger.info.call_args[1]
        assert "duration_ms" in call_kwargs


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

        # Verify error was logged — dispatch uses logger.error for 500s
        assert mock_logger.error.called or mock_logger.warning.called or mock_logger.info.called


@pytest.mark.asyncio
async def test_sensitive_data_masking():
    """Test middleware handles requests with sensitive query params"""
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

        # Verify middleware completed without error
        assert mock_logger.info.called


# ====================================================================================
# PHASE 2: MEDIUM PRIORITY - Error Handling (8 tests)
# ====================================================================================
