from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    CLASS_TEACHER = "class_teacher"  # 班主任
    TEACHER = "teacher"  # 任课教师

class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"

class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    LEAVE = "leave"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    real_name = Column(String, nullable=False)
    role = Column(String, nullable=False, default="teacher")
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    class_obj = relationship("Class", back_populates="teachers")
    students = relationship("Student", back_populates="teacher")

class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    grade = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    teachers = relationship("User", back_populates="class_obj")
    students = relationship("Student", back_populates="class_obj")
    scores = relationship("Score", back_populates="class_obj")
    attendances = relationship("Attendance", back_populates="class_obj")

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    student_no = Column(String, index=True)
    gender = Column(SQLEnum(Gender))
    phone = Column(String, nullable=True)
    parent_phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('class_id', 'student_no', name='uq_student_class_no'),
    )

    class_obj = relationship("Class", back_populates="students")
    teacher = relationship("User", back_populates="students")
    scores = relationship("Score", back_populates="student")
    attendances = relationship("Attendance", back_populates="student")

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    scores = relationship("Score", back_populates="subject")

class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    score = Column(Float, nullable=False)
    exam_type = Column(String, default="midterm")
    exam_date = Column(DateTime(timezone=True), nullable=True)
    semester = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="scores")
    subject = relationship("Subject", back_populates="scores")
    class_obj = relationship("Class", back_populates="scores")

class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    status = Column(SQLEnum(AttendanceStatus), default=AttendanceStatus.PRESENT)
    remark = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="attendances")
    class_obj = relationship("Class", back_populates="attendances")

class Semester(Base):
    __tablename__ = "semesters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    year = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    username = Column(String, nullable=True)
    action = Column(String, nullable=False)
    target_type = Column(String, nullable=False)
    target_id = Column(Integer, nullable=True)
    target_name = Column(String, nullable=True)
    details = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    result = Column(String, default="success")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PointRule(Base):
    """积分规则配置"""
    __tablename__ = "point_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    category = Column(String, nullable=False)
    points = Column(Integer, nullable=False)
    condition_type = Column(String, nullable=False)
    condition_value = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class StudentPoint(Base):
    """学生积分账户"""
    __tablename__ = "student_points"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, unique=True)
    total_points = Column(Integer, default=0)
    available_points = Column(Integer, default=0)
    total_earned = Column(Integer, default=0)
    total_spent = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    student = relationship("Student", backref="point_account")

class PointRecord(Base):
    """积分变动记录"""
    __tablename__ = "point_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    rule_id = Column(Integer, ForeignKey("point_rules.id"), nullable=True)
    points = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)
    source_type = Column(String, nullable=False)
    source_id = Column(Integer, nullable=True)
    description = Column(String, nullable=True)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", backref="point_records")
    rule = relationship("PointRule", backref="records")
    operator = relationship("User", backref="point_operations")

class PointItem(Base):
    """积分商品"""
    __tablename__ = "point_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    item_type = Column(String, nullable=False)
    points_cost = Column(Integer, nullable=False)
    stock = Column(Integer, default=-1)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class PointExchange(Base):
    """积分兑换记录"""
    __tablename__ = "point_exchanges"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("point_items.id"), nullable=False)
    points_spent = Column(Integer, nullable=False)
    quantity = Column(Integer, default=1)
    status = Column(String, default="pending")
    exchange_time = Column(DateTime(timezone=True), server_default=func.now())
    pickup_time = Column(DateTime(timezone=True), nullable=True)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    remark = Column(String, nullable=True)

    student = relationship("Student", backref="exchanges")
    item = relationship("PointItem", backref="exchanges")
    operator = relationship("User", backref="exchange_operations")


class SystemSetting(Base):
    """系统设置"""
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String, unique=True, nullable=False, index=True)
    setting_value = Column(String, nullable=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Homework(Base):
    """作业"""
    __tablename__ = "homeworks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    class_obj = relationship("Class", backref="homeworks")
    subject = relationship("Subject", backref="homeworks")
    creator = relationship("User", backref="homeworks")


class Notification(Base):
    """通知"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=True)
    priority = Column(String, default="normal")
    is_pinned = Column(Boolean, default=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    creator = relationship("User", backref="notifications")
    class_obj = relationship("Class", backref="notifications")


class NotificationRead(Base):
    """通知阅读记录"""
    __tablename__ = "notification_reads"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)

    notification = relationship("Notification", backref="read_records")
    user = relationship("User", backref="notification_reads")
