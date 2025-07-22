from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import os
from datetime import datetime

from database import get_db
import models as db_models
import schemas
from auth import get_current_user, check_admin_permission
from model_inference import ResultProcessor

router = APIRouter()

@router.get("/", response_model=List[schemas.Result])
async def read_results(
    skip: int = 0,
    limit: int = 100,
    data_id: Optional[int] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取结果列表
    """
    query = db.query(db_models.Result)
    
    # 普通用户只能查看自己的结果
    if current_user.user_type != "admin":
        query = query.filter(db_models.Result.user_id == current_user.user_id)
    
    # 根据数据ID过滤
    if data_id:
        query = query.filter(db_models.Result.data_id == data_id)
    
    # 分页并获取结果
    results = query.order_by(db_models.Result.result_time.desc()).offset(skip).limit(limit).all()
    
    return results

@router.get("/{result_id}", response_model=schemas.Result)
async def read_result(
    result_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取特定结果
    """
    db_result = db.query(db_models.Result).filter(db_models.Result.id == result_id).first()
    if db_result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="结果不存在"
        )
    
    # 普通用户只能查看自己的结果
    if current_user.user_type != "admin" and db_result.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限查看此结果"
        )
    
    return db_result

@router.get("/{result_id}/report")
async def read_result_report(
    result_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取结果报告文件
    """
    db_result = db.query(db_models.Result).filter(db_models.Result.id == result_id).first()
    if db_result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="结果不存在"
        )
    
    # 普通用户只能查看自己的结果
    if current_user.user_type != "admin" and db_result.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限查看此结果"
        )
    
    # 检查报告是否存在
    if not db_result.report_path or not os.path.exists(db_result.report_path):
        # 生成报告
        result_processor = ResultProcessor(result_id, db)
        report_path = await result_processor.generate_report()
        
        if not report_path or not os.path.exists(report_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="报告不存在或生成失败"
            )
        
        # 更新报告路径
        db_result.report_path = report_path
        db.commit()
    
    # 读取报告内容
    with open(db_result.report_path, "r", encoding="utf-8") as f:
        report_content = f.read()
    
    # 返回文本内容
    return Response(content=report_content, media_type="text/plain")

@router.delete("/{result_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_result(
    result_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除结果
    """
    db_result = db.query(db_models.Result).filter(db_models.Result.id == result_id).first()
    if db_result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="结果不存在"
        )
    
    # 普通用户只能删除自己的结果
    if current_user.user_type != "admin" and db_result.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除此结果"
        )
    
    # 尝试删除报告文件，但不强制
    try:
        if db_result.report_path and os.path.exists(db_result.report_path):
            os.remove(db_result.report_path)
    except Exception as e:
        logging.warning(f"删除报告文件时出错: {str(e)}")
    
    # 删除结果记录
    db.delete(db_result)
    db.commit()
    
    logging.info(f"用户{current_user.username}删除了结果ID: {result_id}")
    
    return None 