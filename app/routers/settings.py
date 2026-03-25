from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import SystemSetting, User
from app.schemas import SystemSettingResponse, SystemSettingUpdate, SystemSettingsResponse
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/settings", tags=["系统设置"])

def is_admin(user: User) -> bool:
    return user.role.lower() == "admin" if user.role else False


@router.get("/public", response_model=SystemSettingsResponse)
def get_public_settings(db: Session = Depends(get_db)):
    """获取公开的系统设置（不需要登录）"""
    settings = db.query(SystemSetting).all()
    settings_dict = {s.setting_key: s.setting_value for s in settings}
    
    return SystemSettingsResponse(
        system_name=settings_dict.get('system_name', 'DD-CLASS 班级管理系统'),
        login_background=settings_dict.get('login_background', ''),
        system_logo=settings_dict.get('system_logo', ''),
        system_intro=settings_dict.get('system_intro', '一个现代化的班级管理系统'),
        copyright=settings_dict.get('copyright', '© 2024 DD-CLASS'),
        use_bing_background=settings_dict.get('use_bing_background', 'true').lower() == 'true'
    )


@router.get("/all", response_model=List[SystemSettingResponse])
def get_all_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取所有系统设置（仅管理员）"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="只有管理员可以访问")
    
    return db.query(SystemSetting).order_by(SystemSetting.id).all()


@router.put("/{setting_key}")
def update_setting(
    setting_key: str,
    data: SystemSettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新系统设置（仅管理员）"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="只有管理员可以修改设置")
    
    setting = db.query(SystemSetting).filter(SystemSetting.setting_key == setting_key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="设置项不存在")
    
    setting.setting_value = data.setting_value
    db.commit()
    
    return {"message": "设置更新成功", "setting_key": setting_key, "value": data.setting_value}


@router.post("/batch-update")
def batch_update_settings(
    settings: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """批量更新系统设置（仅管理员）"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="只有管理员可以修改设置")
    
    updated = []
    for key, value in settings.items():
        setting = db.query(SystemSetting).filter(SystemSetting.setting_key == key).first()
        if setting:
            setting.setting_value = value
            updated.append(key)
    
    db.commit()
    
    return {"message": f"成功更新 {len(updated)} 个设置项", "updated": updated}
