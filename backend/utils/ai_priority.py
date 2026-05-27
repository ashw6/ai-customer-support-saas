"""Keyword-based ticket priority prediction (no external AI APIs)."""

HIGH_PRIORITY_KEYWORDS: tuple[str, ...] = (
    "payment failed",
    "money deducted",
    "urgent",
    "cannot login",
    "security",
    "hacked",
    "account blocked",
)

MEDIUM_PRIORITY_KEYWORDS: tuple[str, ...] = (
    "slow",
    "delay",
    "issue",
    "not working",
    "bug",
)


def predict_ticket_priority(text: str) -> str:
    """
    Predict ticket priority from free text using keyword scoring.

    Returns one of: "low", "medium", "high".
    """
    normalized = " ".join(text.lower().split())

    for phrase in HIGH_PRIORITY_KEYWORDS:
        if phrase in normalized:
            return "high"

    for phrase in MEDIUM_PRIORITY_KEYWORDS:
        if phrase in normalized:
            return "medium"

    return "low"
