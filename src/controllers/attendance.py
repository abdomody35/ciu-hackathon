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
#     except:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Attendance record with ID {attendance_id} not found",
#         )

#     # Update attendance record
#     updated_attendance = Attendance.update(
#         attendance_id,
#         status=attendance.status,
#         marked_by=attendance.marked_by,
#     )

#     return updated_attendance[0]


# @attendance_router.delete("/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_attendance(
#     attendance_id: int, current_user: Dict = Depends(admin_or_instructor_required)
# ):
#     """Delete an attendance record"""
#     try:
#         # Get attendance record first
#         existing_attendance = Attendance.getById(attendance_id)

#         # Get session to check classroom ownership
#         session = ClassSession.getById(existing_attendance["session_id"])

#         # If instructor, check if they own the classroom
#         if current_user["role"] == "instructor":
#             classroom = Classroom.getById(session["classroom_id"])
#             if classroom["instructor_id"] != current_user["user_id"]:
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail="You can only delete attendance for your own classrooms",
#                 )

#         # Delete attendance record
#         Attendance.delete(attendance_id)
#         return None
#     except:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Attendance record with ID {attendance_id} not found",
#         )


# @attendance_router.get(
#     "/classroom/{classroom_id}/stats", response_model=AttendanceStats
# )
# async def get_classroom_attendance_stats(
#     classroom_id: int, current_user: Dict = Depends(get_current_user)
# ):
#     """Get attendance statistics for a classroom"""
#     # Check if classroom exists
#     try:
#         classroom = Classroom.getById(classroom_id)

#         # If instructor, check if they own the classroom
#         if current_user["role"] == "instructor":
#             if classroom["instructor_id"] != current_user["user_id"]:
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail="You can only access stats for your own classrooms",
#                 )
#     except:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Classroom with ID {classroom_id} not found",
#         )

#     # Get all sessions for this classroom
#     sessions = ClassSession.getAll()
#     classroom_sessions = [s for s in sessions if s["classroom_id"] == classroom_id]

#     # Get all enrollments for this classroom
#     enrollments = ClassroomEnrollment.getAll()
#     classroom_enrollments = [
#         e for e in enrollments if e["classroom_id"] == classroom_id
#     ]

#     # Get all attendance records for classroom sessions
#     attendances = Attendance.getAll()
#     classroom_attendances = [
#         a
#         for a in attendances
#         if any(s["session_id"] == a["session_id"] for s in classroom_sessions)
#     ]

#     # Calculate statistics
#     total_sessions = len(classroom_sessions)
#     total_students = len(classroom_enrollments)
#     present_count = len([a for a in classroom_attendances if a["status"] == "present"])
#     absent_count = len([a for a in classroom_attendances if a["status"] == "absent"])

#     # Calculate attendance rate
#     total_possible_attendances = total_sessions * total_students
#     attendance_rate = (
#         (present_count / total_possible_attendances) * 100
#         if total_possible_attendances > 0
#         else 0
#     )

#     return {
#         "total_sessions": total_sessions,
#         "total_students": total_students,
#         "present_count": present_count,
#         "absent_count": absent_count,
#         "attendance_rate": attendance_rate,
#     }


# @attendance_router.get(
#     "/student/{student_id}/classroom/{classroom_id}",
#     response_model=StudentAttendanceRecord,
# )
# async def get_student_attendance_record(
#     student_id: int, classroom_id: int, current_user: Dict = Depends(get_current_user)
# ):
#     """Get attendance record for a specific student in a classroom"""
#     # Check if classroom exists
#     try:
#         classroom = Classroom.getById(classroom_id)

#         # If instructor, check if they own the classroom
#         if current_user["role"] == "instructor":
#             if classroom["instructor_id"] != current_user["user_id"]:
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail="You can only access attendance for your own classrooms",
#                 )
#     except:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Classroom with ID {classroom_id} not found",
#         )

#     # Check if student exists
#     try:
#         student = Student.getById(student_id)
#     except:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Student with ID {student_id} not found",
#         )

#     # Check if student is enrolled in classroom
#     enrollments = ClassroomEnrollment.getAll()
#     if not any(
#         e["classroom_id"] == classroom_id and e["student_id"] == student_id
#         for e in enrollments
#     ):
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Student with ID {student_id} is not enrolled in classroom with ID {classroom_id}",
#         )

#     # Get all sessions for this classroom
#     sessions = ClassSession.getAll()
#     classroom_sessions = [s for s in sessions if s["classroom_id"] == classroom_id]

#     # Get all attendance records for this student in this classroom
#     attendances = Attendance.getAll()
#     student_attendances = [
#         a
#         for a in attendances
#         if a["student_id"] == student_id
#         and any(s["session_id"] == a["session_id"] for s in classroom_sessions)
#     ]

#     # Calculate statistics
#     present_count = len([a for a in student_attendances if a["status"] == "present"])
#     absent_count = len([a for a in student_attendances if a["status"] == "absent"])
#     total_sessions = len(classroom_sessions)

#     # Calculate attendance rate
#     attendance_rate = (
#         (present_count / total_sessions) * 100 if total_sessions > 0 else 0
#     )

#     return {
#         "student_id": student_id,
#         "student_name": student["name"],
#         "present_count": present_count,
#         "absent_count": absent_count,
#         "attendance_rate": attendance_rate,
#     }


