"""Keyword-based ticket intelligence (escalation, category, urgency, SLA, labels)."""

from __future__ import annotations

ESCALATION_PHRASES: tuple[str, ...] = (
    "hacked",
    "urgent",
    "lawsuit",
    "security breach",
    "refund immediately",
    "worst service ever",
    "payment failed multiple times",
)

CATEGORY_PAYMENT: tuple[str, ...] = (
    "payment",
    "refund",
    "money deducted",
    "billing",
    "charged",
    "checkout",
)
CATEGORY_LOGIN: tuple[str, ...] = (
    "cannot login",
    "can't login",
    "cant login",
    "login",
    "password",
    "sign in",
    "signin",
    "locked out",
)
CATEGORY_TECHNICAL: tuple[str, ...] = (
    "bug",
    "crash",
    "error",
    "not working",
    "technical",
    "slow",
    "timeout",
)
CATEGORY_ACCOUNT: tuple[str, ...] = (
    "account",
    "profile",
    "subscription",
    "settings",
    "email address",
)

URGENCY_CRITICAL: tuple[str, ...] = (
    "lawsuit",
    "security breach",
    "hacked",
    "refund immediately",
    "emergency",
    "critical",
)
URGENCY_NEGATIVE: tuple[str, ...] = (
    "angry",
    "frustrated",
    "terrible",
    "worst",
    "disappointed",
    "useless",
)
URGENCY_PAYMENT: tuple[str, ...] = (
    "payment",
    "refund",
    "money deducted",
    "billing",
    "failed",
    "charged",
)
URGENCY_TECH_OR_FAULT: tuple[str, ...] = (
    "bug",
    "crash",
    "error",
    "timeout",
    "not working",
)
URGENCY_GENERAL_ISSUE: tuple[str, ...] = (
    "issue",
    "problem",
    "broken",
)


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def _contains_any(normalized: str, phrases: tuple[str, ...]) -> bool:
    return any(p in normalized for p in phrases)


def detect_escalation(text: str) -> bool:
    """Return True if ticket text matches escalation signals."""
    normalized = _normalize(text)
    return _contains_any(normalized, ESCALATION_PHRASES)


def predict_category(text: str) -> str:
    """
    Predict a coarse ticket category (keyword buckets, first non-general match wins).
    """
    normalized = _normalize(text)
    if _contains_any(normalized, CATEGORY_PAYMENT):
        return "payment"
    if _contains_any(normalized, CATEGORY_LOGIN):
        return "login"
    if _contains_any(normalized, CATEGORY_TECHNICAL):
        return "technical"
    if _contains_any(normalized, CATEGORY_ACCOUNT):
        return "account"
    return "general"


def calculate_urgency(text: str) -> int:
    """
    Score urgency 1-5 using tiered keyword rules (highest matching tier wins).
    """
    normalized = _normalize(text)
    if _contains_any(normalized, URGENCY_CRITICAL):
        return 5
    if _contains_any(normalized, URGENCY_NEGATIVE):
        return 4
    if _contains_any(normalized, URGENCY_PAYMENT):
        return 3
    if _contains_any(normalized, URGENCY_TECH_OR_FAULT) or _contains_any(
        normalized, URGENCY_GENERAL_ISSUE
    ):
        return 2
    return 1


def generate_sla_tag(priority: str, escalated: bool) -> str:
    """
    Map priority + escalation to an SLA bucket tag.
    """
    p = priority.strip().lower()
    if escalated and p == "high":
        return "immediate"
    if p == "high":
        return "within_1_hour"
    if escalated and p == "medium":
        return "within_1_hour"
    if p == "medium":
        return "within_24_hours"
    if escalated and p == "low":
        return "within_24_hours"
    if p == "low":
        return "within_3_days"
    if escalated:
        return "within_24_hours"
    return "within_24_hours"


def generate_smart_labels(text: str) -> str:
    """
    Produce a deterministic, comma-separated label string from keyword hits.
    """
    normalized = _normalize(text)
    labels: list[str] = []

    def add(label: str) -> None:
        if label not in labels:
            labels.append(label)

    if _contains_any(normalized, CATEGORY_PAYMENT):
        add("payment")
    if _contains_any(normalized, ("refund", "refund immediately")):
        add("refund")
    if _contains_any(normalized, ("urgent", "urgency")):
        add("urgent")
    if _contains_any(normalized, ESCALATION_PHRASES):
        add("escalation")
    if _contains_any(normalized, CATEGORY_LOGIN):
        add("login")
    if _contains_any(normalized, CATEGORY_TECHNICAL):
        add("technical")
    if _contains_any(normalized, CATEGORY_ACCOUNT):
        add("account")
    if _contains_any(normalized, URGENCY_NEGATIVE):
        add("frustrated")
    if _contains_any(normalized, ("hacked", "security breach")):
        add("security")

    if not labels:
        add("general")

    return ",".join(labels)
