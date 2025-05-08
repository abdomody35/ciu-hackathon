from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict, Optional

from ..models.student import Student
from ..models.classroom_enrollment import ClassroomEnrollment
from ..models.class_session import ClassSession
from ..models.classroom import Classroom
from ..models.attendance import Attendance
from ..schemas import (
    AttendanceCreate,
    AttendanceResponse,
    AttendanceUpdate,
    ProcessAttendanceRequest,
    ProcessAttendanceResponse,
    AttendanceStats,
    StudentAttendanceRecord,
)

from ..utils.auth import admin_or_instructor_required, get_current_user

# from ..utils.face import face_recognition

attendance_router = APIRouter(prefix="/attendance", tags=["Attendance"])


# @attendance_router.post(
#     "/", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED
# )
# async def create_attendance(
#     attendance: AttendanceCreate,
#     current_user: Dict = Depends(admin_or_instructor_required),
# ):
#     """Manually create/update attendance record"""
#     # Check if session exists
#     try:
#         session = ClassSession.getById(attendance.session_id)

#         # If instructor, check if they own the classroom
#         if current_user["role"] == "instructor":
#             classroom = Classroom.getById(session["classroom_id"])
#             if classroom["instructor_id"] != current_user["user_id"]:
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail="You can only manage attendance for your own classrooms",
#                 )
#     except:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Session with ID {attendance.session_id} not found",
#         )

#     # Check if student exists and is enrolled
#     try:
#         student = Student.getById(attendance.student_id)

#         # Check if student is enrolled in the classroom
#         enrollments = ClassroomEnrollment.getAll()
#         if not any(
#             e["classroom_id"] == session["classroom_id"]
#             and e["student_id"] == attendance.student_id
#             for e in enrollments
#         ):
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Student is not enrolled in this classroom",
#             )
#     except:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Student with ID {attendance.student_id} not found",
#         )

#     # Check if attendance record already exists
#     attendances = Attendance.getAll()
#     existing_attendance = next(
#         (
#             a
#             for a in attendances
#             if a["session_id"] == attendance.session_id
#             and a["student_id"] == attendance.student_id
#         ),
#         None,
#     )

#     if existing_attendance:
#         # Update existing attendance
#         updated_attendance = Attendance.update(
#             existing_attendance["attendance_id"],
#             status=attendance.status,
#             marked_by=attendance.marked_by,
#         )
#         return updated_attendance[0]
#     else:
#         # Create new attendance record
#         created_attendance = Attendance.create(
#             session_id=attendance.session_id,
#             student_id=attendance.student_id,
#             status=attendance.status,
#             marked_by=attendance.marked_by,
#         )
#         return created_attendance[0]


# @attendance_router.post("/process", response_model=ProcessAttendanceResponse)
# async def process_attendance_with_face_recognition(
#     request: ProcessAttendanceRequest,
#     current_user: Dict = Depends(admin_or_instructor_required),
# ):
#     """Process attendance using face recognition"""
#     # Check if session exists
#     try:
#         session = ClassSession.getById(request.session_id)

#         # If instructor, check if they own the classroom
#         if current_user["role"] == "instructor":
#             classroom = Classroom.getById(session["classroom_id"])
#             if classroom["instructor_id"] != current_user["user_id"]:
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail="You can only manage attendance for your own classrooms",
#                 )
#     except:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Session with ID {request.session_id} not found",
#         )

#     # Get all students enrolled in this classroom
#     classroom_id = session["classroom_id"]
#     enrollments = ClassroomEnrollment.getAll()
#     classroom_enrollments = [
#         e for e in enrollments if e["classroom_id"] == classroom_id
#     ]

#     # Get student data including face templates
#     student_templates = []
#     for enrollment in classroom_enrollments:
#         try:
#             student = Student.getById(enrollment["student_id"])
#             # Only include students with face templates
#             if student["face_template"]:
#                 student_templates.append(student)
#         except:
#             continue

#     # Process the image
#     recognized_students = face_recognition.process_attendance_image(
#         request.image_data, student_templates
#     )

#     # Mark attendance for recognized students
#     attendances = []
#     for student_info in recognized_students:
#         # Create/update attendance record
#         attendance_data = {
#             "session_id": request.session_id,
#             "student_id": student_info["student_id"],
#             "status": "present",
#             "marked_by": "system",
#         }

#         # Check if record already exists
#         all_attendances = Attendance.getAll()
#         existing = next(
#             (
#                 a
#                 for a in all_attendances
#                 if a["session_id"] == request.session_id
#                 and a["student_id"] == student_info["student_id"]
#             ),
#             None,
#         )

#         if existing:
#             # Update existing record
#             updated = Attendance.update(
#                 existing["attendance_id"], status="present", marked_by="system"
#             )
#             if updated:
#                 attendances.append(updated[0])
#         else:
#             # Create new record
#             created = Attendance.create(**attendance_data)
#             if created:
#                 attendances.append(created[0])

#     return {
#         "session_id": request.session_id,
#         "processed_students": recognized_students,
#         "attendances": attendances,
#     }


# @attendance_router.get(
#     "/sessions/{session_id}", response_model=List[AttendanceResponse]
# )
# async def get_session_attendance(
#     session_id: int, current_user: Dict = Depends(get_current_user)
# ):
#     """Get all attendance records for a session"""
#     # Check if session exists
#     try:
#         session = ClassSession.getById(session_id)

#         # If instructor, check if they own the classroom
#         if current_user["role"] == "instructor":
#             classroom = Classroom.getById(session["classroom_id"])
#             if classroom["instructor_id"] != current_user["user_id"]:
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail="You can only access attendance for your own classrooms",
#                 )
#     except:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Session with ID {session_id} not found",
#         )

#     # Get attendance records
#     attendances = Attendance.getAll()
#     session_attendances = [a for a in attendances if a["session_id"] == session_id]

#     return session_attendances


# @attendance_router.put("/{attendance_id}", response_model=AttendanceResponse)
# async def update_attendance(
#     attendance_id: int,
#     attendance: AttendanceUpdate,
#     current_user: Dict = Depends(admin_or_instructor_required),
# ):
#     """Update an attendance record"""
#     # Check if attendance record exists
#     try:
#         existing_attendance = Attendance.getById(attendance_id)

#         # Get session to check classroom ownership
#         session = ClassSession.getById(existing_attendance["session_id"])

#         # If instructor, check if they own the classroom
#         if current_user["role"] == "instructor":
#             classroom = Classroom.getById(session["classroom_id"])
#             if classroom["instructor_id"] != current_user["user_id"]:
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail="You can only update attendance for your own classrooms",
#                 )

#         # Check if student is enrolled in the classroom
#         enrollments = ClassroomEnrollment.getAll()
#         if not any(
#             e["classroom_id"] == session["classroom_id"]
#             and e["student_id"] == existing_attendance["student_id"]
#             for e in enrollments
#         ):
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Student is not enrolled in this classroom",
#             )

#         # Update attendance record
#         updated_attendance = Attendance.update(
#             attendance_id,
#             status=attendance.status,
#             marked_by=attendance.marked_by,
#         )
#         return updated_attendance[0]

#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Attendance record with ID {attendance_id} not found or error: {str(e)}",
#         )
