from typing import Literal, Optional, Tuple

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database.database import get_db
from models.user import User
from utils.auth import verify_token

security = HTTPBearer()


def _get_user_from_token(db: Session, token: str) -> Tuple[Optional[User], Optional[Literal["invalid", "not_found"]]]:
    """
    Resolve the authenticated user from a raw JWT string.

    Returns:
        (user, None) on success.
        (None, "invalid") if the token is invalid, malformed, or ``sub`` is unusable.
        (None, "not_found") if the token is valid but no matching user exists.
    """
    payload = verify_token(token)
    if payload is None:
        return None, "invalid"

    user_id = payload.get("sub")
    if user_id is None:
        return None, "invalid"

    try:
        uid = int(user_id)
    except (TypeError, ValueError):
        return None, "invalid"

    user = db.query(User).filter(User.id == uid).first()
    if user is None:
        return None, "not_found"

    return user, None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token"""
    user, err = _get_user_from_token(db, credentials.credentials)
    if err == "invalid":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if err == "not_found":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    assert user is not None
    return user
