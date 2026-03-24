from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Subject
from app.schemas import SubjectCreate, SubjectResponse
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/subjects", tags=["科目管理"])

@router.get("", response_model=List[SubjectResponse])
def get_subjects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    subjects = db.query(Subject).all()
    return subjects

@router.post("", response_model=SubjectResponse)
def create_subject(
    subject_data: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="只有管理员可以创建科目")
    
    existing = db.query(Subject).filter(Subject.name == subject_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="科目已存在")
    
    subject = Subject(name=subject_data.name)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject

@router.delete("/{subject_id}")
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="只有管理员可以删除科目")
    
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="科目不存在")
    
    db.delete(subject)
    db.commit()
    return {"message": "科目删除成功"}
