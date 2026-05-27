import logging
import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from database.database import get_db
from models.password_reset import PasswordResetToken
from models.user import User
from schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    MessageResponse,
    PasswordResetResponse,
    RefreshTokenRequest,
    ResetPasswordRequest,
    UserLogin,
    UserRegister,
    UserResponse,
)
from settings import get_settings
from utils.auth import verify_password, get_password_hash, create_access_token, create_refresh_token, verify_token
from utils.dependencies import get_current_user as current_user_dependency
from utils.email_service import try_send_password_reset_email, try_send_welcome_email
from utils.roles import UserRole
from main import limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("PASSWORD_RESET_EXPIRE_MINUTES", "15"))
RESET_RESPONSE_MESSAGE = "If that email exists, a password reset link has been sent."


def _hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _reset_url(token: str) -> str:
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
    return f"{frontend_url}/reset-password?token={token}"


def _delete_expired_tokens(db: Session) -> None:
    now = datetime.now(timezone.utc)
    db.query(PasswordResetToken).filter(PasswordResetToken.expires_at <= now).delete(
        synchronize_session=False
    )

@router.post("/register", response_model=AuthResponse, status_code=201)
@limiter.limit("5/minute")
async def register(request: Request, user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        logger.info(
            "registration_rejected_email_exists",
            extra={"email": user_data.email},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Demo/local registration supports creating either customer or admin accounts.
    hashed_password = get_password_hash(user_data.password)
    user_role = (user_data.role or UserRole.CUSTOMER).value
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_role
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        logger.warning(
            "registration_integrity_error",
            extra={"email": user_data.email},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating user"
        )
    
    # Create access token and refresh token
    access_token = create_access_token(data={
        "sub": str(new_user.id),
        "email": new_user.email,
        "role": new_user.role
    })
    refresh_token = create_refresh_token(data={
        "sub": str(new_user.id),
        "email": new_user.email,
        "role": new_user.role
    })

    logger.info(
        "user_registered",
        extra={"user_id": new_user.id, "email": new_user.email},
    )

    await try_send_welcome_email(new_user)

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse(
            id=new_user.id,
            name=new_user.name,
            email=new_user.email,
            role=new_user.role,
            created_at=new_user.created_at
        )
    )

@router.post("/login", response_model=AuthResponse)
@limiter.limit("10/minute")
async def login(request: Request, user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    
    # Find user by email
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        logger.warning(
            "login_failed",
            extra={"reason": "unknown_email", "email": user_data.email},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(user_data.password, user.hashed_password):
        logger.warning(
            "login_failed",
            extra={"reason": "bad_password", "user_id": user.id},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validate role if provided
    if user_data.role and user.role != user_data.role.value:
        logger.warning(
            "login_failed",
            extra={"reason": "role_mismatch", "user_id": user.id, "expected_role": user_data.role.value, "actual_role": user.role},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This account does not have the required role: {user_data.role.value}",
        )
    
    # Create access token and refresh token
    access_token = create_access_token(data={
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    })
    refresh_token = create_refresh_token(data={
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    })

    logger.info(
        "login_success",
        extra={"user_id": user.id, "email": user.email},
    )

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            created_at=user.created_at
        )
    )


@router.post("/forgot-password", response_model=PasswordResetResponse)
@limiter.limit("3/minute")
async def forgot_password(request: Request, body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Create a single-use password reset token and email it to the user."""
    reset_url = None
    try:
        _delete_expired_tokens(db)
        user = db.query(User).filter(User.email == str(body.email)).first()
        if user is None:
            db.commit()
            return PasswordResetResponse(message=RESET_RESPONSE_MESSAGE)

        raw_token = secrets.token_urlsafe(48)
        reset_url = _reset_url(raw_token)
        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=_hash_reset_token(raw_token),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES),
        )
        db.add(reset_token)
        db.commit()
        db.refresh(reset_token)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("password_reset_create_db_error", extra={"email": str(body.email)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create password reset request",
        )

    email_sent = await try_send_password_reset_email(user, reset_url)
    return PasswordResetResponse(
        message=RESET_RESPONSE_MESSAGE,
        email_sent=email_sent,
        dev_reset_url=None if get_settings().is_production else reset_url,
    )


@router.post("/reset-password", response_model=MessageResponse)
@limiter.limit("5/minute")
async def reset_password(request: Request, body: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset a user's password using a valid single-use reset token."""
    now = datetime.now(timezone.utc)
    token_hash = _hash_reset_token(body.token)

    try:
        _delete_expired_tokens(db)
        reset_token = (
            db.query(PasswordResetToken)
            .filter(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > now,
            )
            .first()
        )
        if reset_token is None:
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset link is invalid or expired",
            )

        user = db.query(User).filter(User.id == reset_token.user_id).first()
        if user is None:
            db.delete(reset_token)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset link is invalid or expired",
            )

        user.hashed_password = get_password_hash(body.password)
        reset_token.used_at = now
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.id != reset_token.id,
        ).delete(synchronize_session=False)
        db.add(user)
        db.add(reset_token)
        db.commit()
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        logger.exception("password_reset_update_db_error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not reset password",
        )

    return MessageResponse(message="Password has been reset. You can sign in with your new password.")


@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user: User = Depends(current_user_dependency)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        created_at=current_user.created_at
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(body: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using a valid refresh token"""
    # Verify the refresh token
    payload = verify_token(body.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if it's a refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    # Get user from database
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Create new access token and refresh token
    access_token = create_access_token(data={
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    })
    new_refresh_token = create_refresh_token(data={
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    })

    logger.info(
        "token_refreshed",
        extra={"user_id": user.id, "email": user.email},
    )

    return AuthResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            created_at=user.created_at
        )
    )
