from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.database import get_db
from models.user import User
from schemas.auth import UserResponse
from utils.role_dependencies import require_admin, require_support_agent, require_customer

router = APIRouter(prefix="/api", tags=["role-based"])

@router.get("/admin/dashboard", response_model=dict)
async def admin_dashboard(current_user: User = Depends(require_admin)):
    """Admin only dashboard"""
    return {
        "message": "Welcome to Admin Dashboard",
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role
        },
        "data": {
            "total_users": "Admin can see all users",
            "system_stats": "Admin can access system statistics"
        }
    }

@router.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Get all users - admin only"""
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            created_at=user.created_at
        )
        for user in users
    ]

@router.get("/support/tickets", response_model=dict)
async def support_tickets(current_user: User = Depends(require_support_agent)):
    """Support agent only tickets"""
    return {
        "message": "Welcome to Support Tickets",
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role
        },
        "data": {
            "tickets": "Support agent can view and manage tickets",
            "customer_interactions": "Support agent can interact with customers"
        }
    }

@router.get("/customer/profile", response_model=UserResponse)
async def customer_profile(current_user: User = Depends(require_customer)):
    """Customer profile - any authenticated user"""
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        created_at=current_user.created_at
    )

@router.get("/public/info", response_model=dict)
async def public_info():
    """Public endpoint - no authentication required"""
    return {
        "message": "Public information",
        "data": {
            "service": "AI Customer Support & Sales Agent SaaS",
            "version": "1.0.0",
            "description": "Role-based authentication system"
        }
    }
