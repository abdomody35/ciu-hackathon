from .base import BaseModel


class ClassroomEnrollment(BaseModel):
    table_name = "classroom_enrollments"
    primary_key = "enrollment_id"
    fields = ["enrollment_id", "classroom_id", "student_id", "created_at", "updated_at"]
