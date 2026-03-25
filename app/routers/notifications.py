from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timezone
from app.database import get_db
from app.models import Notification, NotificationRead, User, Class
from app.schemas import (
    NotificationCreate, NotificationUpdate, NotificationResponse, NotificationListResponse
)
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/notifications", tags=["通知管理"])

def is_admin(user: User) -> bool:
    return user.role == 'admin' if user.role else False

def is_admin_or_teacher(user: User) -> bool:
    return user.role.lower() in ["admin", "class_teacher", "teacher"] if user.role else False


@router.get("", response_model=NotificationListResponse)
def get_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Notification)

    if current_user.role != 'admin':
        if current_user.class_id:
            query = query.filter(
                (Notification.class_id == None) |
                (Notification.class_id == current_user.class_id)
            )
        else:
            query = query.filter(Notification.class_id == None)

    query = query.order_by(
        desc(Notification.is_pinned),
        desc(Notification.created_at)
    )

    total = query.count()

    notifications = query.offset((page-1)*page_size).limit(page_size).all()

    unread_count = db.query(NotificationRead).filter(
        NotificationRead.user_id == current_user.id,
        NotificationRead.is_read == False
    ).count()

    read_notification_ids = db.query(NotificationRead.notification_id).filter(
        NotificationRead.user_id == current_user.id,
        NotificationRead.is_read == True
    ).all()
    read_ids = [r[0] for r in read_notification_ids]

    result = []
    for n in notifications:
        creator = db.query(User).filter(User.id == n.created_by).first()
        class_obj = db.query(Class).filter(Class.id == n.class_id).first() if n.class_id else None

        result.append(NotificationResponse(
            id=n.id,
            title=n.title,
            content=n.content,
            priority=n.priority,
            is_pinned=n.is_pinned,
            class_id=n.class_id,
            created_by=n.created_by,
            created_at=n.created_at,
            updated_at=n.updated_at,
            creator_name=creator.real_name if creator else None,
            class_name=class_obj.name if class_obj else None,
            is_read=n.id in read_ids
        ))

    return NotificationListResponse(total=total, unread_count=unread_count, data=result)


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    n = db.query(Notification).filter(Notification.id == notification_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="通知不存在")

    if current_user.role != 'admin':
        if n.class_id and n.class_id != current_user.class_id:
            raise HTTPException(status_code=403, detail="无权访问该通知")

    creator = db.query(User).filter(User.id == n.created_by).first()
    class_obj = db.query(Class).filter(Class.id == n.class_id).first() if n.class_id else None

    read_record = db.query(NotificationRead).filter(
        NotificationRead.notification_id == notification_id,
        NotificationRead.user_id == current_user.id
    ).first()

    is_read = read_record.is_read if read_record else False

    return NotificationResponse(
        id=n.id,
        title=n.title,
        content=n.content,
        priority=n.priority,
        is_pinned=n.is_pinned,
        class_id=n.class_id,
        created_by=n.created_by,
        created_at=n.created_at,
        updated_at=n.updated_at,
        creator_name=creator.real_name if creator else None,
        class_name=class_obj.name if class_obj else None,
        is_read=is_read
    )


@router.post("", response_model=NotificationResponse)
def create_notification(
    data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not is_admin_or_teacher(current_user):
        raise HTTPException(status_code=403, detail="只有教师或管理员可以发布通知")

    if data.class_id:
        class_obj = db.query(Class).filter(Class.id == data.class_id).first()
        if not class_obj:
            raise HTTPException(status_code=404, detail="班级不存在")

        if not is_admin(current_user) and current_user.class_id != data.class_id:
            raise HTTPException(status_code=403, detail="只能发布本班级的通知")

    notification = Notification(
        title=data.title,
        content=data.content,
        priority=data.priority,
        is_pinned=data.is_pinned,
        class_id=data.class_id if data.class_id else None,
        created_by=current_user.id
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    class_obj = db.query(Class).filter(Class.id == notification.class_id).first() if notification.class_id else None

    return NotificationResponse(
        id=notification.id,
        title=notification.title,
        content=notification.content,
        priority=notification.priority,
        is_pinned=notification.is_pinned,
        class_id=notification.class_id,
        created_by=notification.created_by,
        created_at=notification.created_at,
        updated_at=notification.updated_at,
        creator_name=current_user.real_name,
        class_name=class_obj.name if class_obj else None,
        is_read=False
    )


@router.put("/{notification_id}", response_model=NotificationResponse)
def update_notification(
    notification_id: int,
    data: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not is_admin_or_teacher(current_user):
        raise HTTPException(status_code=403, detail="只有教师或管理员可以修改通知")

    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")

    if not is_admin(current_user) and notification.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="只能修改自己的通知")

    if data.title is not None:
        notification.title = data.title
    if data.content is not None:
        notification.content = data.content
    if data.priority is not None:
        notification.priority = data.priority
    if data.is_pinned is not None:
        notification.is_pinned = data.is_pinned
    if data.class_id is not None:
        if data.class_id == 0:
            notification.class_id = None
        else:
            notification.class_id = data.class_id

    db.commit()
    db.refresh(notification)

    creator = db.query(User).filter(User.id == notification.created_by).first()
    class_obj = db.query(Class).filter(Class.id == notification.class_id).first() if notification.class_id else None

    return NotificationResponse(
        id=notification.id,
        title=notification.title,
        content=notification.content,
        priority=notification.priority,
        is_pinned=notification.is_pinned,
        class_id=notification.class_id,
        created_by=notification.created_by,
        created_at=notification.created_at,
        updated_at=notification.updated_at,
        creator_name=creator.real_name if creator else None,
        class_name=class_obj.name if class_obj else None,
        is_read=False
    )


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not is_admin_or_teacher(current_user):
        raise HTTPException(status_code=403, detail="只有教师或管理员可以删除通知")

    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")

    if not is_admin(current_user) and notification.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="只能删除自己的通知")

    db.query(NotificationRead).filter(NotificationRead.notification_id == notification_id).delete()

    db.delete(notification)
    db.commit()

    return {"message": "通知已删除"}


@router.post("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")

    read_record = db.query(NotificationRead).filter(
        NotificationRead.notification_id == notification_id,
        NotificationRead.user_id == current_user.id
    ).first()

    if not read_record:
        read_record = NotificationRead(
            notification_id=notification_id,
            user_id=current_user.id,
            is_read=True,
            read_at=datetime.now(timezone.utc)
        )
        db.add(read_record)
    else:
        read_record.is_read = True
        read_record.read_at = datetime.now(timezone.utc)

    db.commit()

    return {"message": "已标记为已读"}


@router.post("/mark-all-read")
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    unread_records = db.query(NotificationRead).filter(
        NotificationRead.user_id == current_user.id,
        NotificationRead.is_read == False
    ).all()

    for record in unread_records:
        record.is_read = True
        record.read_at = datetime.now(timezone.utc)

    db.commit()

    return {"message": f"已标记 {len(unread_records)} 条通知为已读"}
