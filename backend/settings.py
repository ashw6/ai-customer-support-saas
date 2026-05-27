"""Application settings loaded from the environment (validated on startup in production)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

BACKEND_ENV_PATH = Path(__file__).resolve().with_name(".env")
load_dotenv(
    dotenv_path=BACKEND_ENV_PATH,
    override=os.getenv("ENVIRONMENT", "").lower() not in {"production", "testing"},
)


def _truthy(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _default_cors_origins() -> list[str]:
    return [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]


def _parse_cors_origins(raw: str | None) -> list[str]:
    if not raw or not raw.strip():
        return _default_cors_origins()
    parts = [part.strip() for part in raw.split(",") if part.strip()]
    return parts if parts else _default_cors_origins()


def _is_local_url(value: str | None) -> bool:
    if not value:
        return False
    host = (urlparse(value).hostname or "").lower()
    return host in {"localhost", "127.0.0.1", "::1"}


@dataclass(frozen=True)
class Settings:
    environment: str
    database_url: str
    cors_origins: list[str]
    log_level: str
    skip_health_access_log: bool

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        environment=os.getenv("ENVIRONMENT", "development").strip(),
        database_url=(os.getenv("DATABASE_URL") or "").strip(),
        cors_origins=_parse_cors_origins(os.getenv("CORS_ORIGINS") or os.getenv("ALLOWED_ORIGINS")),
        log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper(),
        skip_health_access_log=_truthy("SKIP_HEALTH_ACCESS_LOG", "true"),
    )


def default_database_url() -> str:
    """Development-only fallback when DATABASE_URL is unset (override in .env for real use)."""
    return "postgresql://postgres:postgres@127.0.0.1:5432/ai_support_db"


def resolve_database_url() -> str:
    url = get_settings().database_url
    if url:
        return url
    if get_settings().is_production:
        raise RuntimeError("DATABASE_URL must be set in production (e.g. Supabase PostgreSQL connection string).")
    return default_database_url()


def validate_jwt_secret() -> None:
    """Ensure JWT_SECRET is present and strong enough for production."""
    secret = (os.getenv("JWT_SECRET") or "").strip()
    if not secret:
        raise RuntimeError(
            "JWT_SECRET must be set to a non-empty value (see backend/.env.example)."
        )
    if get_settings().is_production and len(secret) < 32:
        raise RuntimeError(
            "JWT_SECRET must be at least 32 characters when ENVIRONMENT=production."
        )


def validate_production_settings() -> None:
    s = get_settings()
    validate_jwt_secret()
    if not s.is_production:
        return
    if not s.database_url:
        raise RuntimeError("DATABASE_URL is required when ENVIRONMENT=production.")
    if s.database_url.startswith("sqlite"):
        raise RuntimeError("DATABASE_URL must point to PostgreSQL when ENVIRONMENT=production.")
    if not (os.getenv("CORS_ORIGINS") or os.getenv("ALLOWED_ORIGINS")):
        raise RuntimeError(
            "CORS_ORIGINS (or ALLOWED_ORIGINS) must list your deployed frontend origin(s), "
            "comma-separated, when ENVIRONMENT=production."
        )
    for origin in s.cors_origins:
        if origin.startswith("http://localhost") or origin.startswith("http://127.0.0.1"):
            raise RuntimeError(
                "CORS_ORIGINS must not use localhost when ENVIRONMENT=production; "
                "set your Vercel (or other) HTTPS origin instead."
            )
    fallback_only = _truthy("AI_CHAT_FALLBACK_ONLY")
    ai_provider = os.getenv("AI_PROVIDER", "groq").strip().lower()
    if ai_provider not in {"ollama", "openai"}:
        raise RuntimeError("AI_PROVIDER must be 'ollama' or 'openai'.")
    if not fallback_only and ai_provider == "openai" and not (os.getenv("OPENAI_API_KEY") or "").strip():
        raise RuntimeError("OPENAI_API_KEY is required when AI_PROVIDER=openai in production.")
    if not fallback_only and ai_provider == "ollama":
        local_llm_urls = (
            os.getenv("OLLAMA_GENERATE_URL", "http://localhost:11434/api/generate"),
            os.getenv("OLLAMA_CHAT_URL"),
            os.getenv("OLLAMA_EMBEDDINGS_URL", "http://localhost:11434/api/embeddings"),
        )
        if any(_is_local_url(url) for url in local_llm_urls):
            raise RuntimeError(
                "Production chat cannot use localhost Ollama URLs. Set OLLAMA_* URLs to a reachable "
                "hosted Ollama service, set AI_PROVIDER=openai with OPENAI_API_KEY, set AI_PROVIDER=groq with GROQ_API_KEY, or set "
                "AI_CHAT_FALLBACK_ONLY=true for a non-LLM demo mode."
            )
