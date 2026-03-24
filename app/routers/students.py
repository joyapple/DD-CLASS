from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import User, Student, Class
from app.schemas import StudentCreate, StudentUpdate, StudentResponse
from app.auth import get_current_active_user
from app.routers.classes import get_accessible_class_ids

router = APIRouter(prefix="/api/students", tags=["学生管理"])

@router.get("", response_model=List[StudentResponse])
def get_students(
    class_id: Optional[int] = None,
    name: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    class_ids = get_accessible_class_ids(current_user, db)
    
    query = db.query(Student).filter(Student.class_id.in_(class_ids))
    
    if class_id:
        if class_id not in class_ids:
            raise HTTPException(status_code=403, detail="无权访问该班级")
        query = query.filter(Student.class_id == class_id)
    
    if name:
        query = query.filter(Student.name.contains(name))
    
    total = query.count()
    students = query.offset((page - 1) * page_size).limit(page_size).all()
    
    result = []
    for s in students:
        class_obj = db.query(Class).filter(Class.id == s.class_id).first()
        result.append(StudentResponse(
            id=s.id,
            name=s.name,
            student_no=s.student_no,
            gender=s.gender,
            phone=s.phone,
            parent_phone=s.parent_phone,
            address=s.address,
            class_id=s.class_id,
            teacher_id=s.teacher_id,
            created_at=s.created_at,
            class_name=class_obj.name if class_obj else None
        ))
    
    return result

@router.post("", response_model=StudentResponse)
def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    class_ids = get_accessible_class_ids(current_user, db)
    if student_data.class_id not in class_ids:
        raise HTTPException(status_code=403, detail="无权在该班级添加学生")
    
    existing = db.query(Student).filter(Student.student_no == student_data.student_no).first()
    if existing:
        raise HTTPException(status_code=400, detail="学号已存在")
    
    student = Student(
        name=student_data.name,
        student_no=student_data.student_no,
        gender=student_data.gender,
        phone=student_data.phone,
        parent_phone=student_data.parent_phone,
        address=student_data.address,
        class_id=student_data.class_id,
        teacher_id=current_user.id if current_user.role == "teacher" else None
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    
    class_obj = db.query(Class).filter(Class.id == student.class_id).first()
    return StudentResponse(
        id=student.id,
        name=student.name,
        student_no=student.student_no,
        gender=student.gender,
        phone=student.phone,
        parent_phone=student.parent_phone,
        address=student.address,
        class_id=student.class_id,
        teacher_id=student.teacher_id,
        created_at=student.created_at,
        class_name=class_obj.name if class_obj else None
    )

@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    class_ids = get_accessible_class_ids(current_user, db)
    if student.class_id not in class_ids:
        raise HTTPException(status_code=403, detail="无权访问该学生")
    
    class_obj = db.query(Class).filter(Class.id == student.class_id).first()
    return StudentResponse(
        id=student.id,
        name=student.name,
        student_no=student.student_no,
        gender=student.gender,
        phone=student.phone,
        parent_phone=student.parent_phone,
        address=student.address,
        class_id=student.class_id,
        teacher_id=student.teacher_id,
        created_at=student.created_at,
        class_name=class_obj.name if class_obj else None
    )

@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    class_ids = get_accessible_class_ids(current_user, db)
    if student.class_id not in class_ids:
        raise HTTPException(status_code=403, detail="无权修改该学生")
    
    if student_data.name is not None:
        student.name = student_data.name
    if student_data.student_no is not None:
        existing = db.query(Student).filter(
            Student.student_no == student_data.student_no,
            Student.id != student_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="学号已存在")
        student.student_no = student_data.student_no
    if student_data.gender is not None:
        student.gender = student_data.gender
    if student_data.phone is not None:
        student.phone = student_data.phone
    if student_data.parent_phone is not None:
        student.parent_phone = student_data.parent_phone
    if student_data.address is not None:
        student.address = student_data.address
    if student_data.class_id is not None:
        if student_data.class_id not in class_ids:
            raise HTTPException(status_code=403, detail="无权移动到该班级")
        student.class_id = student_data.class_id
    
    db.commit()
    db.refresh(student)
    
    class_obj = db.query(Class).filter(Class.id == student.class_id).first()
    return StudentResponse(
        id=student.id,
        name=student.name,
        student_no=student.student_no,
        gender=student.gender,
        phone=student.phone,
        parent_phone=student.parent_phone,
        address=student.address,
        class_id=student.class_id,
        teacher_id=student.teacher_id,
        created_at=student.created_at,
        class_name=class_obj.name if class_obj else None
    )

@router.delete("/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    class_ids = get_accessible_class_ids(current_user, db)
    if student.class_id not in class_ids:
        raise HTTPException(status_code=403, detail="无权删除该学生")
    
    db.delete(student)
    db.commit()
    return {"message": "学生删除成功"}
