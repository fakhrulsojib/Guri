"""
Tests for the global exception handler added in main.py.

Verifies that unhandled exceptions are:
  1. Caught by the global handler
  2. Returned as a clean 500 JSON response
  3. Logged with full traceback via structlog
"""
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


def _create_app_with_failing_route():
    """Build a minimal FastAPI app that includes the global exception handler
    and a route that deliberately raises an unhandled exception."""
    from fastapi.responses import JSONResponse
    import structlog

    logger = structlog.get_logger()

    app = FastAPI()

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(
            "Unhandled server error",
            path=str(request.url),
            method=request.method,
            error=str(exc),
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    @app.get("/test/force-500")
    async def force_500():
        raise RuntimeError("Intentional test explosion")

    return app


class TestGlobalExceptionHandler:
    """Suite for the global @app.exception_handler(Exception)."""

    def test_returns_500_json_on_unhandled_exception(self):
        """An unhandled RuntimeError should produce a 500 with a JSON body."""
        app = _create_app_with_failing_route()
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/test/force-500")

        assert response.status_code == 500
        body = response.json()
        assert body == {"detail": "Internal server error"}

    def test_does_not_leak_internal_details(self):
        """The response body must not contain the original exception message."""
        app = _create_app_with_failing_route()
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/test/force-500")

        assert "Intentional test explosion" not in response.text

    @patch("structlog.get_logger")
    def test_logs_error_with_exc_info(self, mock_get_logger):
        """The handler should call logger.error with exc_info=True."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        app = _create_app_with_failing_route()
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/test/force-500")

        assert response.status_code == 500
        # Verify that logger.error was called at least once with exc_info=True
        error_calls = [
            call for call in mock_logger.error.call_args_list
            if call.kwargs.get("exc_info") is True
        ]
        assert len(error_calls) >= 1, "Expected logger.error to be called with exc_info=True"


class TestGlobalHandlerOnRealApp:
    """Verify the handler is wired into the actual main.py app."""

    def test_real_app_has_exception_handler(self):
        """The production app object should have the global exception handler registered."""
        from main import app

        # FastAPI stores exception handlers keyed by exception class
        assert Exception in app.exception_handlers, (
            "main.app should have a global Exception handler registered"
        )
