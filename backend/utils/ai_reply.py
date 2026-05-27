"""Keyword-based suggested support replies (no external AI APIs)."""

PAYMENT_REPLY = (
    "We are sorry for the inconvenience. Our team is checking your payment issue."
)
LOGIN_REPLY = (
    "We understand your login issue. Please try resetting your password while we investigate."
)
TECH_REPLY = (
    "Our technical team has been notified and is working on the issue."
)
DEFAULT_REPLY = (
    "Thank you for contacting support. Our team will get back to you shortly."
)

PAYMENT_SIGNALS: tuple[str, ...] = (
    "payment",
    "money deducted",
    "refund",
    "charged",
    "billing",
)

LOGIN_SIGNALS: tuple[str, ...] = (
    "cannot login",
    "can't login",
    "cant login",
    "login",
    "password",
    "sign in",
    "signin",
    "account blocked",
    "locked out",
)

TECH_SIGNALS: tuple[str, ...] = (
    "bug",
    "technical",
    "not working",
    "crash",
    "error",
)


def _matches_any(normalized: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in normalized for phrase in phrases)


def generate_auto_reply(text: str) -> str:
    """
    Suggest a support reply from ticket title + description text.

    Uses keyword buckets (payment -> login -> technical -> default).
    """
    normalized = " ".join(text.lower().split())

    if _matches_any(normalized, PAYMENT_SIGNALS):
        return PAYMENT_REPLY

    if _matches_any(normalized, LOGIN_SIGNALS):
        return LOGIN_REPLY

    if _matches_any(normalized, TECH_SIGNALS):
        return TECH_REPLY

    return DEFAULT_REPLY
