from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

BACKEND_ENV_PATH = Path(__file__).resolve().with_name(".env")
load_dotenv(
    dotenv_path=BACKEND_ENV_PATH,
    override=os.getenv("ENVIRONMENT", "").lower() not in {"production", "testing"},
)

# Initialize rate limiter (disabled in testing mode)
_is_testing = os.getenv("ENVIRONMENT", "").lower() == "testing"

if _is_testing:
    # Create a no-op limiter for testing that doesn't enforce limits
    class _NoOpLimiter:
        def limit(self, limit_string):
            def decorator(func):
                return func
            return decorator
    limiter = _NoOpLimiter()
else:
    limiter = Limiter(key_func=get_remote_address)

from middleware.request_tracking import RequestIdMiddleware, RequestLoggingMiddleware
from routes.auth import router as auth_router
from routes.chat import router as chat_router
from routes.documents import router as documents_router
from routes.leads import router as leads_router
from routes.role_based import router as role_router
from routes.tickets import router as tickets_router
from ai.ollama_service import ai_provider, check_ai_reachable, is_fallback_only
from settings import get_settings, validate_production_settings
from utils.exception_handlers import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from utils.logging_config import configure_app_logging


def _configure_logging() -> None:
    configure_app_logging(level_name=get_settings().log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_production_settings()
    logging.getLogger("app.startup").info(
        "application_started environment=%s",
        get_settings().environment,
    )
    yield


_configure_logging()

app = FastAPI(
    title="AI Customer Support & Sales Agent API",
    description="Production-ready SaaS platform backend",
    version="1.0.0",
    lifespan=lifespan,
)

# Store limiter in app state for exception handler
app.state.limiter = limiter

# Only add rate limit exception handler if not in testing mode
if get_settings().environment.lower() != "testing":
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Configure CORS (comma-separated CORS_ORIGINS in production)
# Must be added BEFORE routers to ensure it applies to all routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIdMiddleware)

# Include auth router
app.include_router(auth_router)

# Include role-based router
app.include_router(role_router)

# Tickets
app.include_router(tickets_router)

# Chat conversations
app.include_router(chat_router)

# RAG documents
app.include_router(documents_router)

# Lead capture and automation
app.include_router(leads_router)


@app.get("/")
async def root():
    return {"message": "AI Customer Support & Sales Agent API"}


@app.get("/health")
async def health_check():
    fallback_only = is_fallback_only()
    ai_ok = await check_ai_reachable()
    provider = ai_provider()
    return {
        "status": "healthy",
        "service": "AI Support API",
        "ai": "fallback_only" if fallback_only else (f"{provider}_reachable" if ai_ok else f"{provider}_unreachable"),
        "ai_provider": provider,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
