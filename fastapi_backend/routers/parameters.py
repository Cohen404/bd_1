from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from database import get_db
import models as db_models
import schemas
# from auth import check_admin_permission  # 认证已移除

router = APIRouter()

@router.post("/", response_model=schemas.Parameter)
async def create_parameter(
    parameter: schemas.ParameterCreate,
    # current_user = Depends(check_admin_permission),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    创建系统参数
    """
    # 检查参数名是否已存在
    db_param = db.query(db_models.Parameters).filter(
        db_models.Parameters.param_name == parameter.param_name,
        db_models.Parameters.param_type == parameter.param_type
    ).first()
    
    if db_param:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"参数名'{parameter.param_name}'在类型'{parameter.param_type}'中已存在"
        )
    
    # 创建新参数
    db_param = db_models.Parameters(
        param_name=parameter.param_name,
        param_value=parameter.param_value,
        param_type=parameter.param_type,
        description=parameter.description,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    db.add(db_param)
    db.commit()
    db.refresh(db_param)
    
    logging.info(f"创建了参数: {parameter.param_name}")
    
    return db_param

@router.get("/", response_model=List[schemas.Parameter])
async def read_parameters(
    skip: int = 0,
    limit: int = 100,
    param_type: Optional[str] = None,
    # current_user = Depends(check_admin_permission),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    获取参数列表
    """
    query = db.query(db_models.Parameters)
    
    # 根据参数类型过滤
    if param_type:
        query = query.filter(db_models.Parameters.param_type == param_type)
    
    # 分页并获取结果
    parameters = query.order_by(db_models.Parameters.param_type, db_models.Parameters.param_name).offset(skip).limit(limit).all()
    
    return parameters

@router.get("/{param_id}", response_model=schemas.Parameter)
async def read_parameter(
    param_id: int,
    # current_user = Depends(check_admin_permission),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    获取特定参数
    """
    db_param = db.query(db_models.Parameters).filter(db_models.Parameters.id == param_id).first()
    if db_param is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="参数不存在"
        )
    
    return db_param

@router.put("/{param_id}", response_model=schemas.Parameter)
async def update_parameter(
    param_id: int,
    parameter: schemas.ParameterUpdate,
    # current_user = Depends(check_admin_permission),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    更新参数
    """
    db_param = db.query(db_models.Parameters).filter(db_models.Parameters.id == param_id).first()
    if db_param is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="参数不存在"
        )
    
    # 如果要更新参数名或类型，检查是否已存在
    if (parameter.param_name is not None and parameter.param_name != db_param.param_name) or \
       (parameter.param_type is not None and parameter.param_type != db_param.param_type):
        param_name = parameter.param_name if parameter.param_name is not None else db_param.param_name
        param_type = parameter.param_type if parameter.param_type is not None else db_param.param_type
        
        existing_param = db.query(db_models.Parameters).filter(
            db_models.Parameters.param_name == param_name,
            db_models.Parameters.param_type == param_type,
            db_models.Parameters.id != param_id
        ).first()
        
        if existing_param:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"参数名'{param_name}'在类型'{param_type}'中已存在"
            )
    
    # 更新参数
    if parameter.param_name is not None:
        db_param.param_name = parameter.param_name
    
    if parameter.param_value is not None:
        db_param.param_value = parameter.param_value
    
    if parameter.param_type is not None:
        db_param.param_type = parameter.param_type
    
    if parameter.description is not None:
        db_param.description = parameter.description
    
    db_param.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_param)
    
    logging.info(f"更新了参数ID: {param_id}")
    
    return db_param

@router.delete("/{param_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_parameter(
    param_id: int,
    # current_user = Depends(check_admin_permission),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    删除参数
    """
    db_param = db.query(db_models.Parameters).filter(db_models.Parameters.id == param_id).first()
    if db_param is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="参数不存在"
        )
    
    # 删除参数
    db.delete(db_param)
    db.commit()
    
    logging.info(f"删除了参数ID: {param_id}")
    
    return None 