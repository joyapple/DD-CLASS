from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models import Homework, Class, Subject, User
from app.schemas import (
    HomeworkCreate, HomeworkUpdate, HomeworkResponse, HomeworkListResponse
)
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/homeworks", tags=["作业管理"])

def is_teacher(user: User) -> bool:
    return user.role.lower() in ["admin", "class_teacher", "teacher"] if user.role else False


def get_user_class_ids(user: User) -> List[int]:
    """获取用户可以访问的班级ID列表"""
    if user.role == 'admin':
        return []
    elif user.role in ['class_teacher', 'teacher']:
        if user.class_id:
            return [user.class_id]
        return []
    elif user.role == 'student':
        if user.class_id:
            return [user.class_id]
        return []
    return []


@router.get("", response_model=HomeworkListResponse)
def get_homeworks(
    class_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Homework)

    allowed_class_ids = get_user_class_ids(current_user)

    if current_user.role != 'admin':
        if allowed_class_ids:
            query = query.filter(Homework.class_id.in_(allowed_class_ids))
        else:
            return HomeworkListResponse(total=0, data=[])

    if class_id:
        if current_user.role != 'admin' and class_id not in allowed_class_ids:
            return HomeworkListResponse(total=0, data=[])
        query = query.filter(Homework.class_id == class_id)

    if subject_id:
        query = query.filter(Homework.subject_id == subject_id)

    total = query.count()
    homeworks = query.order_by(desc(Homework.created_at)).offset((page-1)*page_size).limit(page_size).all()

    result = []
    for h in homeworks:
        class_obj = db.query(Class).filter(Class.id == h.class_id).first()
        subject_obj = db.query(Subject).filter(Subject.id == h.subject_id).first() if h.subject_id else None
        creator = db.query(User).filter(User.id == h.created_by).first()

        result.append(HomeworkResponse(
            id=h.id,
            title=h.title,
            content=h.content,
            class_id=h.class_id,
            subject_id=h.subject_id,
            due_date=h.due_date,
            created_by=h.created_by,
            created_at=h.created_at,
            updated_at=h.updated_at,
            class_name=class_obj.name if class_obj else None,
            subject_name=subject_obj.name if subject_obj else None,
            creator_name=creator.real_name if creator else None
        ))

    return HomeworkListResponse(total=total, data=result)


@router.get("/{homework_id}", response_model=HomeworkResponse)
def get_homework(
    homework_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    h = db.query(Homework).filter(Homework.id == homework_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="作业不存在")

    allowed_class_ids = get_user_class_ids(current_user)
    if current_user.role != 'admin' and h.class_id not in allowed_class_ids:
        raise HTTPException(status_code=403, detail="无权访问该作业")

    class_obj = db.query(Class).filter(Class.id == h.class_id).first()
    subject_obj = db.query(Subject).filter(Subject.id == h.subject_id).first() if h.subject_id else None
    creator = db.query(User).filter(User.id == h.created_by).first()

    return HomeworkResponse(
        id=h.id,
        title=h.title,
        content=h.content,
        class_id=h.class_id,
        subject_id=h.subject_id,
        due_date=h.due_date,
        created_by=h.created_by,
        created_at=h.created_at,
        updated_at=h.updated_at,
        class_name=class_obj.name if class_obj else None,
        subject_name=subject_obj.name if subject_obj else None,
        creator_name=creator.real_name if creator else None
    )


@router.post("", response_model=HomeworkResponse)
def create_homework(
    data: HomeworkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not is_teacher(current_user):
        raise HTTPException(status_code=403, detail="只有教师可以布置作业")

    class_obj = db.query(Class).filter(Class.id == data.class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="班级不存在")

    homework = Homework(
        title=data.title,
        content=data.content,
        class_id=data.class_id,
        subject_id=data.subject_id,
        due_date=data.due_date,
        created_by=current_user.id
    )
    db.add(homework)
    db.commit()
    db.refresh(homework)

    subject_obj = db.query(Subject).filter(Subject.id == homework.subject_id).first() if homework.subject_id else None

    return HomeworkResponse(
        id=homework.id,
        title=homework.title,
        content=homework.content,
        class_id=homework.class_id,
        subject_id=homework.subject_id,
        due_date=homework.due_date,
        created_by=homework.created_by,
        created_at=homework.created_at,
        updated_at=homework.updated_at,
        class_name=class_obj.name,
        subject_name=subject_obj.name if subject_obj else None,
        creator_name=current_user.real_name
    )


@router.put("/{homework_id}", response_model=HomeworkResponse)
def update_homework(
    homework_id: int,
    data: HomeworkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not is_teacher(current_user):
        raise HTTPException(status_code=403, detail="只有教师可以修改作业")

    homework = db.query(Homework).filter(Homework.id == homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="作业不存在")

    if data.title is not None:
        homework.title = data.title
    if data.content is not None:
        homework.content = data.content
    if data.subject_id is not None:
        homework.subject_id = data.subject_id
    if data.due_date is not None:
        homework.due_date = data.due_date

    db.commit()
    db.refresh(homework)

    class_obj = db.query(Class).filter(Class.id == homework.class_id).first()
    subject_obj = db.query(Subject).filter(Subject.id == homework.subject_id).first() if homework.subject_id else None
    creator = db.query(User).filter(User.id == homework.created_by).first()

    return HomeworkResponse(
        id=homework.id,
        title=homework.title,
        content=homework.content,
        class_id=homework.class_id,
        subject_id=homework.subject_id,
        due_date=homework.due_date,
        created_by=homework.created_by,
        created_at=homework.created_at,
        updated_at=homework.updated_at,
        class_name=class_obj.name if class_obj else None,
        subject_name=subject_obj.name if subject_obj else None,
        creator_name=creator.real_name if creator else None
    )


@router.delete("/{homework_id}")
def delete_homework(
    homework_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not is_teacher(current_user):
        raise HTTPException(status_code=403, detail="只有教师可以删除作业")

    homework = db.query(Homework).filter(Homework.id == homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="作业不存在")

    db.delete(homework)
    db.commit()

    return {"message": "作业已删除"}
