from fastapi import FastAPI, Depends
import uvicorn
from src.controllers.auth import auth_router
from src.controllers.admin import admin_router
from src.controllers.instructor import instructor_router
from src.controllers.student import student_router
from src.controllers.classroom import classroom_router
from src.controllers.attendance import attendance_router
from src.database.connection import db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Student Attendance System",
    description="Automatic facial recognition attendance system",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(instructor_router)
app.include_router(student_router)
app.include_router(classroom_router)
app.include_router(attendance_router)


@app.on_event("startup")
async def startup():
    """Initialize database connection on startup"""
    db.connect()


@app.on_event("shutdown")
async def shutdown():
    """Close database connection on shutdown"""
    db.disconnect()


@app.get("/")
async def root():
    """Root endpoint to verify API is working"""
    return {"message": "Student Attendance System API is running"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
