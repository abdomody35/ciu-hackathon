from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict

from ..models.admin import Admin
from ..schemas import AdminCreate, AdminResponse
from ..utils.auth import hash_password, admin_required

admin_router = APIRouter(prefix="/admins", tags=["Admins"])


@admin_router.post(
    "/", response_model=AdminResponse, status_code=status.HTTP_201_CREATED
)
async def create_admin(
    admin: AdminCreate, current_user: Dict = Depends(admin_required)
):
    """Create a new admin (only existing admins can create new admins)"""
    # Check if email already exists
    all_admins = Admin.getAll()
    if any(a["email"] == admin.email for a in all_admins):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Hash password
    hashed_password = hash_password(admin.password)

    # Create admin
    created_admin = Admin.create(
        email=admin.email, password_hash=hashed_password, name=admin.name
    )

    return created_admin[0]


@admin_router.get("/", response_model=List[AdminResponse])
async def get_admins(current_user: Dict = Depends(admin_required)):
    """Get all admins (admin only)"""
    admins = Admin.getAll()
    return admins


@admin_router.get("/{admin_id}", response_model=AdminResponse)
async def get_admin(admin_id: int, current_user: Dict = Depends(admin_required)):
    """Get admin by ID (admin only)"""
    try:
        admin = Admin.getById(admin_id)
        return admin
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Admin with ID {admin_id} not found",
        )


@admin_router.delete("/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin(admin_id: int, current_user: Dict = Depends(admin_required)):
    """Delete admin (admin only)"""
    # Check if this is the last admin
    all_admins = Admin.getAll()
    if len(all_admins) <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the last admin",
        )

    # Can't delete yourself
    if current_user["user_id"] == admin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    try:
        Admin.delete(admin_id)
        return None
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Admin with ID {admin_id} not found",
        )
