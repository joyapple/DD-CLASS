from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List
from app.database import get_db
from app.models import Score, Student, Subject, Class, User
from app.auth import get_current_active_user
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/analytics", tags=["成绩分析"])


@router.get("/student/{student_id}")
def get_student_analysis(
    student_id: int,
    semester: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取学生成绩分析"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return {"error": "学生不存在"}

    query = db.query(Score).filter(Score.student_id == student_id)
    if semester:
        query = query.filter(Score.semester == semester)

    scores = query.all()

    if not scores:
        return {
            "student": {
                "id": student.id,
                "name": student.name,
                "class_name": student.class_obj.name if student.class_obj else None
            },
            "summary": {
                "total_exams": 0,
                "average_score": 0,
                "max_score": 0,
                "min_score": 0
            },
            "subject_analysis": [],
            "trend": [],
            "weak_subjects": [],
            "rank_in_class": None,
            "rank_in_grade": None
        }

    valid_scores = [s for s in scores if s.score]
    total_exams = len([s for s in scores if s.score])
    average_score = sum(s.score for s in valid_scores) / len(valid_scores) if valid_scores else 0
    max_score = max([s.score for s in valid_scores]) if valid_scores else 0
    min_score = min([s.score for s in valid_scores]) if valid_scores else 0

    subject_analysis = db.query(
        Score.subject_id,
        Subject.name,
        func.avg(Score.score).label("avg_score"),
        func.count(Score.id).label("exam_count"),
        func.max(Score.score).label("max_score"),
        func.min(Score.score).label("min_score")
    ).join(
        Subject, Score.subject_id == Subject.id
    ).filter(
        Score.student_id == student_id
    )

    if semester:
        subject_analysis = subject_analysis.filter(Score.semester == semester)

    subject_stats = subject_analysis.group_by(
        Score.subject_id, Subject.name
    ).all()

    subject_analysis_list = []
    all_avg = average_score
    for stat in subject_stats:
        trend_query = db.query(Score).filter(
            Score.student_id == student_id,
            Score.subject_id == stat.subject_id
        ).order_by(Score.exam_date).all()

        trend = [{"date": str(s.exam_date) if s.exam_date else "", "score": s.score} for s in trend_query if s.score]

        subject_analysis_list.append({
            "subject_id": stat.subject_id,
            "subject_name": stat.name,
            "avg_score": round(stat.avg_score, 1) if stat.avg_score else 0,
            "exam_count": stat.exam_count,
            "max_score": stat.max_score,
            "min_score": stat.min_score,
            "trend": trend
        })

    all_scores = db.query(Score).filter(
        Score.class_id == student.class_id
    ).all()

    student_rank_in_class = 1
    for s in all_scores:
        if s.student_id == student_id and s.score:
            avg_s = sum(x.score for x in all_scores if x.student_id == student_id and x.score) / total_exams if total_exams > 0 else 0
            if s.score > avg_s:
                student_rank_in_class += 1

    class_students = db.query(Student).filter(Student.class_id == student.class_id).all()
    class_avg_scores = []
    for cs in class_students:
        cs_scores = db.query(Score).filter(Score.student_id == cs.id).all()
        if cs_scores:
            valid_cs_scores = [s for s in cs_scores if s.score]
            if valid_cs_scores:
                avg = sum(s.score for s in valid_cs_scores) / len(valid_cs_scores)
                class_avg_scores.append((cs.id, avg))

    class_avg_scores.sort(key=lambda x: x[1], reverse=True)
    rank_in_class = next((i + 1 for i, (sid, _) in enumerate(class_avg_scores) if sid == student_id), None)

    weak_subjects = []
    for sa in subject_analysis_list:
        if sa["avg_score"] < all_avg - 5:
            weak_subjects.append({
                "subject_id": sa["subject_id"],
                "subject_name": sa["subject_name"],
                "avg_score": sa["avg_score"],
                "gap": round(all_avg - sa["avg_score"], 1)
            })

    trend_query = db.query(Score).filter(
        Score.student_id == student_id,
        Score.score.isnot(None)
    ).order_by(Score.exam_date).all()

    trend = [
        {
            "date": str(s.exam_date) if s.exam_date else "",
            "exam_type": s.exam_type,
            "subject": s.subject.name if s.subject else "",
            "score": s.score
        }
        for s in trend_query
    ]

    return {
        "student": {
            "id": student.id,
            "name": student.name,
            "class_name": student.class_obj.name if student.class_obj else None,
            "class_id": student.class_id
        },
        "summary": {
            "total_exams": total_exams,
            "average_score": round(average_score, 1),
            "max_score": max_score,
            "min_score": min_score,
            "rank_in_class": rank_in_class,
            "class_student_count": len(class_avg_scores)
        },
        "subject_analysis": subject_analysis_list,
        "trend": trend,
        "weak_subjects": weak_subjects
    }


@router.get("/class/{class_id}")
def get_class_analysis(
    class_id: int,
    semester: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取班级成绩分析"""
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        return {"error": "班级不存在"}

    query = db.query(Score).filter(Score.class_id == class_id)
    if semester:
        query = query.filter(Score.semester == semester)

    scores = query.all()

    if not scores:
        return {
            "class": {
                "id": class_obj.id,
                "name": class_obj.name
            },
            "summary": {
                "total_exams": 0,
                "total_students": 0,
                "average_score": 0
            },
            "subject_analysis": [],
            "score_distribution": [],
            "top_students": [],
            "weak_students": []
        }

    valid_scores = [s for s in scores if s.score]
    total_exams = len(set((s.student_id, s.subject_id) for s in valid_scores))
    total_students = len(set(s.student_id for s in valid_scores))
    average_score = sum(s.score for s in valid_scores) / len(valid_scores) if valid_scores else 0

    score_distribution = {
        "excellent": len([s for s in valid_scores if s.score >= 90]),
        "good": len([s for s in valid_scores if 80 <= s.score < 90]),
        "average": len([s for s in valid_scores if 70 <= s.score < 80]),
        "pass": len([s for s in valid_scores if 60 <= s.score < 70]),
        "fail": len([s for s in valid_scores if s.score < 60])
    }

    subject_analysis = db.query(
        Score.subject_id,
        Subject.name,
        func.avg(Score.score).label("avg_score"),
        func.count(func.distinct(Score.student_id)).label("student_count")
    ).join(
        Subject, Score.subject_id == Subject.id
    ).filter(
        Score.class_id == class_id
    )

    if semester:
        subject_analysis = subject_analysis.filter(Score.semester == semester)

    subject_stats = subject_analysis.group_by(
        Score.subject_id, Subject.name
    ).all()

    subject_analysis_list = [
        {
            "subject_id": stat.subject_id,
            "subject_name": stat.name,
            "avg_score": round(stat.avg_score, 1) if stat.avg_score else 0,
            "student_count": stat.student_count
        }
        for stat in subject_stats
    ]

    student_avgs = db.query(
        Score.student_id,
        func.avg(Score.score).label("avg_score")
    ).filter(
        Score.class_id == class_id,
        Score.score.isnot(None)
    )

    if semester:
        student_avgs = student_avgs.filter(Score.semester == semester)

    student_stats = student_avgs.group_by(Score.student_id).all()

    student_list = []
    for stat in student_stats:
        student = db.query(Student).filter(Student.id == stat.student_id).first()
        if student:
            student_list.append({
                "student_id": stat.student_id,
                "student_name": student.name,
                "average_score": round(stat.avg_score, 1)
            })

    student_list.sort(key=lambda x: x["average_score"], reverse=True)

    top_students = student_list[:5]
    weak_students = student_list[-5:] if len(student_list) > 5 else student_list

    return {
        "class": {
            "id": class_obj.id,
            "name": class_obj.name
        },
        "summary": {
            "total_exams": total_exams,
            "total_students": total_students,
            "average_score": round(average_score, 1)
        },
        "subject_analysis": subject_analysis_list,
        "score_distribution": score_distribution,
        "top_students": top_students,
        "weak_students": weak_students
    }


@router.get("/comparison")
def compare_class(
    class_id: int,
    semester: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """对比班级成绩"""
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        return {"error": "班级不存在"}

    query = db.query(Score).filter(Score.class_id == class_id)
    if semester:
        query = query.filter(Score.semester == semester)

    scores = query.all()

    if not scores:
        return {
            "class_avg": 0,
            "grade_avg": 0,
            "comparison": 0
        }

    valid_scores = [s for s in scores if s.score]
    class_avg = sum(s.score for s in valid_scores) / len(valid_scores) if valid_scores else 0

    grade_scores = db.query(Score).filter(Score.score.isnot(None)).all()
    if semester:
        grade_scores = [s for s in grade_scores if s.semester == semester]

    grade_valid = [s for s in grade_scores if s.score]
    grade_avg = sum(s.score for s in grade_valid) / len(grade_valid) if grade_valid else 0

    comparison = class_avg - grade_avg

    return {
        "class_avg": round(class_avg, 1),
        "grade_avg": round(grade_avg, 1),
        "comparison": round(comparison, 1),
        "status": "above" if comparison > 0 else "below" if comparison < 0 else "equal"
    }
