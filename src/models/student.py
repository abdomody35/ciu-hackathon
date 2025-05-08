from .base import BaseModel


class Student(BaseModel):
    table_name = "students"
    primary_key = "student_id"
    fields = [
        "student_id",
        "name",
        "email",
        "face_template",
        "student_number",
        "department",
        "created_at",
        "updated_at",
    ]
