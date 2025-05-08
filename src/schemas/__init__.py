from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import date, time, datetime
from enum import Enum


# Enums
class SemesterEnum(str, Enum):
    FALL = "fall"
    SPRING = "spring"
    SUMMER = "summer"


class AttendanceStatusEnum(str, Enum):
    ABSENT = "absent"
    PRESENT = "present"


class MarkedByEnum(str, Enum):
    SYSTEM = "system"
    INSTRUCTOR = "instructor"


# Auth Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# Admin Schemas
class AdminBase(BaseModel):
    email: EmailStr
    name: str


class AdminCreate(AdminBase):
    password: str = Field(..., min_length=8)


class AdminResponse(AdminBase):
    admin_id: int
    created_at: datetime
    updated_at: datetime


# Instructor Schemas
class InstructorBase(BaseModel):
    email: EmailStr
    name: str


class InstructorCreate(InstructorBase):
    password: str = Field(..., min_length=8)


class InstructorResponse(InstructorBase):
    instructor_id: int
    created_at: datetime
    updated_at: datetime


# Student Schemas
class StudentBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    student_number: int
    department: Optional[str] = None


class StudentCreate(StudentBase):
    face_template: Optional[bytes] = None


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    student_number: Optional[int] = None
    department: Optional[str] = None
    face_template: Optional[bytes] = None


class StudentResponse(StudentBase):
    student_id: int
    created_at: datetime
    updated_at: datetime
    face_template: Optional[bytes] = None


# Classroom Schemas
class ClassroomBase(BaseModel):
    name: str
    year: int
    semester: SemesterEnum
    is_active: bool = True


class ClassroomCreate(ClassroomBase):
    instructor_id: int


class ClassroomUpdate(BaseModel):
    name: Optional[str] = None
    year: Optional[int] = None
    semester: Optional[SemesterEnum] = None
    is_active: Optional[bool] = None
    instructor_id: Optional[int] = None


class ClassroomResponse(ClassroomBase):
    classroom_id: int
    instructor_id: int
    created_at: datetime
    updated_at: datetime


# Classroom Enrollment Schemas
class EnrollmentCreate(BaseModel):
    classroom_id: int
    student_id: int


class EnrollmentResponse(EnrollmentCreate):
    enrollment_id: int
    created_at: datetime
    updated_at: datetime


class BulkEnrollmentCreate(BaseModel):
    classroom_id: int
    student_ids: List[int]


# Class Session Schemas
class ClassSessionBase(BaseModel):
    classroom_id: int
    session_date: date
    start_time: time
    end_time: time


class ClassSessionCreate(ClassSessionBase):
    pass


class ClassSessionUpdate(BaseModel):
    session_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None


class ClassSessionResponse(ClassSessionBase):
    session_id: int
    created_at: datetime
    updated_at: datetime


# Attendance Schemas
class AttendanceBase(BaseModel):
    session_id: int
    student_id: int
    status: AttendanceStatusEnum
    marked_by: MarkedByEnum


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseModel):
    status: AttendanceStatusEnum
    marked_by: MarkedByEnum


class AttendanceResponse(AttendanceBase):
    attendance_id: int
    created_at: datetime
    updated_at: datetime


# Face Recognition Schemas
class FaceDetectionResult(BaseModel):
    student_id: int
    confidence: float


class ProcessAttendanceRequest(BaseModel):
    session_id: int
    image_data: str  # Base64 encoded image


class ProcessAttendanceResponse(BaseModel):
    session_id: int
    processed_students: List[Dict[str, Any]]
    attendances: List[AttendanceResponse]


# Dashboard Schemas
class AttendanceStats(BaseModel):
    total_sessions: int
    total_students: int
    present_count: int
    absent_count: int
    attendance_rate: float


class StudentAttendanceRecord(BaseModel):
    student_id: int
    student_name: str
    present_count: int
    absent_count: int
    attendance_rate: float
