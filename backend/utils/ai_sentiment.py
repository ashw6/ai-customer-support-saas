"""Keyword-based ticket sentiment analysis (no external AI APIs)."""

NEGATIVE_KEYWORDS: tuple[str, ...] = (
    "angry",
    "frustrated",
    "terrible",
    "worst",
    "useless",
    "refund",
    "failed",
    "hacked",
    "disappointed",
    "issue",
    "problem",
)

POSITIVE_KEYWORDS: tuple[str, ...] = (
    "great",
    "thanks",
    "awesome",
    "helpful",
    "satisfied",
    "good",
)


def analyze_sentiment(text: str) -> str:
    """
    Classify sentiment from free text using keyword matching.

    Returns one of: "negative", "positive", "neutral".
    Negative signals are checked before positive (complaint-heavy tickets).
    """
    normalized = " ".join(text.lower().split())

    for word in NEGATIVE_KEYWORDS:
        if word in normalized:
            return "negative"

    for word in POSITIVE_KEYWORDS:
        if word in normalized:
            return "positive"

    return "neutral"
