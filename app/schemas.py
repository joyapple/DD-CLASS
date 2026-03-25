from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    CLASS_TEACHER = "class_teacher"
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
    role: str = "teacher"
    class_id: Optional[int] = None
    
    @field_validator('role', mode='before')
    @classmethod
    def convert_role(cls, v):
        if isinstance(v, UserRole):
            return v.value
        return v

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    real_name: Optional[str] = None
    role: Optional[str] = None
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

class TokenData(BaseModel):
    username: Optional[str] = None

class ClassCreate(BaseModel):
    name: str
    grade: int

class ClassUpdate(BaseModel):
    name: Optional[str] = None
    grade: Optional[int] = None

class ClassResponse(BaseModel):
    id: int
    name: str
    grade: int
    created_at: datetime
    student_count: int = 0

    class Config:
        from_attributes = True

class StudentBase(BaseModel):
    name: str
    student_no: str
    gender: Gender
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

class StudentListResponse(BaseModel):
    total: int
    data: List[StudentResponse]

class SubjectCreate(BaseModel):
    name: str
    teacher_id: Optional[int] = None

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    teacher_id: Optional[int] = None

class SubjectResponse(BaseModel):
    id: int
    name: str
    teacher_id: Optional[int] = None

    class Config:
        from_attributes = True

class SemesterCreate(BaseModel):
    name: str
    year: int
    is_current: bool = False

class SemesterUpdate(BaseModel):
    name: Optional[str] = None
    year: Optional[int] = None
    is_current: Optional[bool] = None

class SemesterResponse(BaseModel):
    id: int
    name: str
    year: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ScoreBase(BaseModel):
    student_id: int
    subject_id: int
    class_id: int
    semester: str
    exam_type: str
    score: float
    exam_date: Optional[str] = None

class ScoreCreate(ScoreBase):
    pass

class ScoreUpdate(BaseModel):
    score: Optional[float] = None
    exam_type: Optional[str] = None
    exam_date: Optional[str] = None

class ScoreResponse(ScoreBase):
    id: int
    student_name: Optional[str] = None
    subject_name: Optional[str] = None
    class_name: Optional[str] = None
    exam_date: Optional[datetime] = None

    class Config:
        from_attributes = True

class ScoreListResponse(BaseModel):
    total: int
    data: List[ScoreResponse]

class AttendanceBase(BaseModel):
    student_id: int
    class_id: int
    date: str
    status: AttendanceStatus
    remark: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    status: Optional[AttendanceStatus] = None
    remark: Optional[str] = None

class AttendanceResponse(AttendanceBase):
    id: int
    student_name: Optional[str] = None
    class_name: Optional[str] = None
    date: Optional[datetime] = None

    class Config:
        from_attributes = True

class AttendanceListResponse(BaseModel):
    total: int
    data: List[AttendanceResponse]

class ClassRanking(BaseModel):
    class_id: int
    class_name: str
    avg_score: float
    rank: int

class DashboardStats(BaseModel):
    total_students: int
    total_classes: int
    total_scores: int = 0
    avg_score: float
    attendance_rate: float = 0.0
    recent_scores: List[ScoreResponse] = []
    class_rankings: List[ClassRanking] = []

class StudentRanking(BaseModel):
    student_id: int
    student_name: str
    class_name: str
    avg_score: float
    rank: int

class OperationLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str
    target_type: str
    target_id: Optional[int] = None
    target_name: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    result: str
    created_at: datetime

    class Config:
        from_attributes = True

class OperationLogListResponse(BaseModel):
    total: int
    data: List[OperationLogResponse]

class PointRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    points: int
    condition_type: str
    condition_value: Optional[str] = None

class PointRuleCreate(PointRuleBase):
    pass

class PointRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    points: Optional[int] = None
    condition_type: Optional[str] = None
    condition_value: Optional[str] = None
    is_active: Optional[bool] = None

class PointRuleResponse(PointRuleBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class StudentPointResponse(BaseModel):
    id: int
    student_id: int
    total_points: int
    available_points: int
    total_earned: int
    total_spent: int
    student_name: Optional[str] = None
    class_name: Optional[str] = None

    class Config:
        from_attributes = True

class PointRecordResponse(BaseModel):
    id: int
    student_id: int
    rule_id: Optional[int] = None
    points: int
    balance_after: int
    source_type: str
    source_id: Optional[int] = None
    description: Optional[str] = None
    operator_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PointRecordListResponse(BaseModel):
    total: int
    data: List[PointRecordResponse]

class PointItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    item_type: str
    points_cost: int
    stock: int = -1
    image_url: Optional[str] = None

class PointItemCreate(PointItemBase):
    pass

class PointItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    item_type: Optional[str] = None
    points_cost: Optional[int] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

class PointItemResponse(PointItemBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class PointExchangeResponse(BaseModel):
    id: int
    student_id: int
    item_id: int
    points_spent: int
    quantity: int
    status: str
    exchange_time: datetime
    pickup_time: Optional[datetime] = None
    operator_name: Optional[str] = None
    remark: Optional[str] = None
    student_name: Optional[str] = None
    item_name: Optional[str] = None

    class Config:
        from_attributes = True

class PointExchangeListResponse(BaseModel):
    total: int
    data: List[PointExchangeResponse]

class PointAddRequest(BaseModel):
    student_id: int
    points: int
    description: str
    source_type: str = "manual"
    source_id: Optional[int] = None
    rule_id: Optional[int] = None

class PointExchangeRequest(BaseModel):
    item_id: int
    quantity: int = 1
    student_id: Optional[int] = None

class PointRankingResponse(BaseModel):
    student_id: int
    student_name: str
    class_name: str
    total_points: int
    rank: int

class PointStatsResponse(BaseModel):
    total_students: int
    active_students: int
    total_points_distributed: int
    total_points_exchanged: int
    top_students: List[PointRankingResponse]

class SystemSettingResponse(BaseModel):
    id: int
    setting_key: str
    setting_value: Optional[str]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SystemSettingUpdate(BaseModel):
    setting_value: str

class SystemSettingsResponse(BaseModel):
    system_name: str
    login_background: str
    system_logo: str
    system_intro: str
    copyright: str
    use_bing_background: bool


class HomeworkBase(BaseModel):
    title: str
    content: Optional[str] = None
    class_id: int
    subject_id: Optional[int] = None
    due_date: Optional[datetime] = None

class HomeworkCreate(HomeworkBase):
    pass

class HomeworkUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    subject_id: Optional[int] = None
    due_date: Optional[datetime] = None

class HomeworkResponse(HomeworkBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    class_name: Optional[str] = None
    subject_name: Optional[str] = None
    creator_name: Optional[str] = None

    class Config:
        from_attributes = True

class HomeworkListResponse(BaseModel):
    total: int
    data: List[HomeworkResponse]


class NotificationBase(BaseModel):
    title: str
    content: Optional[str] = None
    priority: str = "normal"
    is_pinned: bool = False
    class_id: Optional[int] = None

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    priority: Optional[str] = None
    is_pinned: Optional[bool] = None
    class_id: Optional[int] = None

class NotificationResponse(NotificationBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    creator_name: Optional[str] = None
    class_name: Optional[str] = None
    is_read: Optional[bool] = False

    class Config:
        from_attributes = True

class NotificationListResponse(BaseModel):
    total: int
    unread_count: int
    data: List[NotificationResponse]
