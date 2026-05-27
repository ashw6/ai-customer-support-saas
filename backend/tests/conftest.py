from __future__ import annotations

import os
from pathlib import Path

import pytest


BACKEND_DIR = Path(__file__).resolve().parents[1]
TEST_DB = BACKEND_DIR / ".test.db"
TEST_CHROMA = BACKEND_DIR / ".test_chroma"

os.environ.setdefault("ENVIRONMENT", "testing")
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ.setdefault("JWT_SECRET", "test-secret-with-at-least-thirty-two-chars")
os.environ.setdefault("AI_CHAT_FALLBACK_ONLY", "true")
os.environ.setdefault("AI_CHAT_FALLBACK_ENABLED", "true")
os.environ.setdefault("CHROMA_DB_DIR", str(TEST_CHROMA))


@pytest.fixture(scope="session", autouse=True)
def _prepare_test_database():
    if TEST_DB.exists():
        TEST_DB.unlink()

    from database.database import Base, get_engine
    from models.conversation import Conversation, Message  # noqa: F401
    from models.document import UploadedDocument  # noqa: F401
    from models.lead import Lead  # noqa: F401
    from models.password_reset import PasswordResetToken  # noqa: F401
    from models.ticket import Ticket  # noqa: F401
    from models.user import User  # noqa: F401

    Base.metadata.create_all(bind=get_engine())
    yield
