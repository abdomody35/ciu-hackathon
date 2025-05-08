from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict

from ..models.instructor import Instructor
from ..schemas import InstructorCreate, InstructorResponse
from ..utils.auth import (
    hash_password,
    admin_required,
    get_current_user,
    instructor_required,
)

instructor_router = APIRouter(prefix="/instructors", tags=["Instructors"])


@instructor_router.post(
    "/", response_model=InstructorResponse, status_code=status.HTTP_201_CREATED
)
async def create_instructor(
    instructor: InstructorCreate, current_user: Dict = Depends(admin_required)
):
    """Create a new instructor (admin only)"""
    # Check if email already exists
    all_instructors = Instructor.getAll()
    if any(i["email"] == instructor.email for i in all_instructors):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Hash password
    hashed_password = hash_password(instructor.password)

    # Create instructor
    created_instructor = Instructor.create(
        email=instructor.email, password_hash=hashed_password, name=instructor.name
    )

    return created_instructor[0]


@instructor_router.get("/", response_model=List[InstructorResponse])
async def get_instructors(current_user: Dict = Depends(get_current_user)):
    """Get all instructors (any authenticated user)"""
    instructors = Instructor.getAll()
    return instructors


@instructor_router.get("/{instructor_id}", response_model=InstructorResponse)
async def get_instructor(
    instructor_id: int, current_user: Dict = Depends(get_current_user)
):
    """Get instructor by ID (any authenticated user)"""
    try:
        instructor = Instructor.getById(instructor_id)
        return instructor
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instructor with ID {instructor_id} not found",
        )


@instructor_router.get("/me/profile", response_model=InstructorResponse)
async def get_instructor_profile(current_user: Dict = Depends(instructor_required)):
    """Get current instructor's profile (instructor only)"""
    try:
        instructor = Instructor.getById(current_user["user_id"])
        return instructor
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Instructor profile not found"
        )


@instructor_router.delete("/{instructor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_instructor(
    instructor_id: int, current_user: Dict = Depends(admin_required)
):
    """Delete instructor (admin only)"""
    try:
        Instructor.delete(instructor_id)
        return None
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instructor with ID {instructor_id} not found",
        )
