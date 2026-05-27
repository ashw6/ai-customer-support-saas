from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional
from utils.roles import UserRole
import re

# Request schemas
class UserRegister(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., max_length=72)
    role: Optional[UserRole] = Field(
        default=UserRole.CUSTOMER,
        description="Role to create for demo/local registration.",
    )
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError(
                "Password must be at least 8 characters long"
            )

        if not re.search(r"[A-Z]", v):
            raise ValueError(
                "Password must contain at least one uppercase letter"
            )

        if not re.search(r"[a-z]", v):
            raise ValueError(
                "Password must contain at least one lowercase letter"
            )

        if not re.search(r"\d", v):
            raise ValueError(
                "Password must contain at least one number"
            )

        return v
    

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)
    role: Optional[UserRole] = Field(
        default=None,
        description="Optional role to validate during login. If provided, user must have this role.",
    )


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=32, max_length=256)
    password: str = Field(..., max_length=72)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        return v


class MessageResponse(BaseModel):
    message: str


class PasswordResetResponse(MessageResponse):
    email_sent: bool = False
    dev_reset_url: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)

# Response schemas
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: UserRole
    created_at: datetime

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str
    user: UserResponse

class Token(BaseModel):
    access_token: str
    token_type: str
