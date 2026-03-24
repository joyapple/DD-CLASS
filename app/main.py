from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, classes, students, scores, attendance, dashboard, subjects, users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="班级管理系统 API",
    description="轻量化班级管理系统后端API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(classes.router)
app.include_router(students.router)
app.include_router(scores.router)
app.include_router(attendance.router)
app.include_router(dashboard.router)
app.include_router(subjects.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "班级管理系统 API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
