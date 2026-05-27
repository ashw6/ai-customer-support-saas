INTEREST_KEYWORDS = (
    "pricing",
    "price",
    "demo",
    "trial",
    "buy",
    "purchase",
    "quote",
    "sales",
    "subscribe",
    "subscription",
    "upgrade",
    "book a call",
    "contact sales",
)

EMAIL_PATTERN = r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"
PHONE_PATTERN = r"(?:\+?\d[\d\s().-]{6,}\d)"


def detect_lead_interest(message: str) -> str | None:
    normalized = f" {message.lower()} "
    for keyword in INTEREST_KEYWORDS:
        if f" {keyword} " in normalized or keyword in normalized:
            return keyword
    return None


def extract_lead_contact(message: str) -> dict[str, str] | None:
    """Extract contact details from a sales-intent chat message when present."""
    import re

    matched_keyword = detect_lead_interest(message)
    if not matched_keyword:
        return None

    email_match = re.search(EMAIL_PATTERN, message)
    if not email_match:
        return None

    phone_match = re.search(PHONE_PATTERN, message)

    name = ""
    name_patterns = (
        r"(?:my name is|i am|i'm|this is)\s+([a-z][a-z .'-]{1,80})",
        r"name\s*[:=-]\s*([a-z][a-z .'-]{1,80})",
    )
    for pattern in name_patterns:
        match = re.search(pattern, message, flags=re.IGNORECASE)
        if match:
            name = " ".join(match.group(1).strip(" .,'-").split())
            break

    return {
        "name": name,
        "email": email_match.group(0),
        "phone": " ".join(phone_match.group(0).split()) if phone_match else "",
        "matched_keyword": matched_keyword,
    }
