"""Transactional email via Resend (preferred) or Gmail SMTP fallback."""
from __future__ import annotations

import asyncio
import logging
import os
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from html import escape

import httpx

from models.lead import Lead
from models.user import User

logger = logging.getLogger(__name__)


class EmailServiceError(RuntimeError):
    pass


@dataclass(frozen=True)
class ResendConfig:
    api_key: str | None
    from_email: str
    endpoint: str
    timeout_seconds: float


@dataclass(frozen=True)
class SmtpConfig:
    host: str
    port: int
    user: str
    password: str
    from_header: str
    timeout_seconds: float


def get_resend_config() -> ResendConfig:
    return ResendConfig(
        api_key=os.getenv("RESEND_API_KEY"),
        from_email=os.getenv("RESEND_FROM_EMAIL", "AI Support <onboarding@resend.dev>"),
        endpoint=os.getenv("RESEND_EMAILS_URL", "https://api.resend.com/emails"),
        timeout_seconds=float(os.getenv("RESEND_TIMEOUT_SECONDS", "15")),
    )


def get_smtp_config() -> SmtpConfig | None:
    user = (os.getenv("SMTP_USER") or "").strip()
    password = (os.getenv("SMTP_PASSWORD") or "").strip()
    if not user or not password:
        return None
    host = (os.getenv("SMTP_HOST") or "smtp.gmail.com").strip()
    if host.lower().endswith("gmail.com"):
        password = "".join(password.split())
    from_override = (os.getenv("SMTP_FROM_EMAIL") or "").strip()
    from_header = from_override if from_override else f"AI Support <{user}>"
    return SmtpConfig(
        host=host,
        port=int(os.getenv("SMTP_PORT", "587")),
        user=user,
        password=password,
        from_header=from_header,
        timeout_seconds=float(os.getenv("SMTP_TIMEOUT_SECONDS", "15")),
    )


def resend_is_configured() -> bool:
    key = get_resend_config().api_key
    return bool(key and key.strip())


def smtp_is_configured() -> bool:
    return get_smtp_config() is not None


def email_is_configured() -> bool:
    return resend_is_configured() or smtp_is_configured()


def _lead_email_html(lead: Lead) -> str:
    safe_name = escape(lead.name)
    return f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.5; color: #111827;">
      <h2>Thanks for your interest, {safe_name}.</h2>
      <p>We received your request and our team will follow up shortly.</p>
      <p>If there is anything specific you want covered, reply to this email with the details.</p>
      <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;" />
      <p style="font-size: 12px; color: #6b7280;">AI Customer Support & Sales Agent</p>
    </div>
    """


def _password_reset_html(user: User, reset_url: str) -> str:
    safe_name = escape(user.name)
    safe_url = escape(reset_url, quote=True)
    return f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.5; color: #111827;">
      <h2>Reset your password</h2>
      <p>Hi {safe_name},</p>
      <p>Use the button below to reset your password. This link expires soon and can only be used once.</p>
      <p style="margin: 24px 0;">
        <a href="{safe_url}" style="background:#111827;color:#ffffff;padding:12px 18px;border-radius:8px;text-decoration:none;">Reset password</a>
      </p>
      <p>If the button does not work, paste this link into your browser:</p>
      <p style="word-break: break-all; color:#374151;">{safe_url}</p>
      <p>If you did not request this, you can ignore this email.</p>
    </div>
    """


