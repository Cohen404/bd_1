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
from auth import get_current_user, check_permission
from config import DATA_DIR

router = APIRouter()

@router.post("/", response_model=schemas.Data)
async def create_data(
    personnel_id: str = Form(...),
    personnel_name: str = Form(...),
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传数据文件
    """
    # 创建数据目录
    data_dir = os.path.join(DATA_DIR, personnel_id)
    os.makedirs(data_dir, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(data_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 创建数据记录
    db_data = db_models.Data(
        personnel_id=personnel_id,
        data_path=data_dir,
        upload_user=1 if current_user.user_type == "admin" else 0,
        personnel_name=personnel_name,
        user_id=current_user.user_id,
        upload_time=datetime.now()
    )
    
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    
    logging.info(f"用户{current_user.username}上传了数据: {personnel_id}")
    
    return db_data

@router.get("/", response_model=List[schemas.Data])
async def read_data(
    skip: int = 0,
    limit: int = 100,
    personnel_id: Optional[str] = None,
    personnel_name: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取数据列表
    """
    query = db.query(db_models.Data)
    
    # 普通用户只能查看自己上传的数据
    if current_user.user_type != "admin":
        query = query.filter(db_models.Data.user_id == current_user.user_id)
    
    # 根据参数过滤
    if personnel_id:
        query = query.filter(db_models.Data.personnel_id.ilike(f"%{personnel_id}%"))
    
    if personnel_name:
        query = query.filter(db_models.Data.personnel_name.ilike(f"%{personnel_name}%"))
    
    # 分页并获取结果
    data = query.order_by(db_models.Data.upload_time.desc()).offset(skip).limit(limit).all()
    
    return data

@router.get("/{data_id}", response_model=schemas.Data)
async def read_data_by_id(
    data_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取特定数据
    """
    db_data = db.query(db_models.Data).filter(db_models.Data.id == data_id).first()
    if db_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据不存在"
        )
    
    # 普通用户只能查看自己上传的数据
    if current_user.user_type != "admin" and db_data.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限查看此数据"
        )
    
    return db_data

@router.delete("/{data_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_data(
    data_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除数据
    """
    db_data = db.query(db_models.Data).filter(db_models.Data.id == data_id).first()
    if db_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据不存在"
        )
    
    # 普通用户只能删除自己上传的数据
    if current_user.user_type != "admin" and db_data.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除此数据"
        )
    
    # 删除相关的结果
    db.query(db_models.Result).filter(db_models.Result.data_id == data_id).delete()
    
    # 删除数据记录
    db.delete(db_data)
    db.commit()
    
    # 尝试删除数据目录，但不强制
    try:
        if os.path.exists(db_data.data_path):
            shutil.rmtree(db_data.data_path)
    except Exception as e:
        logging.warning(f"删除数据目录时出错: {str(e)}")
    
    logging.info(f"用户{current_user.username}删除了数据ID: {data_id}")
    
    return None 