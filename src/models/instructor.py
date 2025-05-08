from .base import BaseModel


class Instructor(BaseModel):
    table_name = "instructors"
    primary_key = "instructor_id"
    fields = [
        "instructor_id",
        "email",
        "password_hash",
        "name",
        "created_at",
        "updated_at",
    ]
