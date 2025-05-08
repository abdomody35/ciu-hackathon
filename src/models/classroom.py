from .base import BaseModel


class Classroom(BaseModel):
    table_name = "classrooms"
    primary_key = "classroom_id"
    fields = [
        "classroom_id",
        "instructor_id",
        "name",
        "year",
        "semester",
        "is_active",
        "created_at",
        "updated_at",
    ]
