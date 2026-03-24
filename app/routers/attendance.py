from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models import User, Attendance, Student, Class
from app.schemas import AttendanceCreate, AttendanceUpdate, AttendanceResponse
from app.auth import get_current_active_user
from app.routers.classes import get_accessible_class_ids

router = APIRouter(prefix="/api/attendance", tags=["考勤管理"])

@router.get("", response_model=List[AttendanceResponse])
def get_attendances(
    class_id: Optional[int] = None,
    student_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    class_ids = get_accessible_class_ids(current_user, db)
    
    query = db.query(Attendance).filter(Attendance.class_id.in_(class_ids))
    
    if class_id:
        if class_id not in class_ids:
            raise HTTPException(status_code=403, detail="无权访问该班级")
        query = query.filter(Attendance.class_id == class_id)
    if student_id:
        query = query.filter(Attendance.student_id == student_id)
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    if status:
        query = query.filter(Attendance.status == status)
    
    attendances = query.order_by(Attendance.date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    result = []
    for a in attendances:
        student = db.query(Student).filter(Student.id == a.student_id).first()
        result.append(AttendanceResponse(
            id=a.id,
            student_id=a.student_id,
            class_id=a.class_id,
            date=a.date,
            status=a.status,
            remark=a.remark,
            created_at=a.created_at,
            student_name=student.name if student else None
        ))
    
    return result

@router.post("", response_model=AttendanceResponse)
def create_attendance(
    attendance_data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    class_ids = get_accessible_class_ids(current_user, db)
    if attendance_data.class_id not in class_ids:
        raise HTTPException(status_code=403, detail="无权在该班级添加考勤")
    
    student = db.query(Student).filter(Student.id == attendance_data.student_id).first()
    if not student or student.class_id != attendance_data.class_id:
        raise HTTPException(status_code=400, detail="学生不存在或不在该班级")
    
    existing = db.query(Attendance).filter(
        Attendance.student_id == attendance_data.student_id,
        Attendance.date == attendance_data.date
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该日期已有考勤记录")
    
    attendance = Attendance(
        student_id=attendance_data.student_id,
        class_id=attendance_data.class_id,
        date=attendance_data.date,
        status=attendance_data.status,
        remark=attendance_data.remark
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    
    return AttendanceResponse(
        id=attendance.id,
        student_id=attendance.student_id,
        class_id=attendance.class_id,
        date=attendance.date,
        status=attendance.status,
        remark=attendance.remark,
        created_at=attendance.created_at,
        student_name=student.name
    )

@router.put("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(
    attendance_id: int,
    attendance_data: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="考勤记录不存在")
    
    class_ids = get_accessible_class_ids(current_user, db)
    if attendance.class_id not in class_ids:
        raise HTTPException(status_code=403, detail="无权修改该考勤记录")
    
    if attendance_data.status is not None:
        attendance.status = attendance_data.status
    if attendance_data.remark is not None:
        attendance.remark = attendance_data.remark
    
    db.commit()
    db.refresh(attendance)
    
    student = db.query(Student).filter(Student.id == attendance.student_id).first()
    
    return AttendanceResponse(
        id=attendance.id,
        student_id=attendance.student_id,
        class_id=attendance.class_id,
        date=attendance.date,
        status=attendance.status,
        remark=attendance.remark,
        created_at=attendance.created_at,
        student_name=student.name if student else None
    )

@router.delete("/{attendance_id}")
def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="考勤记录不存在")
    
    class_ids = get_accessible_class_ids(current_user, db)
    if attendance.class_id not in class_ids:
        raise HTTPException(status_code=403, detail="无权删除该考勤记录")
    
    db.delete(attendance)
    db.commit()
    return {"message": "考勤记录删除成功"}

@router.get("/statistics/class/{class_id}")
def get_class_attendance_stats(
    class_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    class_ids = get_accessible_class_ids(current_user, db)
    if class_id not in class_ids:
        raise HTTPException(status_code=403, detail="无权访问该班级")
    
    query = db.query(Attendance).filter(Attendance.class_id == class_id)
    
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    
    attendances = query.all()
    
    stats = {
        "total": len(attendances),
        "present": 0,
        "absent": 0,
        "late": 0,
        "leave": 0
    }
    
    for a in attendances:
        if a.status == "present":
            stats["present"] += 1
        elif a.status == "absent":
            stats["absent"] += 1
        elif a.status == "late":
            stats["late"] += 1
        elif a.status == "leave":
            stats["leave"] += 1
    
    if stats["total"] > 0:
        stats["attendance_rate"] = round(stats["present"] / stats["total"] * 100, 2)
    else:
        stats["attendance_rate"] = 0
    
    return stats

@router.get("/statistics/student/{student_id}")
def get_student_attendance_stats(
    student_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    class_ids = get_accessible_class_ids(current_user, db)
    if student.class_id not in class_ids:
        raise HTTPException(status_code=403, detail="无权访问该学生")
    
    query = db.query(Attendance).filter(Attendance.student_id == student_id)
    
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    
    attendances = query.all()
    
    stats = {
        "total": len(attendances),
        "present": 0,
        "absent": 0,
        "late": 0,
        "leave": 0
    }
    
    for a in attendances:
        if a.status == "present":
            stats["present"] += 1
        elif a.status == "absent":
            stats["absent"] += 1
        elif a.status == "late":
            stats["late"] += 1
        elif a.status == "leave":
            stats["leave"] += 1
    
    if stats["total"] > 0:
        stats["attendance_rate"] = round(stats["present"] / stats["total"] * 100, 2)
    else:
        stats["attendance_rate"] = 0
    
    return stats
