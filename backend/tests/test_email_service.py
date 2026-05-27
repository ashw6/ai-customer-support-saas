"""Unit tests for Resend + SMTP email dispatch."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from utils import email_service as es


@pytest.fixture(autouse=True)
def _clear_email_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in (
        "RESEND_API_KEY",
        "SMTP_USER",
        "SMTP_PASSWORD",
        "SMTP_HOST",
        "SMTP_PORT",
        "SMTP_FROM_EMAIL",
    ):
        monkeypatch.delenv(key, raising=False)


def test_resend_preferred_over_smtp(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RESEND_API_KEY", "re_test_key")
    monkeypatch.setenv("SMTP_USER", "user@gmail.com")
    monkeypatch.setenv("SMTP_PASSWORD", "app-password")

    with (
        patch.object(es, "_send_via_resend", new_callable=AsyncMock) as resend_mock,
        patch.object(es, "_send_via_smtp", new_callable=AsyncMock) as smtp_mock,
    ):
        import asyncio

        asyncio.run(
            es._dispatch_email(
                to_email="a@example.com",
                subject="Hi",
                html="<p>x</p>",
            )
        )
        resend_mock.assert_awaited_once()
        smtp_mock.assert_not_awaited()


def test_smtp_fallback_when_resend_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SMTP_USER", "user@gmail.com")
    monkeypatch.setenv("SMTP_PASSWORD", "app-password")

    with (
        patch.object(es, "_send_via_resend", new_callable=AsyncMock) as resend_mock,
        patch.object(es, "_send_via_smtp", new_callable=AsyncMock, return_value=True) as smtp_mock,
    ):
        import asyncio

        ok = asyncio.run(
            es._dispatch_email(
                to_email="a@example.com",
                subject="Hi",
                html="<p>x</p>",
            )
        )
        assert ok is True
        resend_mock.assert_not_awaited()
        smtp_mock.assert_awaited_once()


def test_no_provider_raises() -> None:
    import asyncio

    with pytest.raises(es.EmailServiceError, match="No email provider"):
        asyncio.run(
            es._dispatch_email(
                to_email="a@example.com",
                subject="Hi",
                html="<p>x</p>",
            )
        )


def test_try_send_skips_when_unconfigured() -> None:
    import asyncio
    from datetime import datetime, timezone

    user = MagicMock()
    user.id = 1
    user.email = "u@example.com"
    user.name = "User"
    user.created_at = datetime.now(timezone.utc)

    ok = asyncio.run(es.try_send_welcome_email(user))
    assert ok is False


def test_smtp_sync_builds_message(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SMTP_USER", "user@gmail.com")
    monkeypatch.setenv("SMTP_PASSWORD", "secret")
    cfg = es.get_smtp_config()
    assert cfg is not None
    assert cfg.host == "smtp.gmail.com"
    assert cfg.port == 587

    server = MagicMock()
    server.__enter__ = MagicMock(return_value=server)
    server.__exit__ = MagicMock(return_value=False)

    with patch("utils.email_service.smtplib.SMTP", return_value=server):
        es._send_smtp_sync(
            cfg=cfg,
            to_email="to@example.com",
            subject="Test",
            html="<p>Hello</p>",
        )

    server.starttls.assert_called_once()
    server.login.assert_called_once_with("user@gmail.com", "secret")
    server.send_message.assert_called_once()


def test_gmail_app_password_spaces_are_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SMTP_USER", "user@gmail.com")
    monkeypatch.setenv("SMTP_PASSWORD", "abcd efgh ijkl mnop")

    cfg = es.get_smtp_config()

    assert cfg is not None
    assert cfg.password == "abcdefghijklmnop"
