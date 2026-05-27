import pytest

import settings
from ai.rag_pipeline import _extractive_pdf_answer
from utils.lead_detection import extract_lead_contact


def test_resume_specific_extractive_answer_is_generic() -> None:
    chunks = [
        {
            "text": (
                "SKILLS\n"
                "Python, FastAPI, React, PostgreSQL\n"
                "PROJECTS\n"
                "Support Automation Portal\n"
            )
        }
    ]

    answer = _extractive_pdf_answer("What skills are listed?", chunks)

    assert answer is not None
    assert "Ashwitha" not in answer
    assert "Python" in answer
    assert "FastAPI" in answer


def test_production_rejects_local_ollama_without_demo_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    settings.get_settings.cache_clear()
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@db.example.com:5432/app")
    monkeypatch.setenv("JWT_SECRET", "x" * 32)
    monkeypatch.setenv("CORS_ORIGINS", "https://example.com")
    monkeypatch.setenv("AI_CHAT_FALLBACK_ONLY", "false")
    monkeypatch.setenv("AI_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_GENERATE_URL", "http://localhost:11434/api/generate")
    monkeypatch.setenv("OLLAMA_EMBEDDINGS_URL", "http://localhost:11434/api/embeddings")

    with pytest.raises(RuntimeError, match="localhost Ollama"):
        settings.validate_production_settings()

    settings.get_settings.cache_clear()


def test_production_allows_demo_fallback_without_ollama(monkeypatch: pytest.MonkeyPatch) -> None:
    settings.get_settings.cache_clear()
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@db.example.com:5432/app")
    monkeypatch.setenv("JWT_SECRET", "x" * 32)
    monkeypatch.setenv("CORS_ORIGINS", "https://example.com")
    monkeypatch.setenv("AI_CHAT_FALLBACK_ONLY", "true")
    monkeypatch.setenv("OLLAMA_GENERATE_URL", "http://localhost:11434/api/generate")
    monkeypatch.setenv("OLLAMA_EMBEDDINGS_URL", "http://localhost:11434/api/embeddings")

    settings.validate_production_settings()

    settings.get_settings.cache_clear()


def test_production_allows_openai_provider_without_ollama(monkeypatch: pytest.MonkeyPatch) -> None:
    settings.get_settings.cache_clear()
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@db.example.com:5432/app")
    monkeypatch.setenv("JWT_SECRET", "x" * 32)
    monkeypatch.setenv("CORS_ORIGINS", "https://example.com")
    monkeypatch.setenv("AI_CHAT_FALLBACK_ONLY", "false")
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OLLAMA_GENERATE_URL", "http://localhost:11434/api/generate")
    monkeypatch.setenv("OLLAMA_EMBEDDINGS_URL", "http://localhost:11434/api/embeddings")

    settings.validate_production_settings()

    settings.get_settings.cache_clear()


def test_chat_message_contact_extraction() -> None:
    lead = extract_lead_contact(
        "I want pricing. My name is Priya Sharma, email priya@example.com, phone +91 98765 43210."
    )

    assert lead == {
        "name": "Priya Sharma",
        "email": "priya@example.com",
        "phone": "+91 98765 43210",
        "matched_keyword": "pricing",
    }
