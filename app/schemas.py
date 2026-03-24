from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    LEAVE = "leave"

class UserBase(BaseModel):
    username: str
    real_name: str
    role: UserRole = UserRole.TEACHER
    class_id: Optional[int] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    real_name: Optional[str] = None
    role: Optional[UserRole] = None
    class_id: Optional[int] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    class_id: Optional[int] = None

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ClassBase(BaseModel):
    name: str
    grade: int

class ClassCreate(ClassBase):
    pass

class ClassUpdate(BaseModel):
    name: Optional[str] = None
    grade: Optional[int] = None

class ClassResponse(ClassBase):
    id: int
    created_at: datetime
    student_count: Optional[int] = 0

    class Config:
        from_attributes = True

class StudentBase(BaseModel):
    name: str
    student_no: str
    gender: Optional[Gender] = None
    phone: Optional[str] = None
    parent_phone: Optional[str] = None
    address: Optional[str] = None
    class_id: int

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    student_no: Optional[str] = None
    gender: Optional[Gender] = None
    phone: Optional[str] = None
    parent_phone: Optional[str] = None
    address: Optional[str] = None
    class_id: Optional[int] = None

class StudentResponse(StudentBase):
    id: int
    teacher_id: Optional[int] = None
    created_at: datetime
    class_name: Optional[str] = None

    class Config:
        from_attributes = True

class SubjectBase(BaseModel):
    name: str

class SubjectCreate(SubjectBase):
    pass

class SubjectResponse(SubjectBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ScoreBase(BaseModel):
    student_id: int
    subject_id: int
    class_id: int
    score: float
    exam_type: str = "midterm"
    semester: str

class ScoreCreate(ScoreBase):
    pass

class ScoreUpdate(BaseModel):
    score: Optional[float] = None
    exam_type: Optional[str] = None
    semester: Optional[str] = None

class ScoreResponse(ScoreBase):
    id: int
    class_id: int
    created_at: datetime
    student_name: Optional[str] = None
    subject_name: Optional[str] = None

    class Config:
        from_attributes = True

class AttendanceBase(BaseModel):
    student_id: int
    date: datetime
    status: AttendanceStatus = AttendanceStatus.PRESENT
    remark: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    status: Optional[AttendanceStatus] = None
    remark: Optional[str] = None

class AttendanceResponse(AttendanceBase):
    id: int
    class_id: int
    created_at: datetime
    student_name: Optional[str] = None

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_students: int
    total_classes: int
    total_scores: int
    avg_score: float
    attendance_rate: float
    recent_scores: List[ScoreResponse] = []
    class_rankings: List[dict] = []

class ClassRanking(BaseModel):
    class_id: int
    class_name: str
    avg_score: float
    rank: int

class StudentRanking(BaseModel):
    student_id: int
    student_name: str
    class_name: str
    avg_score: float
    rank: int
