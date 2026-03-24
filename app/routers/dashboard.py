from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User, Student, Class, Score, Attendance, Subject
from app.schemas import DashboardStats, ScoreResponse, ClassRanking, StudentRanking
from app.auth import get_current_active_user
from app.routers.classes import get_accessible_class_ids

router = APIRouter(prefix="/api/dashboard", tags=["仪表盘"])

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    semester: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    class_ids = get_accessible_class_ids(current_user, db)
    
    total_students = db.query(Student).filter(Student.class_id.in_(class_ids)).count()
    total_classes = len(class_ids)
    
    score_query = db.query(Score).filter(Score.class_id.in_(class_ids))
    if semester:
        score_query = score_query.filter(Score.semester == semester)
    
    total_scores = score_query.count()
    avg_score = 0
    if total_scores > 0:
        avg_score = round(score_query.with_entities(func.avg(Score.score)).scalar(), 2)
    
    attendance_query = db.query(Attendance).filter(Attendance.class_id.in_(class_ids))
    total_attendance = attendance_query.count()
    present_attendance = attendance_query.filter(Attendance.status == "present").count()
    
    attendance_rate = 0
    if total_attendance > 0:
        attendance_rate = round(present_attendance / total_attendance * 100, 2)
    
    recent_scores = score_query.order_by(Score.created_at.desc()).limit(10).all()
    recent_score_list = []
    for s in recent_scores:
        student = db.query(Student).filter(Student.id == s.student_id).first()
        subject = db.query(Subject).filter(Subject.id == s.subject_id).first()
        recent_score_list.append(ScoreResponse(
            id=s.id,
            student_id=s.student_id,
            subject_id=s.subject_id,
            class_id=s.class_id,
            score=s.score,
            exam_type=s.exam_type,
            semester=s.semester,
            created_at=s.created_at,
            student_name=student.name if student else None,
            subject_name=subject.name if subject else None
        ))
    
    return DashboardStats(
        total_students=total_students,
        total_classes=total_classes,
        total_scores=total_scores,
        avg_score=avg_score,
        attendance_rate=attendance_rate,
        recent_scores=recent_score_list,
        class_rankings=[]
    )

@router.get("/rankings/classes", response_model=list[ClassRanking])
def get_class_rankings(
    semester: Optional[str] = None,
    exam_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    class_ids = get_accessible_class_ids(current_user, db)
    
    query = db.query(
        Score.class_id,
        func.avg(Score.score).label("avg_score")
    ).filter(Score.class_id.in_(class_ids))
    
    if semester:
        query = query.filter(Score.semester == semester)
    if exam_type:
        query = query.filter(Score.exam_type == exam_type)
    
    results = query.group_by(Score.class_id).order_by(func.avg(Score.score).desc()).all()
    
    rankings = []
    for rank, (class_id, avg_score) in enumerate(results, 1):
        class_obj = db.query(Class).filter(Class.id == class_id).first()
        rankings.append(ClassRanking(
            class_id=class_id,
            class_name=class_obj.name if class_obj else "",
            avg_score=round(avg_score, 2) if avg_score else 0,
            rank=rank
        ))
    
    return rankings

@router.get("/rankings/students", response_model=list[StudentRanking])
def get_student_rankings(
    class_id: Optional[int] = None,
    semester: Optional[str] = None,
    exam_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    class_ids = get_accessible_class_ids(current_user, db)
    
    query = db.query(
        Score.student_id,
        func.avg(Score.score).label("avg_score")
    ).filter(Score.class_id.in_(class_ids))
    
    if class_id:
        if class_id not in class_ids:
            raise HTTPException(status_code=403, detail="无权访问该班级")
        query = query.filter(Score.class_id == class_id)
    
    if semester:
        query = query.filter(Score.semester == semester)
    if exam_type:
        query = query.filter(Score.exam_type == exam_type)
    
    results = query.group_by(Score.student_id).order_by(func.avg(Score.score).desc()).limit(limit).all()
    
    rankings = []
    for rank, (student_id, avg_score) in enumerate(results, 1):
        student = db.query(Student).filter(Student.id == student_id).first()
        class_obj = db.query(Class).filter(Class.id == student.class_id).first() if student else None
        rankings.append(StudentRanking(
            student_id=student_id,
            student_name=student.name if student else "",
            class_name=class_obj.name if class_obj else "",
            avg_score=round(avg_score, 2) if avg_score else 0,
            rank=rank
        ))
    
    return rankings

@router.get("/rankings/subjects/{subject_id}")
def get_subject_rankings(
    subject_id: int,
    class_id: Optional[int] = None,
    semester: Optional[str] = None,
    exam_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    class_ids = get_accessible_class_ids(current_user, db)
    
    query = db.query(Score).filter(
        Score.subject_id == subject_id,
        Score.class_id.in_(class_ids)
    )
    
    if class_id:
        if class_id not in class_ids:
            raise HTTPException(status_code=403, detail="无权访问该班级")
        query = query.filter(Score.class_id == class_id)
    
    if semester:
        query = query.filter(Score.semester == semester)
    if exam_type:
        query = query.filter(Score.exam_type == exam_type)
    
    scores = query.order_by(Score.score.desc()).limit(limit).all()
    
    results = []
    for rank, s in enumerate(scores, 1):
        student = db.query(Student).filter(Student.id == s.student_id).first()
        subject = db.query(Subject).filter(Subject.id == s.subject_id).first()
        results.append({
            "rank": rank,
            "student_id": s.student_id,
            "student_name": student.name if student else "",
            "score": s.score,
            "subject_name": subject.name if subject else "",
            "exam_type": s.exam_type,
            "semester": s.semester
        })
    
    return results

@router.get("/analysis/trends")
def get_score_trends(
    semester: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    class_ids = get_accessible_class_ids(current_user, db)
    
    query = db.query(Score).filter(Score.class_id.in_(class_ids))
    if semester:
        query = query.filter(Score.semester == semester)
    
    scores = query.all()
    
    exam_types = {}
    for s in scores:
        if s.exam_type not in exam_types:
            exam_types[s.exam_type] = []
        exam_types[s.exam_type].append(s.score)
    
    trends = {}
    for exam_type, score_list in exam_types.items():
        trends[exam_type] = {
            "avg": round(sum(score_list) / len(score_list), 2),
            "max": max(score_list),
            "min": min(score_list),
            "count": len(score_list)
        }
    
    return trends

@router.get("/analysis/subjects")
def get_subject_analysis(
    semester: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    class_ids = get_accessible_class_ids(current_user, db)
    
    query = db.query(
        Score.subject_id,
        func.avg(Score.score).label("avg_score"),
        func.max(Score.score).label("max_score"),
        func.min(Score.score).label("min_score"),
        func.count(Score.id).label("count")
    ).filter(Score.class_id.in_(class_ids))
    
    if semester:
        query = query.filter(Score.semester == semester)
    
    results = query.group_by(Score.subject_id).all()
    
    analysis = []
    for subject_id, avg_score, max_score, min_score, count in results:
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        analysis.append({
            "subject_id": subject_id,
            "subject_name": subject.name if subject else "",
            "avg_score": round(avg_score, 2) if avg_score else 0,
            "max_score": max_score,
            "min_score": min_score,
            "count": count
        })
    
    return analysis
