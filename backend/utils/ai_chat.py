def generate_chat_response(message: str) -> str:
    """Local deterministic assistant response until an external AI provider is configured."""
    normalized = message.strip().lower()
    if any(word in normalized for word in ("refund", "payment", "charged", "billing")):
        return (
            "I understand this is a billing or payment issue. Please share the order ID, "
            "payment date, and the amount charged so the support team can investigate quickly."
        )
    if any(word in normalized for word in ("login", "password", "account", "access")):
        return (
            "This sounds account-related. Try resetting your password first, and share any "
            "error message you see so we can narrow it down."
        )
    if any(word in normalized for word in ("urgent", "angry", "escalate", "manager")):
        return (
            "I hear the urgency. I have captured the concern clearly; please add any ticket "
            "or order reference so the team can prioritize the next action."
        )
    return (
        "Thanks for the details. I can help route this: please add any relevant order ID, "
        "screenshots, or steps you already tried, and I will summarize the next best action."
    )
