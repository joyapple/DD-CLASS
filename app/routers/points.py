from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from app.database import get_db
from app.models import User, Student, Class, PointRule, StudentPoint, PointRecord, PointItem, PointExchange
from app.schemas import (
    PointRuleResponse, PointRuleCreate, PointRuleUpdate,
    StudentPointResponse, PointRecordResponse, PointRecordListResponse,
    PointItemResponse, PointItemCreate, PointItemUpdate,
    PointExchangeResponse, PointExchangeListResponse,
    PointAddRequest, PointExchangeRequest,
    PointRankingResponse, PointStatsResponse
)
from app.auth import get_current_active_user
from app.routers.classes import get_accessible_class_ids
from datetime import datetime

router = APIRouter(prefix="/api/points", tags=["积分系统"])

def is_admin(user: User) -> bool:
    return user.role.lower() == "admin" if user.role else False

def is_class_teacher(user: User) -> bool:
    return user.role.lower() == "class_teacher" if user.role else False

def is_teacher(user: User) -> bool:
    return user.role.lower() in ["admin", "class_teacher", "teacher"] if user.role else False

@router.get("/stats", response_model=PointStatsResponse)
def get_point_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    class_ids = get_accessible_class_ids(current_user, db)
    student_ids = [s.id for s in db.query(Student).filter(Student.class_id.in_(class_ids)).all()]

    total_students = len(student_ids)
    active_students = db.query(StudentPoint).filter(
        StudentPoint.student_id.in_(student_ids),
        StudentPoint.total_points > 0
    ).count()

    total_distributed = db.query(func.coalesce(func.sum(StudentPoint.total_earned), 0)).filter(
        StudentPoint.student_id.in_(student_ids)
    ).scalar()

    total_exchanged = db.query(func.coalesce(func.sum(PointExchange.points_spent), 0)).filter(
        PointExchange.student_id.in_(student_ids)
    ).scalar()

    top_students_query = db.query(
        StudentPoint,
        Student.name,
        Student.class_id,
        Class.name.label("class_name")
    ).join(Student, StudentPoint.student_id == Student.id
    ).join(Class, Student.class_id == Class.id
    ).filter(
        StudentPoint.student_id.in_(student_ids)
    ).order_by(desc(StudentPoint.total_points)
    ).limit(10).all()

    top_students = []
    for i, (sp, name, class_id, class_name) in enumerate(top_students_query):
        top_students.append(PointRankingResponse(
            student_id=sp.student_id,
            student_name=name,
            class_name=class_name,
            total_points=sp.total_points,
            rank=i+1
        ))

    return PointStatsResponse(
        total_students=total_students,
        active_students=active_students,
        total_points_distributed=total_distributed or 0,
        total_points_exchanged=total_exchanged or 0,
        top_students=top_students
    )

