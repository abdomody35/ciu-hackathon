from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile, Form
from typing import List, Dict, Optional
import base64
import io

from ..models.student import Student
from ..schemas import StudentCreate, StudentResponse, StudentUpdate
from ..utils.auth import admin_or_instructor_required, get_current_user

# from ..utils.face import face_recognition

student_router = APIRouter(prefix="/students", tags=["Students"])


@student_router.post(
    "/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED
)
async def create_student(
    student: StudentCreate, current_user: Dict = Depends(admin_or_instructor_required)
):
    """Create a new student"""
    # Check if student number already exists
    all_students = Student.getAll()
    if any(s["student_number"] == student.student_number for s in all_students):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student number already registered",
        )

    # Create student with optional face template
    created_student = Student.create(
        name=student.name,
        email=student.email,
        student_number=student.student_number,
        department=student.department,
        face_template=student.face_template,
    )

    return created_student[0]


@student_router.post("/{student_id}/face", response_model=StudentResponse)
async def upload_face_template(
    student_id: int,
    image: str = Form(...),  # Base64 encoded image
    current_user: Dict = Depends(admin_or_instructor_required),
):
    """Upload and process student face for template creation"""
    # try:
    #     # Get student first
    #     student = Student.getById(student_id)

    #     # Create face template
    #     face_template = face_recognition.create_face_template(image)

    #     if not face_template:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Failed to create face template. Make sure the image contains a clear face.",
    #         )

    #     # Update student with face template
    #     updated_student = Student.update(student_id, face_template=face_template)
    #     return updated_student[0]

    # except Exception as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail=f"Student not found or error processing face: {str(e)}",
    #     )


@student_router.get("/", response_model=List[StudentResponse])
async def get_students(
    current_user: Dict = Depends(get_current_user), department: Optional[str] = None
):
    """Get all students with optional department filter"""
    students = Student.getAll()

    if department:
        students = [s for s in students if s["department"] == department]

    return students


@student_router.get("/{student_id}", response_model=StudentResponse)
async def get_student(student_id: int, current_user: Dict = Depends(get_current_user)):
    """Get student by ID"""
    try:
        student = Student.getById(student_id)
        return student
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found",
        )


@student_router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    student: StudentUpdate,
    current_user: Dict = Depends(admin_or_instructor_required),
):
    """Update student information"""
    # Check if student exists
    try:
        existing_student = Student.getById(student_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found",
        )

    # Prepare update data
    update_data = {k: v for k, v in student.dict().items() if v is not None}

    # If updating student number, check if it's unique
    if "student_number" in update_data:
        all_students = Student.getAll()
        if any(
            s["student_number"] == update_data["student_number"]
            and s["student_id"] != student_id
            for s in all_students
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student number already registered",
            )

    # Update student
    updated_student = Student.update(student_id, **update_data)
    return updated_student[0]


@student_router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: int, current_user: Dict = Depends(admin_or_instructor_required)
):
    """Delete student"""
    try:
        Student.delete(student_id)
        return None
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found",
        )
