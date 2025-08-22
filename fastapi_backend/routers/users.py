from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging
import uuid
from datetime import datetime

from database import get_db
import models as db_models
import schemas
from auth import get_current_user, check_admin_permission, hash_password

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
        
        logger.info(f"用户 {user.username} 创建成功，操作者：{current_user.username}")
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

@router.get("/{user_id}", response_model=schemas.User)
async def read_user(
    user_id: str,
    # current_user = Depends(get_current_user),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    获取特定用户信息
    """
    # 检查权限，普通用户只能查看自己的信息
    if current_user.user_type != "admin" and current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限查看其他用户的信息"
        )
    
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
    # 检查权限，普通用户只能更新自己的信息
    if current_user.user_type != "admin" and current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限更新其他用户的信息"
        )
    
    # 普通用户不能修改自己的用户类型
    if current_user.user_type != "admin" and user.user_type is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限修改用户类型"
        )
    
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
    
    if user.user_type is not None and current_user.user_type == "admin":
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
    
    # 管理员不能删除自己
    if db_user.user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除当前登录的管理员账户"
        )
    
    # 删除相关的用户角色关联
    db.query(db_models.UserRole).filter(db_models.UserRole.user_id == user_id).delete()
    
    # 删除用户
    db.delete(db_user)
    db.commit()
    
    logging.info(f"管理员{current_user.username}删除了用户: {db_user.username}")
    
    return None 