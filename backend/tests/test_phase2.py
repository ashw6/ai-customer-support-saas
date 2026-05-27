"""Phase 2: pagination, filters, search, sort, middleware, exception format."""
from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from database.database import SessionLocal
from main import app
from models.user import User


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _email(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}@audit-python-client.org"


@pytest.fixture
def support_headers(client: TestClient) -> dict[str, str]:
    email = _email("p2_support")
    r = client.post(
        "/auth/register",
        json={"name": "Support P2", "email": email, "password": "Testpass1"},
    )
    assert r.status_code == 201, r.text
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.email == email).first()
        assert u is not None
        u.role = "support_agent"
        db.commit()
    finally:
        db.close()
    tok = client.post(
        "/auth/login",
        json={"email": email, "password": "Testpass1"},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


@pytest.fixture
def customer_headers(client: TestClient) -> dict[str, str]:
    email = _email("p2_customer")
    r = client.post(
        "/auth/register",
        json={"name": "Cust P2", "email": email, "password": "Testpass1"},
    )
    assert r.status_code == 201, r.text
    tok = r.json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


def test_health_has_request_id_header(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert "X-Request-ID" in r.headers
    assert len(r.headers["X-Request-ID"]) > 8


def test_invalid_limit_returns_422_with_request_id(client: TestClient, support_headers: dict[str, str]) -> None:
    r = client.get("/tickets?limit=200", headers=support_headers)
    assert r.status_code == 422
    body = r.json()
    assert body.get("success") is False
    assert "request_id" in body
    assert r.headers.get("X-Request-ID")


def test_invalid_page_returns_422(client: TestClient, support_headers: dict[str, str]) -> None:
    r = client.get("/tickets?page=0", headers=support_headers)
    assert r.status_code == 422
    assert r.json().get("success") is False


def test_pagination_and_filters_and_search(
    client: TestClient,
    support_headers: dict[str, str],
    customer_headers: dict[str, str],
) -> None:
    for i in range(3):
        r = client.post(
            "/tickets",
            json={
                "title": f"Alpha ticket number {i} unique",
                "description": f"Description long enough for ticket {i} with payment keyword",
                "priority": "high",
            },
            headers=customer_headers,
        )
        assert r.status_code == 201, r.text

    r1 = client.get("/tickets?limit=2&page=1", headers=support_headers)
    assert r1.status_code == 200
    j1 = r1.json()
    assert j1["success"] is True
    assert len(j1["data"]["items"]) == 2
    assert j1["data"]["total"] >= 3
    assert j1["data"]["page"] == 1
    assert j1["data"]["limit"] == 2
    assert j1["data"]["pages"] >= 2

    r2 = client.get("/tickets?status=open&limit=100", headers=support_headers)
    assert r2.status_code == 200
    for item in r2.json()["data"]["items"]:
        assert item["status"] == "open"

    r3 = client.get("/tickets?search=Alpha%20ticket&limit=50", headers=support_headers)
    assert r3.status_code == 200
    assert r3.json()["data"]["total"] >= 1

    r4 = client.get(
        "/tickets/my?search=Alpha&sort_by=created_at&order=desc&limit=10",
        headers=customer_headers,
    )
    assert r4.status_code == 200
    body = r4.json()
    assert body["success"] is True
    assert len(body["data"]["items"]) >= 1
    assert "X-Request-ID" in r4.headers


def test_http_exception_shape_on_403(client: TestClient, customer_headers: dict[str, str]) -> None:
    r = client.get("/tickets", headers=customer_headers)
    assert r.status_code == 403
    j = r.json()
    assert j.get("success") is False
    assert "message" in j
    assert "request_id" in j


def test_sort_by_urgency_score(client: TestClient, support_headers: dict[str, str]) -> None:
    r = client.get("/tickets?sort_by=urgency_score&order=desc&limit=5", headers=support_headers)
    assert r.status_code == 200
    data = r.json()["data"]["items"]
    if len(data) >= 2:
        scores = [row["urgency_score"] for row in data]
        assert scores == sorted(scores, reverse=True)
