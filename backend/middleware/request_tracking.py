"""Request ID + HTTP access logging (no print)."""
from __future__ import annotations

import logging
import time
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from settings import get_settings

logger = logging.getLogger("http.request")


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Assign ``request.state.request_id`` and ``X-Request-ID`` response header."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log method, path, status, duration, and request id after the response is produced."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        rid = getattr(request.state, "request_id", "-")
        if get_settings().skip_health_access_log and request.url.path in {"/health", "/"}:
            return response
        logger.info(
            "%s %s %s %.2fms",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
            extra={
                "request_id": rid,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "elapsed_ms": round(elapsed_ms, 2),
            },
        )
        return response