@router.get("/ranking", response_model=List[PointRankingResponse])
def get_point_ranking(
    class_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    accessible_class_ids = get_accessible_class_ids(current_user, db)

    query = db.query(
        StudentPoint,
        Student.name,
        Class.name.label("class_name")
    ).join(Student, StudentPoint.student_id == Student.id
    ).join(Class, Student.class_id == Class.id
    ).filter(Student.class_id.in_(accessible_class_ids))

    if class_id:
        query = query.filter(Student.class_id == class_id)

    results = query.order_by(desc(StudentPoint.total_points)).limit(limit).all()

    ranking = []
    for i, (sp, name, class_name) in enumerate(results):
        ranking.append(PointRankingResponse(
            student_id=sp.student_id,
            student_name=name,
            class_name=class_name,
            total_points=sp.total_points,
            rank=i+1
        ))

    return ranking

@router.get("/my", response_model=StudentPointResponse)
def get_my_points(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if is_admin(current_user) or is_class_teacher(current_user):
        raise HTTPException(status_code=400, detail="教师账号没有个人积分")

    if not current_user.class_id:
        raise HTTPException(status_code=400, detail="未分配班级")

    student = db.query(Student).filter(Student.teacher_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="未找到对应的学生账号")

    sp = db.query(StudentPoint).filter(StudentPoint.student_id == student.id).first()
    if not sp:
        sp = StudentPoint(student_id=student.id, total_points=0, available_points=0)
        db.add(sp)
        db.commit()
        db.refresh(sp)

    return StudentPointResponse(
        id=sp.id,
        student_id=sp.student_id,
        total_points=sp.total_points,
        available_points=sp.available_points,
        total_earned=sp.total_earned,
        total_spent=sp.total_spent,
        student_name=student.name,
        class_name=student.class_obj.name if student.class_obj else None
    )

@router.get("/students/{student_id}", response_model=StudentPointResponse)
def get_student_points(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    accessible_class_ids = get_accessible_class_ids(current_user, db)
    if student.class_id not in accessible_class_ids:
        raise HTTPException(status_code=403, detail="无权查看该学生积分")

    sp = db.query(StudentPoint).filter(StudentPoint.student_id == student_id).first()
    if not sp:
        sp = StudentPoint(student_id=student_id, total_points=0, available_points=0)
        db.add(sp)
        db.commit()
        db.refresh(sp)

    return StudentPointResponse(
        id=sp.id,
        student_id=sp.student_id,
        total_points=sp.total_points,
        available_points=sp.available_points,
        total_earned=sp.total_earned,
        total_spent=sp.total_spent,
        student_name=student.name,
        class_name=student.class_obj.name if student.class_obj else None
    )

@router.post("/students/{student_id}/add")
def add_points(
    student_id: int,
    data: PointAddRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not is_teacher(current_user):
        raise HTTPException(status_code=403, detail="只有教师可以添加积分")

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    accessible_class_ids = get_accessible_class_ids(current_user, db)
    if student.class_id not in accessible_class_ids:
        raise HTTPException(status_code=403, detail="无权操作该学生")

    sp = db.query(StudentPoint).filter(StudentPoint.student_id == student_id).first()
    if not sp:
        sp = StudentPoint(student_id=student_id, total_points=0, available_points=0)
        db.add(sp)
        db.commit()
        db.refresh(sp)

    sp.total_points += data.points
    sp.available_points += data.points
    sp.total_earned += data.points

    record = PointRecord(
        student_id=student_id,
        points=data.points,
        balance_after=sp.total_points,
        source_type=data.source_type,
        source_id=data.source_id,
        description=data.description,
        operator_id=current_user.id,
        rule_id=data.rule_id
    )
    db.add(record)
    db.commit()

    return {"message": "积分添加成功", "current_points": sp.total_points}

@router.get("/rules", response_model=List[PointRuleResponse])
def get_rules(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(PointRule).filter(PointRule.is_active == True)
    if category:
        query = query.filter(PointRule.category == category)
    return query.order_by(PointRule.category, PointRule.points.desc()).all()

@router.post("/rules", response_model=PointRuleResponse)
def create_rule(
    data: PointRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="只有管理员可以创建规则")

    existing = db.query(PointRule).filter(PointRule.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="规则名称已存在")

    rule = PointRule(**data.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

@router.put("/rules/{rule_id}", response_model=PointRuleResponse)
def update_rule(
    rule_id: int,
    data: PointRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="只有管理员可以修改规则")

    rule = db.query(PointRule).filter(PointRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(rule, key, value)

    db.commit()
    db.refresh(rule)
    return rule

@router.get("/items", response_model=List[PointItemResponse])
def get_items(
    item_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(PointItem).filter(PointItem.is_active == True)
    if item_type:
        query = query.filter(PointItem.item_type == item_type)
    return query.order_by(PointItem.points_cost).all()

@router.post("/items", response_model=PointItemResponse)
def create_item(
    data: PointItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="只有管理员可以创建商品")

    item = PointItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.put("/items/{item_id}", response_model=PointItemResponse)
def update_item(
    item_id: int,
    data: PointItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="只有管理员可以修改商品")

    item = db.query(PointItem).filter(PointItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="商品不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item

@router.post("/exchange")
def exchange_item(
    data: PointExchangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    student_id = None
    
    if is_teacher(current_user):
        if not data.student_id:
            raise HTTPException(status_code=400, detail="教师帮学生兑换时需要提供student_id")
        student_id = data.student_id
        
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="学生不存在")
            
        accessible_class_ids = get_accessible_class_ids(current_user, db)
        if student.class_id not in accessible_class_ids:
            raise HTTPException(status_code=403, detail="无权为该学生兑换")
    else:
        student = db.query(Student).filter(Student.teacher_id == current_user.id).first()
        if not student:
            raise HTTPException(status_code=404, detail="未找到对应的学生账号")
        student_id = student.id

    item = db.query(PointItem).filter(PointItem.id == data.item_id, PointItem.is_active == True).first()
    if not item:
        raise HTTPException(status_code=404, detail="商品不存在或已下架")

    if item.stock != -1 and item.stock < data.quantity:
        raise HTTPException(status_code=400, detail="库存不足")

    sp = db.query(StudentPoint).filter(StudentPoint.student_id == student_id).first()
    if not sp:
        sp = StudentPoint(student_id=student_id, total_points=0, available_points=0, total_earned=0, total_spent=0)
        db.add(sp)
        db.commit()
        db.refresh(sp)

    total_cost = item.points_cost * data.quantity
    if sp.available_points < total_cost:
        raise HTTPException(status_code=400, detail=f"积分不足，需要{total_cost}积分，当前可用{sp.available_points}积分")

    sp.available_points -= total_cost
    sp.total_spent += total_cost

    if item.stock != -1:
        item.stock -= data.quantity

    exchange = PointExchange(
        student_id=student_id,
        item_id=data.item_id,
        points_spent=total_cost,
        quantity=data.quantity,
        status="pending",
        operator_id=current_user.id
    )
    db.add(exchange)

    record = PointRecord(
        student_id=student_id,
        points=-total_cost,
        balance_after=sp.available_points,
        source_type="exchange",
        source_id=exchange.id,
        description=f"兑换商品：{item.name}",
        operator_id=current_user.id
    )
    db.add(record)

    db.commit()

    return {"message": "兑换成功", "exchange_id": exchange.id}

@router.get("/exchanges", response_model=PointExchangeListResponse)
def get_exchanges(
    status: Optional[str] = None,
    student_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    accessible_class_ids = get_accessible_class_ids(current_user, db)
    accessible_student_ids = [s.id for s in db.query(Student).filter(Student.class_id.in_(accessible_class_ids)).all()]
    
    query = db.query(PointExchange).filter(PointExchange.student_id.in_(accessible_student_ids))
    if status:
        query = query.filter(PointExchange.status == status)
    if student_id and student_id in accessible_student_ids:
        query = query.filter(PointExchange.student_id == student_id)

    total = query.count()
    exchanges = query.order_by(desc(PointExchange.exchange_time)).offset((page-1)*page_size).limit(page_size).all()

    result = []
    for e in exchanges:
        student_obj = db.query(Student).filter(Student.id == e.student_id).first()
        item_obj = db.query(PointItem).filter(PointItem.id == e.item_id).first()
        operator = db.query(User).filter(User.id == e.operator_id).first() if e.operator_id else None

        result.append(PointExchangeResponse(
            id=e.id,
            student_id=e.student_id,
            item_id=e.item_id,
            points_spent=e.points_spent,
            quantity=e.quantity,
            status=e.status,
            exchange_time=e.exchange_time,
            pickup_time=e.pickup_time,
            operator_name=operator.real_name if operator else None,
            remark=e.remark,
            student_name=student_obj.name if student_obj else None,
            item_name=item_obj.name if item_obj else None
        ))

    return PointExchangeListResponse(total=total, data=result)

@router.put("/exchanges/{exchange_id}/complete")
def complete_exchange(
    exchange_id: int,
    remark: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not is_teacher(current_user):
        raise HTTPException(status_code=403, detail="只有教师可以确认兑换")

    exchange = db.query(PointExchange).filter(PointExchange.id == exchange_id).first()
    if not exchange:
        raise HTTPException(status_code=404, detail="兑换记录不存在")

    exchange.status = "completed"
    exchange.pickup_time = datetime.now()
    if remark:
        exchange.remark = remark
    exchange.operator_id = current_user.id

    db.commit()

    return {"message": "兑换完成确认成功"}

@router.get("/records/{student_id}", response_model=PointRecordListResponse)
def get_student_records(
    student_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    accessible_class_ids = get_accessible_class_ids(current_user, db)
    if student.class_id not in accessible_class_ids:
        raise HTTPException(status_code=403, detail="无权查看该学生积分记录")

    query = db.query(PointRecord).filter(PointRecord.student_id == student_id)
    total = query.count()
    records = query.order_by(desc(PointRecord.created_at)).offset((page-1)*page_size).limit(page_size).all()

    result = []
    for r in records:
        operator = db.query(User).filter(User.id == r.operator_id).first() if r.operator_id else None
        result.append(PointRecordResponse(
            id=r.id,
            student_id=r.student_id,
            rule_id=r.rule_id,
            points=r.points,
            balance_after=r.balance_after,
            source_type=r.source_type,
            source_id=r.source_id,
            description=r.description,
            operator_name=operator.real_name if operator else None,
            created_at=r.created_at
        ))

    return PointRecordListResponse(total=total, data=result)
