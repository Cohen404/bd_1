from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from database import get_db
import models as db_models
import schemas
from auth import check_admin_permission

router = APIRouter()

@router.post("/", response_model=schemas.Role)
async def create_role(
    role: schemas.RoleCreate,
    current_user = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    """
    创建角色
    """
    # 检查角色名是否已存在
    db_role = db.query(db_models.Role).filter(db_models.Role.role_name == role.role_name).first()
    if db_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色名已存在"
        )
    
    # 创建新角色
    db_role = db_models.Role(
        role_name=role.role_name,
        description=role.description,
        created_at=datetime.now()
    )
    
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    
    logging.info(f"管理员{current_user.username}创建了角色: {role.role_name}")
    
    return db_role

@router.get("/", response_model=List[schemas.Role])
async def read_roles(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    """
    获取角色列表
    """
    roles = db.query(db_models.Role).offset(skip).limit(limit).all()
    return roles

@router.get("/{role_id}", response_model=schemas.Role)
async def read_role(
    role_id: int,
    current_user = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    """
    获取特定角色
    """
    db_role = db.query(db_models.Role).filter(db_models.Role.role_id == role_id).first()
    if db_role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    return db_role

@router.put("/{role_id}", response_model=schemas.Role)
async def update_role(
    role_id: int,
    role: schemas.RoleUpdate,
    current_user = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    """
    更新角色
    """
    db_role = db.query(db_models.Role).filter(db_models.Role.role_id == role_id).first()
    if db_role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 如果要更新角色名，检查是否已存在
    if role.role_name is not None and role.role_name != db_role.role_name:
        existing_role = db.query(db_models.Role).filter(
            db_models.Role.role_name == role.role_name,
            db_models.Role.role_id != role_id
        ).first()
        
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色名已存在"
            )
        
        db_role.role_name = role.role_name
    
    if role.description is not None:
        db_role.description = role.description
    
    db.commit()
    db.refresh(db_role)
    
    logging.info(f"管理员{current_user.username}更新了角色ID: {role_id}")
    
    return db_role

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    current_user = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    """
    删除角色
    """
    db_role = db.query(db_models.Role).filter(db_models.Role.role_id == role_id).first()
    if db_role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 删除相关的角色权限关联
    db.query(db_models.RolePermission).filter(db_models.RolePermission.role_id == role_id).delete()
    
    # 删除相关的用户角色关联
    db.query(db_models.UserRole).filter(db_models.UserRole.role_id == role_id).delete()
    
    # 删除角色
    db.delete(db_role)
    db.commit()
    
    logging.info(f"管理员{current_user.username}删除了角色ID: {role_id}")
    
    return None

@router.post("/{role_id}/permissions", response_model=schemas.RolePermission)
async def add_permission_to_role(
    role_id: int,
    permission: schemas.RolePermissionCreate,
    current_user = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    """
    为角色添加权限
    """
    # 检查角色是否存在
    db_role = db.query(db_models.Role).filter(db_models.Role.role_id == role_id).first()
    if db_role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 检查权限是否存在
    db_permission = db.query(db_models.Permission).filter(db_models.Permission.permission_id == permission.permission_id).first()
    if db_permission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存在"
        )
    
    # 检查关联是否已存在
    db_role_permission = db.query(db_models.RolePermission).filter(
        db_models.RolePermission.role_id == role_id,
        db_models.RolePermission.permission_id == permission.permission_id
    ).first()
    
    if db_role_permission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色已拥有此权限"
        )
    
    # 创建新的关联
    db_role_permission = db_models.RolePermission(
        role_id=role_id,
        permission_id=permission.permission_id
    )
    
    db.add(db_role_permission)
    db.commit()
    db.refresh(db_role_permission)
    
    logging.info(f"管理员{current_user.username}为角色ID {role_id} 添加了权限ID {permission.permission_id}")
    
    return db_role_permission

@router.delete("/{role_id}/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_permission_from_role(
    role_id: int,
    permission_id: int,
    current_user = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    """
    从角色中移除权限
    """
    # 检查关联是否存在
    db_role_permission = db.query(db_models.RolePermission).filter(
        db_models.RolePermission.role_id == role_id,
        db_models.RolePermission.permission_id == permission_id
    ).first()
    
    if db_role_permission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色没有此权限"
        )
    
    # 删除关联
    db.delete(db_role_permission)
    db.commit()
    
    logging.info(f"管理员{current_user.username}从角色ID {role_id} 移除了权限ID {permission_id}")
    
    return None 