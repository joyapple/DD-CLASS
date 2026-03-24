from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Class, Student
from app.schemas import ClassCreate, ClassUpdate, ClassResponse
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/classes", tags=["班级管理"])

def get_accessible_class_ids(user: User, db: Session) -> List[int]:
    if user.role == "admin":
        classes = db.query(Class).all()
        return [c.id for c in classes]
    elif user.class_id:
        return [user.class_id]
    return []

@router.get("", response_model=List[ClassResponse])
def get_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    class_ids = get_accessible_class_ids(current_user, db)
    classes = db.query(Class).filter(Class.id.in_(class_ids)).all()
    
    result = []
    for c in classes:
        student_count = db.query(Student).filter(Student.class_id == c.id).count()
        class_data = ClassResponse(
            id=c.id,
            name=c.name,
            grade=c.grade,
            created_at=c.created_at,
            student_count=student_count
        )
        result.append(class_data)
    return result

@router.post("", response_model=ClassResponse)
def create_class(
    class_data: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="只有管理员可以创建班级")
    
    new_class = Class(name=class_data.name, grade=class_data.grade)
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return ClassResponse(id=new_class.id, name=new_class.name, grade=new_class.grade, 
                         created_at=new_class.created_at, student_count=0)

@router.get("/{class_id}", response_model=ClassResponse)
def get_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    class_ids = get_accessible_class_ids(current_user, db)
    if class_id not in class_ids:
        raise HTTPException(status_code=403, detail="无权访问该班级")
    
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    student_count = db.query(Student).filter(Student.class_id == class_id).count()
    return ClassResponse(id=class_obj.id, name=class_obj.name, grade=class_obj.grade,
                        created_at=class_obj.created_at, student_count=student_count)

@router.put("/{class_id}", response_model=ClassResponse)
def update_class(
    class_id: int,
    class_data: ClassUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="只有管理员可以修改班级")
    
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    if class_data.name is not None:
        class_obj.name = class_data.name
    if class_data.grade is not None:
        class_obj.grade = class_data.grade
    
    db.commit()
    db.refresh(class_obj)
    
    student_count = db.query(Student).filter(Student.class_id == class_id).count()
    return ClassResponse(id=class_obj.id, name=class_obj.name, grade=class_obj.grade,
                        created_at=class_obj.created_at, student_count=student_count)

@router.delete("/{class_id}")
def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="只有管理员可以删除班级")
    
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    db.delete(class_obj)
    db.commit()
    return {"message": "班级删除成功"}
