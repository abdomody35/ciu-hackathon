from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict

from ..models.instructor import Instructor
from ..models.admin import Admin
from ..schemas import LoginRequest, Token, RefreshTokenRequest
from ..utils.auth import (
    verify_password,
    create_tokens,
    decode_token,
    get_current_user,
)

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/login", response_model=Token)
async def login(request: LoginRequest):
    """Authenticate admin or instructor and provide JWT tokens"""
    # Try to find the user in admin table first
    admin_result = Admin.getAll()
    admin = next((a for a in admin_result if a["email"] == request.email), None)

    if admin and verify_password(request.password, admin["password_hash"]):
        access_token, refresh_token = create_tokens(admin["admin_id"], "admin")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    # Try instructor table if admin not found or password incorrect
    instructor_result = Instructor.getAll()
    instructor = next(
        (i for i in instructor_result if i["email"] == request.email), None
    )

    if instructor and verify_password(request.password, instructor["password_hash"]):
        access_token, refresh_token = create_tokens(
            instructor["instructor_id"], "instructor"
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    # If no valid user found, raise exception
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


@auth_router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest):
    """Get new access token using refresh token"""
    try:
        payload = decode_token(request.refresh_token)

        # Verify this is a refresh token
        if not payload.get("token_type") == "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create new tokens
        user_id = int(payload["sub"])
        role = payload["role"]
        access_token, refresh_token = create_tokens(user_id, role)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@auth_router.get("/me")
async def get_me(current_user: Dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user
