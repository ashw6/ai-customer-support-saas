"""Backend audit integration tests (requires working DATABASE_URL)."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from database.database import SessionLocal
from main import app
from models.user import User


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _unique_email(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}@audit-python-client.org"


def _register_token(client: TestClient, prefix: str) -> tuple[str, str]:
    email = _unique_email(prefix)
    r = client.post(
        "/auth/register",
        json={"name": prefix.title(), "email": email, "password": "Testpass1"},
    )
    assert r.status_code == 201, r.text
    return email, r.json()["access_token"]


def _set_role(email: str, role: str) -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        assert user is not None
        user.role = role
        db.commit()
    finally:
        db.close()


def test_register_can_create_admin_when_admin_requested(client: TestClient) -> None:
    email = _unique_email("admin_register")
    r = client.post(
        "/auth/register",
        json={
            "name": "Bad Actor",
            "email": email,
            "password": "Testpass1",
            "role": "admin",
        },
    )
    assert r.status_code == 201, r.text
    assert r.json()["user"]["role"] == "admin"


def test_login_role_mismatch_is_forbidden(client: TestClient) -> None:
    email = _unique_email("role_mismatch")
    r = client.post(
        "/auth/register",
        json={"name": "Role Mismatch", "email": email, "password": "Testpass1"},
    )
    assert r.status_code == 201, r.text

    login = client.post(
        "/auth/login",
        json={"email": email, "password": "Testpass1", "role": "admin"},
    )
    assert login.status_code == 403


def test_refresh_accepts_json_body(client: TestClient) -> None:
    email = _unique_email("refresh_body")
    r = client.post(
        "/auth/register",
        json={"name": "Refresh Body", "email": email, "password": "Testpass1"},
    )
    assert r.status_code == 201, r.text
    refresh_token = r.json()["refresh_token"]

    refreshed = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refreshed.status_code == 200, refreshed.text
    assert refreshed.json()["access_token"]
    assert refreshed.json()["refresh_token"]


def test_login_invalid_password(client: TestClient) -> None:
    r = client.post(
        "/auth/login",
        json={"email": "nonexistent@audit-python-client.org", "password": "wrong"},
    )
    assert r.status_code == 401


def test_tickets_list_requires_auth(client: TestClient) -> None:
    assert client.get("/tickets").status_code in (401, 403)


def test_whitespace_ticket_rejected_after_strip(client: TestClient) -> None:
    email = _unique_email("strip")
    tok = client.post(
        "/auth/register",
        json={"name": "S", "email": email, "password": "Testpass1"},
    ).json()["access_token"]
    h = {"Authorization": f"Bearer {tok}"}
    r = client.post(
        "/tickets",
        json={
            "title": "xx      ",
            "description": "yyyyyyyyyy",
        },
        headers=h,
    )
    assert r.status_code == 400


def test_customer_cannot_list_all_tickets(client: TestClient) -> None:
    email = _unique_email("cust")
    tok = client.post(
        "/auth/register",
        json={"name": "C", "email": email, "password": "Testpass1"},
    ).json()["access_token"]
    assert client.get("/tickets", headers={"Authorization": f"Bearer {tok}"}).status_code == 403


def test_invalid_sub_jwt_returns_401(client: TestClient) -> None:
    from utils.auth import create_access_token

    bad = create_access_token(data={"sub": "not-an-int"})
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {bad}"})
    assert r.status_code == 401


def test_customer_cannot_upload_shared_rag_document(client: TestClient) -> None:
    _, token = _register_token(client, "doc_customer")
    r = client.post(
        "/documents/upload",
        files={"file": ("policy.pdf", b"%PDF-1.4\nnot a real pdf", "application/pdf")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


def test_staff_cannot_send_message_as_other_conversation_owner(client: TestClient) -> None:
    _, customer_token = _register_token(client, "chat_owner")
    support_email, support_token = _register_token(client, "chat_support")
    _set_role(support_email, "support_agent")

    with patch("routes.chat.generate_grounded_answer", new_callable=AsyncMock, return_value="Answer"):
        created = client.post(
            "/chat/send",
            json={"message": "What is the refund policy?"},
            headers={"Authorization": f"Bearer {customer_token}"},
        )
    assert created.status_code == 201, created.text
    conversation_id = created.json()["conversation"]["id"]

    r = client.post(
        "/chat/send",
        json={"conversation_id": conversation_id, "message": "Staff follow-up"},
        headers={"Authorization": f"Bearer {support_token}"},
    )
    assert r.status_code == 403
