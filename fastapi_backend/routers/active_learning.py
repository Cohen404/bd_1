"""
主动学习相关API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db
import models as db_models

router = APIRouter()

class ActiveLearningRequest(BaseModel):
    personnel_id: str

class ActiveLearningResponse(BaseModel):
    success: bool
    message: str
    updated_count: int

@router.post("/mark-as-learned", response_model=ActiveLearningResponse)
async def mark_personnel_as_learned(
    request: ActiveLearningRequest,
    db: Session = Depends(get_db)
):
    """
    标记人员为已主动学习
    
    该接口会将该人员的所有数据记录标记为已主动学习，
    同时更新相关的评估结果记录
    """
    try:
        # 查找该人员的所有数据记录
        data_list = db.query(db_models.Data).filter(
            db_models.Data.personnel_id == request.personnel_id
        ).all()
        
        if not data_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"未找到人员ID为 {request.personnel_id} 的数据"
            )
        
        # 更新所有数据记录的主动学习状态
        for data in data_list:
            data.active_learned = True
        
        # 更新所有相关结果记录的主动学习状态
        data_ids = [data.id for data in data_list]
        results = db.query(db_models.Result).filter(
            db_models.Result.data_id.in_(data_ids)
        ).all()
        
        for result in results:
            result.active_learned = True
        
        db.commit()
        
        return ActiveLearningResponse(
            success=True,
            message=f"成功标记人员 {data_list[0].personnel_name} 为已主动学习",
            updated_count=len(data_list)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"标记主动学习失败: {str(e)}"
        )

@router.get("/check-learned-status/{personnel_id}")
async def check_learned_status(
    personnel_id: str,
    db: Session = Depends(get_db)
):
    """
    检查人员是否已主动学习
    """
    try:
        # 查找该人员的数据记录
        data = db.query(db_models.Data).filter(
            db_models.Data.personnel_id == personnel_id
        ).first()
        
        if not data:
            return {
                "personnel_id": personnel_id,
                "learned": False,
                "exists": False
            }
        
        return {
            "personnel_id": personnel_id,
            "personnel_name": data.personnel_name,
            "learned": data.active_learned,
            "exists": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询主动学习状态失败: {str(e)}"
        )

@router.get("/all-learned-personnel")
async def get_all_learned_personnel(
    db: Session = Depends(get_db)
):
    """
    获取所有已主动学习的人员列表
    """
    try:
        # 查找所有已主动学习的数据记录
        learned_data = db.query(db_models.Data).filter(
            db_models.Data.active_learned == True
        ).all()
        
        # 按人员ID去重
        personnel_set = {}
        for data in learned_data:
            if data.personnel_id not in personnel_set:
                personnel_set[data.personnel_id] = {
                    "personnel_id": data.personnel_id,
                    "personnel_name": data.personnel_name,
                    "data_count": 0
                }
            personnel_set[data.personnel_id]["data_count"] += 1
        
        return {
            "count": len(personnel_set),
            "personnel": list(personnel_set.values())
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取已学习人员列表失败: {str(e)}"
        )
