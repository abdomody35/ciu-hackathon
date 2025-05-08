from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict, Optional

from ..models.student import Student
from ..models.classroom_enrollment import ClassroomEnrollment
from ..models.class_session import ClassSession
from ..models.classroom import Classroom
from ..schemas import (
    ClassroomCreate,
    ClassroomResponse,
    ClassroomUpdate,
    EnrollmentCreate,
    EnrollmentResponse,
    BulkEnrollmentCreate,
    ClassSessionCreate,
    ClassSessionResponse,
    ClassSessionUpdate,
    StudentResponse,
)
from ..utils.auth import (
    admin_or_instructor_required,
    get_current_user,
    instructor_required,
)

classroom_router = APIRouter(prefix="/classrooms", tags=["Classrooms"])


@classroom_router.post(
    "/", response_model=ClassroomResponse, status_code=status.HTTP_201_CREATED
)
async def create_classroom(
    classroom: ClassroomCreate,
    current_user: Dict = Depends(admin_or_instructor_required),
):
    """Create a new classroom"""
    # Check if instructor exists
    try:
        # For admin users, they can create classrooms for any instructor
        if (
            current_user["role"] == "instructor"
            and current_user["user_id"] != classroom.instructor_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create classrooms for yourself",
            )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Instructor with ID {classroom.instructor_id} not found",
        )

    # Create classroom
    created_classroom = Classroom.create(
        instructor_id=classroom.instructor_id,
        name=classroom.name,
        year=classroom.year,
        semester=classroom.semester,
        is_active=classroom.is_active,
    )

    return created_classroom[0]


@classroom_router.get("/", response_model=List[ClassroomResponse])
async def get_classrooms(
    current_user: Dict = Depends(get_current_user),
    year: Optional[int] = None,
    semester: Optional[str] = None,
    instructor_id: Optional[int] = None,
    is_active: Optional[bool] = None,
):
    """Get all classrooms with optional filters"""
    classrooms = Classroom.getAll()

    # Apply filters if provided
    if year:
        classrooms = [c for c in classrooms if c["year"] == year]
    if semester:
        classrooms = [c for c in classrooms if c["semester"] == semester]
    if instructor_id:
        classrooms = [c for c in classrooms if c["instructor_id"] == instructor_id]
    if is_active is not None:
        classrooms = [c for c in classrooms if c["is_active"] == is_active]

    # For instructors, only show their classrooms
    if current_user["role"] == "instructor":
        classrooms = [
            c for c in classrooms if c["instructor_id"] == current_user["user_id"]
        ]

    return classrooms


@classroom_router.get("/{classroom_id}", response_model=ClassroomResponse)
async def get_classroom(
    classroom_id: int, current_user: Dict = Depends(get_current_user)
):
    """Get classroom by ID"""
    try:
        classroom = Classroom.getById(classroom_id)

        # Check if instructor is accessing their own classroom
        if (
            current_user["role"] == "instructor"
            and classroom["instructor_id"] != current_user["user_id"]
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own classrooms",
            )

        return classroom
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classroom with ID {classroom_id} not found",
        )


@classroom_router.put("/{classroom_id}", response_model=ClassroomResponse)
async def update_classroom(
    classroom_id: int,
    classroom: ClassroomUpdate,
    current_user: Dict = Depends(admin_or_instructor_required),
):
    """Update classroom information"""
    # Check if classroom exists
    try:
        existing_classroom = Classroom.getById(classroom_id)

        # Check if instructor is updating their own classroom
        if (
            current_user["role"] == "instructor"
            and existing_classroom["instructor_id"] != current_user["user_id"]
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own classrooms",
            )
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classroom with ID {classroom_id} not found",
        )

    # Prepare update data
    update_data = {k: v for k, v in classroom.dict().items() if v is not None}

    # If instructor_id is being updated, check if instructor exists
    if "instructor_id" in update_data and current_user["role"] == "instructor":
        if update_data["instructor_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot transfer classroom to another instructor",
            )

    # Update classroom
    updated_classroom = Classroom.update(classroom_id, **update_data)
    return updated_classroom[0]


