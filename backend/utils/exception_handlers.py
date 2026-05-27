"""Centralized FastAPI exception handlers."""
from __future__ import annotations

import logging
from typing import Any

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from schemas.errors import ErrorResponse

logger = logging.getLogger("app.exceptions")


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", None) or "unknown"


def _http_message(detail: Any) -> str:
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list):
        parts: list[str] = []
        for item in detail:
            if isinstance(item, dict):
                parts.append(str(item.get("msg", item)))
            else:
                parts.append(str(item))
        return "; ".join(parts) if parts else "Request error"
    return str(detail)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    rid = _request_id(request)
    body = ErrorResponse(
        success=False,
        message=_http_message(exc.detail),
        request_id=rid,
    ).model_dump()
    resp = JSONResponse(status_code=exc.status_code, content=body)
    resp.headers["X-Request-ID"] = rid
    logger.warning(
        "http_exception",
        extra={"request_id": rid, "status": exc.status_code, "error_message": body["message"]},
    )
    return resp


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    rid = _request_id(request)
    errors = exc.errors()
    message = "; ".join(f"{e.get('loc')}: {e.get('msg')}" for e in errors) or "Validation error"
    body = ErrorResponse(success=False, message=message, request_id=rid).model_dump()
    resp = JSONResponse(status_code=422, content=body)
    resp.headers["X-Request-ID"] = rid
    logger.warning("validation_error", extra={"request_id": rid, "errors": errors})
    return resp


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    rid = _request_id(request)
    logger.exception("unhandled_exception request_id=%s path=%s", rid, request.url.path)
    body = ErrorResponse(
        success=False,
        message="An unexpected error occurred. Please try again or contact support if the problem persists.",
        request_id=rid,
    ).model_dump()
    resp = JSONResponse(status_code=500, content=body)
    resp.headers["X-Request-ID"] = rid
    return resp
