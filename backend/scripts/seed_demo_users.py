"""Create local demo users for customer and company owner login."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database.database import SessionLocal
from models.conversation import Conversation, Message  # noqa: F401
from models.document import UploadedDocument  # noqa: F401
from models.lead import Lead  # noqa: F401
from models.password_reset import PasswordResetToken  # noqa: F401
from models.ticket import Ticket  # noqa: F401
from models.user import User
from utils.auth import get_password_hash


DEMO_USERS = [
    {
        "name": "Demo Customer",
        "email": "customer@example.com",
        "password": "Customer123",
        "role": "customer",
    },
    {
        "name": "Company Owner",
        "email": "owner@example.com",
        "password": "Owner12345",
        "role": "admin",
    },
    {
        "name": "Support Agent",
        "email": "support@example.com",
        "password": "Support123",
        "role": "support_agent",
    },
]


def main() -> None:
    db = SessionLocal()
    try:
        for item in DEMO_USERS:
            user = db.query(User).filter(User.email == item["email"]).first()
            if user is None:
                user = User(
                    name=item["name"],
                    email=item["email"],
                    hashed_password=get_password_hash(item["password"]),
                    role=item["role"],
                )
                db.add(user)
            else:
                user.name = item["name"]
                user.hashed_password = get_password_hash(item["password"])
                user.role = item["role"]
        db.commit()
    finally:
        db.close()

    print("Demo users ready:")
    for item in DEMO_USERS:
        print(f"- {item['role']}: {item['email']} / {item['password']}")


if __name__ == "__main__":
    main()