@classroom_router.delete("/{classroom_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_classroom(
    classroom_id: int, current_user: Dict = Depends(admin_or_instructor_required)
):
    """Delete classroom"""
    try:
        existing_classroom = Classroom.getById(classroom_id)

        # Check if instructor is deleting their own classroom
        if (
            current_user["role"] == "instructor"
            and existing_classroom["instructor_id"] != current_user["user_id"]
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own classrooms",
            )

        Classroom.delete(classroom_id)
        return None
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classroom with ID {classroom_id} not found",
        )


# Enrollment endpoints
@classroom_router.post(
    "/enrollments",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_enrollment(
    enrollment: EnrollmentCreate,
    current_user: Dict = Depends(admin_or_instructor_required),
):
    """Enroll a student in a classroom"""
    # Check if classroom exists and instructor owns it
    try:
        classroom = Classroom.getById(enrollment.classroom_id)

        # Check if instructor owns the classroom
        if (
            current_user["role"] == "instructor"
            and classroom["instructor_id"] != current_user["user_id"]
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only enroll students in your own classrooms",
            )
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classroom with ID {enrollment.classroom_id} not found",
        )

    # Check if student exists
    try:
        Student.getById(enrollment.student_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {enrollment.student_id} not found",
        )

    # Check if enrollment already exists
    enrollments = ClassroomEnrollment.getAll()
    if any(
        e["classroom_id"] == enrollment.classroom_id
        and e["student_id"] == enrollment.student_id
        for e in enrollments
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student is already enrolled in this classroom",
        )

    # Create enrollment
    created_enrollment = ClassroomEnrollment.create(
        classroom_id=enrollment.classroom_id, student_id=enrollment.student_id
    )

    return created_enrollment[0]


@classroom_router.post(
    "/bulk-enrollments",
    response_model=List[EnrollmentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_bulk_enrollments(
    enrollment_data: BulkEnrollmentCreate,
    current_user: Dict = Depends(admin_or_instructor_required),
):
    """Enroll multiple students in a classroom at once"""
    # Check if classroom exists and instructor owns it
    try:
        classroom = Classroom.getById(enrollment_data.classroom_id)

        # Check if instructor owns the classroom
        if (
            current_user["role"] == "instructor"
            and classroom["instructor_id"] != current_user["user_id"]
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only enroll students in your own classrooms",
            )
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classroom with ID {enrollment_data.classroom_id} not found",
        )

    # Get existing enrollments
    enrollments = ClassroomEnrollment.getAll()
    existing_enrollments = [
        e["student_id"]
        for e in enrollments
        if e["classroom_id"] == enrollment_data.classroom_id
    ]

    # Process each student
    created_enrollments = []
    for student_id in enrollment_data.student_ids:
        # Skip if already enrolled
        if student_id in existing_enrollments:
            continue

        # Check if student exists
        try:
            Student.getById(student_id)
        except:
            continue  # Skip invalid student IDs

        # Create enrollment
        created = ClassroomEnrollment.create(
            classroom_id=enrollment_data.classroom_id, student_id=student_id
        )

        if created:
            created_enrollments.append(created[0])

    return created_enrollments


@classroom_router.get("/{classroom_id}/students", response_model=List[StudentResponse])
async def get_classroom_students(
    classroom_id: int, current_user: Dict = Depends(get_current_user)
):
    """Get all students enrolled in a classroom"""
    # Check if classroom exists
    try:
        classroom = Classroom.getById(classroom_id)

        # Check if instructor is accessing their own classroom
        if (
            current_user["role"] == "instructor"
            and classroom["instructor_id"] != current_user["user_id"]
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own classrooms",
            )
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classroom with ID {classroom_id} not found",
        )

    # Get enrollments for this classroom
    enrollments = ClassroomEnrollment.getAll()
    classroom_enrollments = [
        e for e in enrollments if e["classroom_id"] == classroom_id
    ]

    # Get students
    students = []
    for enrollment in classroom_enrollments:
        try:
            student = Student.getById(enrollment["student_id"])
            students.append(student)
        except:
            continue

    return students


