from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.database import get_db
from app.models import User, Score, Student, Subject, Class
from app.schemas import ScoreCreate, ScoreUpdate, ScoreResponse
from app.auth import get_current_active_user
from app.routers.classes import get_accessible_class_ids

router = APIRouter(prefix="/api/scores", tags=["成绩管理"])

@router.get("", response_model=List[ScoreResponse])
def get_scores(
    class_id: Optional[int] = None,
    student_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    semester: Optional[str] = None,
    exam_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    class_ids = get_accessible_class_ids(current_user, db)
    
    query = db.query(Score).filter(Score.class_id.in_(class_ids))
    
    if class_id:
        if class_id not in class_ids:
            raise HTTPException(status_code=403, detail="无权访问该班级")
        query = query.filter(Score.class_id == class_id)
    if student_id:
        query = query.filter(Score.student_id == student_id)
    if subject_id:
        query = query.filter(Score.subject_id == subject_id)
    if semester:
        query = query.filter(Score.semester == semester)
    if exam_type:
        query = query.filter(Score.exam_type == exam_type)
    
    scores = query.order_by(Score.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    result = []
    for s in scores:
        student = db.query(Student).filter(Student.id == s.student_id).first()
        subject = db.query(Subject).filter(Subject.id == s.subject_id).first()
        result.append(ScoreResponse(
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
    
    return result

@router.post("", response_model=ScoreResponse)
def create_score(
    score_data: ScoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    class_ids = get_accessible_class_ids(current_user, db)
    if score_data.class_id not in class_ids:
        raise HTTPException(status_code=403, detail="无权在该班级添加成绩")
    
    student = db.query(Student).filter(Student.id == score_data.student_id).first()
    if not student or student.class_id != score_data.class_id:
        raise HTTPException(status_code=400, detail="学生不存在或不在该班级")
    
    subject = db.query(Subject).filter(Subject.id == score_data.subject_id).first()
    if not subject:
        raise HTTPException(status_code=400, detail="科目不存在")
    
    score = Score(
        student_id=score_data.student_id,
        subject_id=score_data.subject_id,
        class_id=score_data.class_id,
        score=score_data.score,
        exam_type=score_data.exam_type,
        semester=score_data.semester
    )
    db.add(score)
    db.commit()
    db.refresh(score)
    
    return ScoreResponse(
        id=score.id,
        student_id=score.student_id,
        subject_id=score.subject_id,
        class_id=score.class_id,
        score=score.score,
        exam_type=score.exam_type,
        semester=score.semester,
        created_at=score.created_at,
        student_name=student.name,
        subject_name=subject.name
    )

@router.put("/{score_id}", response_model=ScoreResponse)
def update_score(
    score_id: int,
    score_data: ScoreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    score = db.query(Score).filter(Score.id == score_id).first()
    if not score:
        raise HTTPException(status_code=404, detail="成绩不存在")
    
    class_ids = get_accessible_class_ids(current_user, db)
    if score.class_id not in class_ids:
        raise HTTPException(status_code=403, detail="无权修改该成绩")
    
    if score_data.score is not None:
        score.score = score_data.score
    if score_data.exam_type is not None:
        score.exam_type = score_data.exam_type
    if score_data.semester is not None:
        score.semester = score_data.semester
    
    db.commit()
    db.refresh(score)
    
    student = db.query(Student).filter(Student.id == score.student_id).first()
    subject = db.query(Subject).filter(Subject.id == score.subject_id).first()
    
    return ScoreResponse(
        id=score.id,
        student_id=score.student_id,
        subject_id=score.subject_id,
        class_id=score.class_id,
        score=score.score,
        exam_type=score.exam_type,
        semester=score.semester,
        created_at=score.created_at,
        student_name=student.name if student else None,
        subject_name=subject.name if subject else None
    )

@router.delete("/{score_id}")
def delete_score(
    score_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    score = db.query(Score).filter(Score.id == score_id).first()
    if not score:
        raise HTTPException(status_code=404, detail="成绩不存在")
    
    class_ids = get_accessible_class_ids(current_user, db)
    if score.class_id not in class_ids:
        raise HTTPException(status_code=403, detail="无权删除该成绩")
    
    db.delete(score)
    db.commit()
    return {"message": "成绩删除成功"}

@router.get("/student/{student_id}")
def get_student_scores(
    student_id: int,
    semester: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    class_ids = get_accessible_class_ids(current_user, db)
    if student.class_id not in class_ids:
        raise HTTPException(status_code=403, detail="无权访问该学生成绩")
    
    query = db.query(Score).filter(Score.student_id == student_id)
    if semester:
        query = query.filter(Score.semester == semester)
    
    scores = query.all()
    
    result = []
    for s in scores:
        subject = db.query(Subject).filter(Subject.id == s.subject_id).first()
        result.append({
            "id": s.id,
            "subject_id": s.subject_id,
            "subject_name": subject.name if subject else None,
            "score": s.score,
            "exam_type": s.exam_type,
            "semester": s.semester
        })
    
    return result
