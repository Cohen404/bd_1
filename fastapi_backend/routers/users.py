from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging
import uuid
from datetime import datetime, timedelta
import os

from database import get_db
import models as db_models
import schemas
from auth import get_current_user, check_admin_permission, hash_password
from config import LOG_FILE

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.User)
async def create_user(
    user: schemas.UserCreate,
    # # current_user = Depends(check_admin_permission),  # 认证已移除  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    创建新用户
    """
    try:
        # 检查用户名是否已存在
        db_user = db.query(db_models.User).filter(db_models.User.username == user.username).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 生成用户ID
        user_id = str(uuid.uuid4())
        
        # 创建新用户
        db_user = db_models.User(
            user_id=user_id,
            username=user.username,
            password=hash_password(user.password),  # 使用安全的密码哈希
            email=user.email,
            phone=user.phone,
            user_type=user.user_type,
            created_at=datetime.now()
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"用户 {user.username} 创建成功")
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建用户失败: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建用户失败"
        )

@router.get("/", response_model=List[schemas.User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    # # current_user = Depends(check_admin_permission),  # 认证已移除  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    获取用户列表
    """
    users = db.query(db_models.User).offset(skip).limit(limit).all()
    return users

@router.get("/me", response_model=schemas.User)
async def read_user_me(current_user = Depends(get_current_user)):
    """
    获取当前用户信息
    """
    return current_user

@router.get("/stats", response_model=schemas.AdminStats)
async def get_admin_stats(
    # current_user = Depends(check_admin_permission),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    获取管理员统计数据
    """
    try:
        # 统计用户数量
        total_users = db.query(db_models.User).count()
        
        # 统计角色数量
        total_roles = db.query(db_models.Role).count()
        
        # 统计模型数量
        total_models = db.query(db_models.Model).count()
        
        # 统计日志数量（从日志文件）
        total_logs = 0
        recent_activities = 0
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = f.readlines()
                total_logs = len(logs)
                
                # 计算最近24小时的活动数量
                one_day_ago = datetime.now() - timedelta(days=1)
                for log in logs:
                    try:
                        log_time_str = log.split(" - ")[0]
                        log_time = datetime.strptime(log_time_str, "%Y-%m-%d %H:%M:%S,%f")
                        if log_time >= one_day_ago:
                            recent_activities += 1
                    except (ValueError, IndexError):
                        continue
        
        # 计算系统健康度（基于数据完整性）
        total_data = db.query(db_models.Data).count()
        total_results = db.query(db_models.Result).count()
        
        system_health = min(100,
            (20 if total_models > 0 else 0) +
            (20 if total_data > 0 else 0) +
            (20 if total_results > 0 else 0) +
            (20 if total_users > 0 else 0) +
            (20 if total_logs > 0 else 0)
        )
        
        admin_stats = schemas.AdminStats(
            totalUsers=total_users,
            totalRoles=total_roles,
            totalModels=total_models,
            totalLogs=total_logs,
            systemHealth=system_health,
            recentActivities=recent_activities
        )
        
        return admin_stats
    except Exception as e:
        logger.error(f"获取统计数据失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计数据失败: {str(e)}"
        )

@router.get("/{user_id}", response_model=schemas.User)
async def read_user(
    user_id: str,
    # current_user = Depends(get_current_user),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    获取特定用户信息
    """
    db_user = db.query(db_models.User).filter(db_models.User.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return db_user

@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: str,
    user: schemas.UserUpdate,
    # current_user = Depends(get_current_user),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    更新用户信息
    """
    db_user = db.query(db_models.User).filter(db_models.User.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新用户信息
    if user.username is not None:
        # 检查新用户名是否已存在
        existing_user = db.query(db_models.User).filter(
            db_models.User.username == user.username,
            db_models.User.user_id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        db_user.username = user.username
    
    if user.password is not None:
        db_user.password = hash_password(user.password)
    
    if user.email is not None:
        db_user.email = user.email
    
    if user.phone is not None:
        db_user.phone = user.phone
    
    if user.user_type is not None:
        db_user.user_type = user.user_type
    
    db_user.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    # # current_user = Depends(check_admin_permission),  # 认证已移除  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    删除用户
    """
    db_user = db.query(db_models.User).filter(db_models.User.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 删除相关的用户角色关联
    db.query(db_models.UserRole).filter(db_models.UserRole.user_id == user_id).delete()
    
    # 删除用户
    db.delete(db_user)
    db.commit()
    
    logging.info(f"删除了用户: {db_user.username}")
    
    return None