# @attendance_router.get(
#     "/classroom/{classroom_id}/records", response_model=List[StudentAttendanceRecord]
# )
# async def get_classroom_attendance_records(
#     classroom_id: int, current_user: Dict = Depends(get_current_user)
# ):
#     """Get attendance records for all students in a classroom"""
#     # Check if classroom exists
#     try:
#         classroom = Classroom.getById(classroom_id)

#         # If instructor, check if they own the classroom
#         if current_user["role"] == "instructor":
#             if classroom["instructor_id"] != current_user["user_id"]:
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail="You can only access attendance for your own classrooms",
#                 )
#     except:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Classroom with ID {classroom_id} not found",
#         )

#     # Get all enrollments for this classroom
#     enrollments = ClassroomEnrollment.getAll()
#     classroom_enrollments = [
#         e for e in enrollments if e["classroom_id"] == classroom_id
#     ]

#     # Get all sessions for this classroom
#     sessions = ClassSession.getAll()
#     classroom_sessions = [s for s in sessions if s["classroom_id"] == classroom_id]
#     total_sessions = len(classroom_sessions)

#     # Get all attendance records for classroom sessions
#     attendances = Attendance.getAll()

#     # Get all students
#     students = Student.getAll()

#     # Calculate attendance records for each enrolled student
#     student_records = []
#     for enrollment in classroom_enrollments:
#         student_id = enrollment["student_id"]
#         student = next((s for s in students if s["student_id"] == student_id), None)

#         if student:
#             # Get attendance records for this student
#             student_attendances = [
#                 a
#                 for a in attendances
#                 if a["student_id"] == student_id
#                 and any(s["session_id"] == a["session_id"] for s in classroom_sessions)
#             ]

#             present_count = len(
#                 [a for a in student_attendances if a["status"] == "present"]
#             )
#             absent_count = len(
#                 [a for a in student_attendances if a["status"] == "absent"]
#             )

#             # Calculate attendance rate
#             attendance_rate = (
#                 (present_count / total_sessions) * 100 if total_sessions > 0 else 0
#             )

#             student_records.append(
#                 {
#                     "student_id": student_id,
#                     "student_name": student["name"],
#                     "present_count": present_count,
#                     "absent_count": absent_count,
#                     "attendance_rate": attendance_rate,
#                 }
#             )

#     return student_records


# @attendance_router.post("/mark-absences/{session_id}", status_code=status.HTTP_200_OK)
# async def mark_absent_students(
#     session_id: int, current_user: Dict = Depends(admin_or_instructor_required)
# ):
#     """Mark all students without attendance records as absent"""
#     # Check if session exists
#     try:
#         session = ClassSession.getById(session_id)

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
#             detail=f"Session with ID {session_id} not found",
#         )

#     # Get classroom ID
#     classroom_id = session["classroom_id"]

#     # Get all students enrolled in this classroom
#     enrollments = ClassroomEnrollment.getAll()
#     classroom_enrollments = [
#         e for e in enrollments if e["classroom_id"] == classroom_id
#     ]

#     # Get existing attendance records for this session
#     attendances = Attendance.getAll()
#     session_attendances = [a for a in attendances if a["session_id"] == session_id]

#     # Get student IDs with existing attendance
#     students_with_attendance = [a["student_id"] for a in session_attendances]

#     # Mark absent for students without attendance records
#     created_records = []
#     for enrollment in classroom_enrollments:
#         student_id = enrollment["student_id"]

#         # Skip if student already has an attendance record
#         if student_id in students_with_attendance:
#             continue

#         # Create absent record
#         attendance_data = {
#             "session_id": session_id,
#             "student_id": student_id,
#             "status": "absent",
#             "marked_by": (
#                 "instructor" if current_user["role"] == "instructor" else "admin"
#             ),
#         }

#         created = Attendance.create(**attendance_data)
#         if created:
#             created_records.append(created[0])

#     return {"session_id": session_id, "absent_records_created": len(created_records)}


# @attendance_router.get("/session/{session_id}/stats", response_model=AttendanceStats)
# async def get_session_attendance_stats(
#     session_id: int, current_user: Dict = Depends(get_current_user)
# ):
#     """Get attendance statistics for a specific session"""
#     # Check if session exists
#     try:
#         session = ClassSession.getById(session_id)

#         # If instructor, check if they own the classroom
#         if current_user["role"] == "instructor":
#             classroom = Classroom.getById(session["classroom_id"])
#             if classroom["instructor_id"] != current_user["user_id"]:
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail="You can only access stats for your own classrooms",
#                 )
#     except:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Session with ID {session_id} not found",
#         )

#     # Get classroom ID
#     classroom_id = session["classroom_id"]

#     # Get all students enrolled in this classroom
#     enrollments = ClassroomEnrollment.getAll()
#     classroom_enrollments = [
#         e for e in enrollments if e["classroom_id"] == classroom_id
#     ]
#     total_students = len(classroom_enrollments)

#     # Get attendance records for this session
#     attendances = Attendance.getAll()
#     session_attendances = [a for a in attendances if a["session_id"] == session_id]

#     # Calculate statistics
#     present_count = len([a for a in session_attendances if a["status"] == "present"])
#     absent_count = len([a for a in session_attendances if a["status"] == "absent"])

#     # Calculate attendance rate
#     attendance_rate = (
#         (present_count / total_students) * 100 if total_students > 0 else 0
#     )

#     return {
#         "total_sessions": 1,  # Always 1 for a single session
#         "total_students": total_students,
#         "present_count": present_count,
#         "absent_count": absent_count,
#         "attendance_rate": attendance_rate,
#     }
