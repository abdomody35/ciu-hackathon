from .base import BaseModel


class Attendance(BaseModel):
    table_name = "attendances"
    primary_key = "attendance_id"
    fields = [
        "attendance_id",
        "session_id",
        "student_id",
        "status",
        "marked_by",
        "created_at",
        "updated_at",
    ]
