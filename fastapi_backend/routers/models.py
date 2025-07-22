from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import os
import shutil
from datetime import datetime

from database import get_db
import models as db_models
import schemas
from auth import check_admin_permission
from config import MODEL_DIR

router = APIRouter()

MODEL_TYPE_NAMES = {
    0: "普通应激模型",
    1: "抑郁评估模型",
    2: "焦虑评估模型",
    3: "社交孤立评估模型"
}

@router.post("/", response_model=schemas.Model)
async def create_model(
    model_type: int = Form(...),
    file: UploadFile = File(...),
    current_user = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    """
    上传模型文件
    """
    # 验证模型类型
    if model_type not in MODEL_TYPE_NAMES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的模型类型: {model_type}"
        )
    
    # 创建模型类型目录
    model_type_dir = os.path.join(MODEL_DIR, str(model_type))
    os.makedirs(model_type_dir, exist_ok=True)
    
    # 检查是否已存在此类型的模型
    existing_model = db.query(db_models.Model).filter(db_models.Model.model_type == model_type).first()
    
    # 生成文件名
    model_filename = f"model_{model_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.keras"
    model_path = os.path.join(model_type_dir, model_filename)
    
    # 保存文件
    with open(model_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 创建standarder目录并创建空的std_{i}.pkl文件
    standarder_dir = os.path.join(model_type_dir, "standarder")
    os.makedirs(standarder_dir, exist_ok=True)
    
    # 如果已存在此类型的模型，则更新
    if existing_model:
        # 尝试删除旧模型文件，但不强制
        try:
            if os.path.exists(existing_model.model_path):
                os.remove(existing_model.model_path)
        except Exception as e:
            logging.warning(f"删除旧模型文件时出错: {str(e)}")
        
        # 更新模型记录
        existing_model.model_path = model_path
        existing_model.create_time = datetime.now()
        db.commit()
        db.refresh(existing_model)
        
        logging.info(f"管理员{current_user.username}更新了{MODEL_TYPE_NAMES[model_type]}")
        
        return existing_model
    else:
        # 创建新模型记录
        db_model = db_models.Model(
            model_type=model_type,
            model_path=model_path,
            create_time=datetime.now()
        )
        
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        
        logging.info(f"管理员{current_user.username}创建了{MODEL_TYPE_NAMES[model_type]}")
        
        return db_model

@router.get("/", response_model=List[schemas.Model])
async def read_models(
    current_user = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    """
    获取模型列表
    """
    models = db.query(db_models.Model).all()
    return models

@router.get("/{model_id}", response_model=schemas.Model)
async def read_model(
    model_id: int,
    current_user = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    """
    获取特定模型
    """
    db_model = db.query(db_models.Model).filter(db_models.Model.id == model_id).first()
    if db_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型不存在"
        )
    
    return db_model

@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: int,
    current_user = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    """
    删除模型
    """
    db_model = db.query(db_models.Model).filter(db_models.Model.id == model_id).first()
    if db_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型不存在"
        )
    
    # 尝试删除模型文件，但不强制
    try:
        if os.path.exists(db_model.model_path):
            os.remove(db_model.model_path)
    except Exception as e:
        logging.warning(f"删除模型文件时出错: {str(e)}")
    
    # 删除模型记录
    db.delete(db_model)
    db.commit()
    
    logging.info(f"管理员{current_user.username}删除了模型ID: {model_id}")
    
    return None 