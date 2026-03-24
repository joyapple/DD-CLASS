from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import User, Class
from app.schemas import UserCreate, UserUpdate, UserResponse
from app.auth import get_current_active_user, get_password_hash

router = APIRouter(prefix="/api/users", tags=["用户管理"])

@router.get("", response_model=List[UserResponse])
def get_users(
    role: Optional[str] = None,
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="只有管理员可以查看用户列表")
    
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    if class_id:
        query = query.filter(User.class_id == class_id)
    
    users = query.all()
    return users

@router.post("", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="只有管理员可以创建用户")
    
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    if user_data.class_id:
        class_obj = db.query(Class).filter(Class.id == user_data.class_id).first()
        if not class_obj:
            raise HTTPException(status_code=400, detail="班级不存在")
    
    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        hashed_password=hashed_password,
        real_name=user_data.real_name,
        role=user_data.role,
        class_id=user_data.class_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="无权查看该用户")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="无权修改该用户")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if current_user.role != "admin":
        if user_data.role or user_data.class_id is not None:
            raise HTTPException(status_code=403, detail="无权修改权限或班级")
    
    if user_data.username is not None:
        existing = db.query(User).filter(
            User.username == user_data.username,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="用户名已存在")
        user.username = user_data.username
    
    if user_data.real_name is not None:
        user.real_name = user_data.real_name
    
    if user_data.role is not None and current_user.role == "admin":
        user.role = user_data.role
    
    if user_data.class_id is not None and current_user.role == "admin":
        if user_data.class_id:
            class_obj = db.query(Class).filter(Class.id == user_data.class_id).first()
            if not class_obj:
                raise HTTPException(status_code=400, detail="班级不存在")
        user.class_id = user_data.class_id
    
    if user_data.is_active is not None and current_user.role == "admin":
        user.is_active = user_data.is_active
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="只有管理员可以删除用户")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己的账号")
    
    db.delete(user)
    db.commit()
    return {"message": "用户删除成功"}