@classroom_router.delete(
    "/enrollments/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_enrollment(
    enrollment_id: int, current_user: Dict = Depends(admin_or_instructor_required)
):
    """Remove a student from a classroom"""
    try:
        # Get enrollment first
        enrollment = ClassroomEnrollment.getById(enrollment_id)

        # Check if instructor owns the classroom
        if current_user["role"] == "instructor":
            classroom = Classroom.getById(enrollment["classroom_id"])
            if classroom["instructor_id"] != current_user["user_id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only remove students from your own classrooms",
                )

        # Delete enrollment
        ClassroomEnrollment.delete(enrollment_id)
        return None
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enrollment with ID {enrollment_id} not found",
        )


# Class Session endpoints
@classroom_router.post(
    "/sessions",
    response_model=ClassSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_class_session(
    session: ClassSessionCreate,
    current_user: Dict = Depends(admin_or_instructor_required),
):
    """Create a new class session"""
    # Check if classroom exists
    try:
        classroom = Classroom.getById(session.classroom_id)

        # Check if instructor owns the classroom
        if (
            current_user["role"] == "instructor"
            and classroom["instructor_id"] != current_user["user_id"]
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create sessions for your own classrooms",
            )
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classroom with ID {session.classroom_id} not found",
        )

    # Create session
    created_session = ClassSession.create(
        classroom_id=session.classroom_id,
        session_date=session.session_date,
        start_time=session.start_time,
        end_time=session.end_time,
    )

    return created_session[0]


@classroom_router.get(
    "/{classroom_id}/sessions", response_model=List[ClassSessionResponse]
)
async def get_classroom_sessions(
    classroom_id: int, current_user: Dict = Depends(get_current_user)
):
    """Get all sessions for a classroom"""
    # Check if classroom exists
    try:
        classroom = Classroom.getById(classroom_id)

        # Check if instructor is accessing their own classroom
        if (
            current_user["role"] == "instructor"
            and classroom["instructor_id"] != current_user["user_id"]
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own classrooms",
            )
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classroom with ID {classroom_id} not found",
        )

    # Get all sessions
    sessions = ClassSession.getAll()
    classroom_sessions = [s for s in sessions if s["classroom_id"] == classroom_id]

    return classroom_sessions


@classroom_router.put("/sessions/{session_id}", response_model=ClassSessionResponse)
async def update_class_session(
    session_id: int,
    session: ClassSessionUpdate,
    current_user: Dict = Depends(admin_or_instructor_required),
):
    """Update a class session"""
    # Check if session exists
    try:
        existing_session = ClassSession.getById(session_id)

        # Check if instructor owns the classroom
        if current_user["role"] == "instructor":
            classroom = Classroom.getById(existing_session["classroom_id"])
            if classroom["instructor_id"] != current_user["user_id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only update sessions for your own classrooms",
                )
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found",
        )

    # Prepare update data
    update_data = {k: v for k, v in session.dict().items() if v is not None}

    # Update session
    updated_session = ClassSession.update(session_id, **update_data)
    return updated_session[0]


@classroom_router.delete(
    "/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_class_session(
    session_id: int, current_user: Dict = Depends(admin_or_instructor_required)
):
    """Delete a class session"""
    try:
        # Get session first
        session = ClassSession.getById(session_id)

        # Check if instructor owns the classroom
        if current_user["role"] == "instructor":
            classroom = Classroom.getById(session["classroom_id"])
            if classroom["instructor_id"] != current_user["user_id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only delete sessions for your own classrooms",
                )

        # Delete session
        ClassSession.delete(session_id)
        return None
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found",
        )