def _welcome_email_html(user: User) -> str:
    safe_name = escape(user.name)
    safe_email = escape(user.email)
    return f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.5; color: #111827;">
      <h2>Welcome, {safe_name}.</h2>
      <p>Your AI Customer Support & Sales Agent account is ready.</p>
      <p><strong>Account email:</strong> {safe_email}</p>
      <p>You can now sign in, manage support tickets, chat with the AI assistant, and use the dashboard tools available for your role.</p>
      <p style="font-size: 12px; color: #6b7280;">AI Customer Support & Sales Agent</p>
    </div>
    """


def _plain_text_from_html(html: str) -> str:
    """Minimal plain-text part for clients that do not render HTML."""
    return "Please view this message in an HTML-capable email client."


def _send_smtp_sync(
    *,
    cfg: SmtpConfig,
    to_email: str,
    subject: str,
    html: str,
) -> None:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = cfg.from_header
    message["To"] = to_email
    message.set_content(_plain_text_from_html(html))
    message.add_alternative(html, subtype="html")

    with smtplib.SMTP(cfg.host, cfg.port, timeout=cfg.timeout_seconds) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(cfg.user, cfg.password)
        server.send_message(message)


async def _send_via_resend(
    *,
    to_email: str,
    subject: str,
    html: str,
    config: ResendConfig | None = None,
    log_context: dict | None = None,
) -> bool:
    cfg = config or get_resend_config()
    if not cfg.api_key:
        raise EmailServiceError("RESEND_API_KEY is not configured.")

    payload = {
        "from": cfg.from_email,
        "to": [to_email],
        "subject": subject,
        "html": html,
    }
    headers = {"Authorization": f"Bearer {cfg.api_key}", "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=cfg.timeout_seconds) as client:
            response = await client.post(cfg.endpoint, json=payload, headers=headers)
            response.raise_for_status()
    except httpx.TimeoutException as exc:
        logger.warning("resend_timeout", extra={**(log_context or {}), "error": str(exc)})
        raise EmailServiceError("Email provider request timed out.") from exc
    except httpx.HTTPStatusError as exc:
        logger.warning(
            "resend_http_error",
            extra={**(log_context or {}), "status_code": exc.response.status_code},
        )
        raise EmailServiceError("Resend rejected the email.") from exc
    except httpx.RequestError as exc:
        logger.warning("resend_request_error", extra={**(log_context or {}), "error": str(exc)})
        raise EmailServiceError("Could not reach Resend.") from exc

    logger.info("email_sent_resend", extra={**(log_context or {}), "to": to_email})
    return True


async def _send_via_smtp(
    *,
    to_email: str,
    subject: str,
    html: str,
    log_context: dict | None = None,
) -> bool:
    cfg = get_smtp_config()
    if cfg is None:
        raise EmailServiceError("SMTP is not configured (SMTP_USER and SMTP_PASSWORD required).")

    try:
        await asyncio.to_thread(
            _send_smtp_sync,
            cfg=cfg,
            to_email=to_email,
            subject=subject,
            html=html,
        )
    except smtplib.SMTPAuthenticationError as exc:
        logger.warning("smtp_auth_error", extra={**(log_context or {}), "error": str(exc)})
        raise EmailServiceError("SMTP authentication failed. Check SMTP_USER and SMTP_PASSWORD.") from exc
    except smtplib.SMTPException as exc:
        logger.warning("smtp_error", extra={**(log_context or {}), "error": str(exc)})
        raise EmailServiceError("SMTP delivery failed.") from exc
    except OSError as exc:
        logger.warning("smtp_connection_error", extra={**(log_context or {}), "error": str(exc)})
        raise EmailServiceError("Could not connect to the SMTP server.") from exc

    logger.info("email_sent_smtp", extra={**(log_context or {}), "to": to_email, "host": cfg.host})
    return True


async def _dispatch_email(
    *,
    to_email: str,
    subject: str,
    html: str,
    log_context: dict | None = None,
) -> bool:
    """Send via Resend when configured; otherwise use SMTP (e.g. Gmail)."""
    if resend_is_configured():
        return await _send_via_resend(
            to_email=to_email,
            subject=subject,
            html=html,
            log_context=log_context,
        )
    if smtp_is_configured():
        return await _send_via_smtp(
            to_email=to_email,
            subject=subject,
            html=html,
            log_context=log_context,
        )
    logger.warning("email_provider_not_configured", extra=log_context or {})
    raise EmailServiceError("No email provider configured (set RESEND_API_KEY or SMTP credentials).")


async def send_lead_followup(lead: Lead) -> bool:
    return await _dispatch_email(
        to_email=lead.email,
        subject="Thanks for your interest",
        html=_lead_email_html(lead),
        log_context={"lead_id": lead.id, "email_type": "lead_followup"},
    )


async def send_welcome_email(user: User) -> bool:
    return await _dispatch_email(
        to_email=user.email,
        subject="Welcome to AI Customer Support",
        html=_welcome_email_html(user),
        log_context={"user_id": user.id, "email_type": "welcome"},
    )


async def send_password_reset_email(user: User, reset_url: str) -> bool:
    return await _dispatch_email(
        to_email=user.email,
        subject="Reset your password",
        html=_password_reset_html(user, reset_url),
        log_context={"user_id": user.id, "email_type": "password_reset"},
    )


async def try_send_welcome_email(user: User) -> bool:
    if not email_is_configured():
        logger.info(
            "email_skipped_not_configured",
            extra={"user_id": user.id, "email_type": "welcome"},
        )
        return False
    try:
        return await send_welcome_email(user)
    except EmailServiceError as exc:
        logger.warning(
            "welcome_email_failed",
            extra={"user_id": user.id, "error": str(exc)},
        )
        return False


async def try_send_password_reset_email(user: User, reset_url: str) -> bool:
    if not email_is_configured():
        logger.info(
            "email_skipped_not_configured",
            extra={"user_id": user.id, "email_type": "password_reset"},
        )
        return False
    try:
        return await send_password_reset_email(user, reset_url)
    except EmailServiceError as exc:
        logger.warning(
            "password_reset_email_failed",
            extra={"user_id": user.id, "error": str(exc)},
        )
        return False


async def try_send_lead_followup(lead: Lead) -> bool:
    if not email_is_configured():
        logger.info(
            "email_skipped_not_configured",
            extra={"lead_id": lead.id, "email_type": "lead_followup"},
        )
        return False
    try:
        return await send_lead_followup(lead)
    except EmailServiceError as exc:
        logger.warning(
            "lead_followup_email_failed",
            extra={"lead_id": lead.id, "error": str(exc)},
        )
        return False
