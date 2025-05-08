from .base import BaseModel


class Admin(BaseModel):
    table_name = "admins"
    primary_key = "admin_id"
    fields = ["admin_id", "email", "password_hash", "name", "created_at", "updated_at"]
