from .base import BaseModel


class ClassSession(BaseModel):
    table_name = "class_sessions"
    primary_key = "session_id"
    fields = [
        "session_id",
        "classroom_id",
        "session_date",
        "start_time",
        "end_time",
        "created_at",
        "updated_at",
    ]
