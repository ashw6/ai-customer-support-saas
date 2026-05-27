from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database.database import get_db
from models.user import User
from utils.dependencies import _get_user_from_token, security
from utils.roles import UserRole
from dotenv import load_dotenv
import os

load_dotenv(override=os.getenv("ENVIRONMENT", "").lower() not in {"production", "testing"})


def get_current_user_with_role(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Get current user with role verification"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user, err = _get_user_from_token(db, credentials.credentials)
    if err is not None or user is None:
        raise credentials_exception

    return user


def require_admin(current_user: User = Depends(get_current_user_with_role)):
    """Require admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_support_agent(current_user: User = Depends(get_current_user_with_role)):
    """Require support_agent role"""
    if current_user.role not in [UserRole.SUPPORT_AGENT, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Support agent access required"
        )
    return current_user


def require_customer(current_user: User = Depends(get_current_user_with_role)):
    """Require customer role (or any authenticated user)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPPORT_AGENT, UserRole.CUSTOMER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer access required"
        )
    return current_user


def require_authenticated(current_user: User = Depends(get_current_user_with_role)):
    """Require any authenticated user"""
    return current_user
