from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    TEACHER = "teacher"

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
    role = Column(SQLEnum(UserRole), default=UserRole.TEACHER)
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
    student_no = Column(String, unique=True, index=True)
    gender = Column(SQLEnum(Gender))
    phone = Column(String, nullable=True)
    parent_phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

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
