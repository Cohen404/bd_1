from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
import os
import shutil
from datetime import datetime
import zipfile
import io
import json
import glob

from database import get_db
import models as db_models
import schemas
# from auth import check_admin_permission  # 认证已移除
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
    # current_user = Depends(check_admin_permission),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    上传模型文件
    """
    try:
        # 验证模型类型
        if model_type not in MODEL_TYPE_NAMES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的模型类型: {model_type}"
            )
        
        # 验证文件格式
        allowed_extensions = ['.keras', '.h5', '.pt', '.pkl']
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件格式: {file_ext}，仅支持 {', '.join(allowed_extensions)}"
            )
        
        # 创建模型类型目录
        model_type_dir = os.path.join(MODEL_DIR, str(model_type))
        os.makedirs(model_type_dir, exist_ok=True)
        
        # 检查是否已存在此类型的模型
        existing_model = db.query(db_models.Model).filter(db_models.Model.model_type == model_type).first()
        
        # 保留原始文件名（使用上传的文件名）
        model_filename = file.filename
        model_path = os.path.join(model_type_dir, model_filename)
        
        # 保存文件
        with open(model_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logging.info(f"模型文件已保存: {model_path}")
        
        # 如果存在旧模型，备份旧文件并更新记录
        if existing_model:
            # 备份旧模型
            if os.path.exists(existing_model.model_path) and existing_model.model_path != model_path:
                backup_filename = f"backup_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.path.basename(existing_model.model_path)}"
                backup_path = os.path.join(model_type_dir, backup_filename)
                try:
                    shutil.move(existing_model.model_path, backup_path)
                    logging.info(f"旧模型已备份到: {backup_path}")
                except Exception as e:
                    logging.warning(f"备份旧模型失败: {str(e)}")
                    import traceback
                    logging.warning(traceback.format_exc())
            
            # 更新模型记录
            existing_model.model_path = model_path
            existing_model.create_time = datetime.now()
            db.commit()
            db.refresh(existing_model)
            
            logging.info(f"更新了模型类型 {model_type} 的模型文件，新路径: {model_path}")
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
            
            logging.info(f"上传了新的模型类型 {model_type}，路径: {model_path}")
            return db_model
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"上传模型失败: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传模型失败: {str(e)}"
        )

@router.get("/", response_model=List[schemas.Model])
async def read_models(
    skip: int = 0,
    limit: int = 100,
    model_type: Optional[int] = None,
    # current_user = Depends(check_admin_permission),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    获取模型列表
    """
    query = db.query(db_models.Model)
    
    if model_type is not None:
        query = query.filter(db_models.Model.model_type == model_type)
    
    models = query.order_by(db_models.Model.create_time.desc()).offset(skip).limit(limit).all()
    return models

@router.get("/{model_id}", response_model=schemas.Model)
async def read_model(
    model_id: int,
    # current_user = Depends(check_admin_permission),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    获取特定模型
    """
    model = db.query(db_models.Model).filter(db_models.Model.id == model_id).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID为{model_id}的模型不存在"
        )
    
    return model

@router.delete("/{model_id}")
async def delete_model(
    model_id: int,
    # current_user = Depends(check_admin_permission),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    删除特定模型
    """
    model = db.query(db_models.Model).filter(db_models.Model.id == model_id).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID为{model_id}的模型不存在"
        )
    
    # 删除模型文件
    if os.path.exists(model.model_path):
        try:
            os.remove(model.model_path)
        except Exception as e:
            logging.warning(f"删除模型文件失败: {str(e)}")
    
    # 删除数据库记录
    db.delete(model)
    db.commit()
    
    return {"message": f"模型ID {model_id} 删除成功"}

@router.get("/export/{model_id}")
async def export_model(
    model_id: int,
    # current_user = Depends(check_admin_permission),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    导出模型文件
    """
    from fastapi.responses import FileResponse
    
    model = db.query(db_models.Model).filter(db_models.Model.id == model_id).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID为{model_id}的模型不存在"
        )
    
    if not os.path.exists(model.model_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型文件不存在"
        )
    
    # 生成导出文件名
    model_type_name = MODEL_TYPE_NAMES.get(model.model_type, f"类型{model.model_type}")
    export_filename = f"{model_type_name}_{model.create_time.strftime('%Y%m%d_%H%M%S')}.keras"
    
    return FileResponse(
        path=model.model_path,
        media_type="application/octet-stream",
        filename=export_filename
    )

@router.post("/export-all")
async def export_all_models(
    # current_user = Depends(check_admin_permission),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    导出所有模型文件为ZIP包
    """
    models = db.query(db_models.Model).all()
    
    if not models:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="没有找到任何模型"
        )
    
    # 创建ZIP文件
    output = io.BytesIO()
    
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for model in models:
            if os.path.exists(model.model_path):
                model_type_name = MODEL_TYPE_NAMES.get(model.model_type, f"类型{model.model_type}")
                zip_filename = f"{model_type_name}_{model.create_time.strftime('%Y%m%d_%H%M%S')}.keras"
                zipf.write(model.model_path, zip_filename)
    
    output.seek(0)
    filename = f"所有模型_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    from fastapi import Response
    return Response(
        content=output.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/status/check")
async def check_model_status(
    # current_user = Depends(check_admin_permission),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    检查所有模型的状态
    """
    models = db.query(db_models.Model).all()
    status_info = {
        "total_models": len(models),
        "available_models": 0,
        "missing_models": 0,
        "model_details": []
    }
    
    for model in models:
        model_type_name = MODEL_TYPE_NAMES.get(model.model_type, f"类型{model.model_type}")
        file_exists = os.path.exists(model.model_path)
        file_size = 0
        
        if file_exists:
            try:
                file_size = os.path.getsize(model.model_path)
                status_info["available_models"] += 1
            except Exception:
                file_exists = False
        
        if not file_exists:
            status_info["missing_models"] += 1
        
        model_detail = {
            "id": model.id,
            "model_type": model.model_type,
            "model_type_name": model_type_name,
            "model_path": model.model_path,
            "create_time": model.create_time.isoformat(),
            "file_exists": file_exists,
            "file_size_mb": round(file_size / (1024 * 1024), 2) if file_exists else 0,
            "status": "可用" if file_exists else "文件缺失"
        }
        
        status_info["model_details"].append(model_detail)
    
    return status_info

@router.get("/versions/{model_type}")
async def get_model_versions(
    model_type: int,
    # current_user = Depends(check_admin_permission),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    获取特定类型模型的版本历史（包括备份文件）
    """
    # 验证模型类型
    if model_type not in MODEL_TYPE_NAMES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的模型类型: {model_type}"
        )
    
    # 获取当前模型
    current_model = db.query(db_models.Model).filter(db_models.Model.model_type == model_type).first()
    
    # 查找备份文件
    model_type_dir = os.path.join(MODEL_DIR, str(model_type))
    versions = []
    
    if current_model:
        versions.append({
            "id": current_model.id,
            "version": "当前版本",
            "create_time": current_model.create_time.isoformat(),
            "file_path": current_model.model_path,
            "file_exists": os.path.exists(current_model.model_path),
            "file_size_mb": round(os.path.getsize(current_model.model_path) / (1024 * 1024), 2) if os.path.exists(current_model.model_path) else 0,
            "is_current": True
        })
    
    # 查找备份文件
    if os.path.exists(model_type_dir):
        backup_files = glob.glob(os.path.join(model_type_dir, "backup_*.keras"))
        
        for backup_file in sorted(backup_files, reverse=True):
            try:
                file_stat = os.stat(backup_file)
                versions.append({
                    "id": None,
                    "version": f"备份版本_{os.path.basename(backup_file)}",
                    "create_time": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    "file_path": backup_file,
                    "file_exists": True,
                    "file_size_mb": round(file_stat.st_size / (1024 * 1024), 2),
                    "is_current": False
                })
            except Exception as e:
                logging.warning(f"读取备份文件信息失败: {str(e)}")
    
    return {
        "model_type": model_type,
        "model_type_name": MODEL_TYPE_NAMES[model_type],
        "versions": versions
    }

@router.post("/restore/{model_type}")
async def restore_model_version(
    model_type: int,
    backup_filename: str = Form(...),
    # current_user = Depends(check_admin_permission),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    恢复模型的备份版本
    """
    # 验证模型类型
    if model_type not in MODEL_TYPE_NAMES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的模型类型: {model_type}"
        )
    
    # 构建备份文件路径
    model_type_dir = os.path.join(MODEL_DIR, str(model_type))
    backup_path = os.path.join(model_type_dir, backup_filename)
    
    if not os.path.exists(backup_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"备份文件不存在: {backup_filename}"
        )
    
    # 获取当前模型记录
    current_model = db.query(db_models.Model).filter(db_models.Model.model_type == model_type).first()
    
    if not current_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"模型类型 {model_type} 的记录不存在"
        )
    
    try:
        # 备份当前模型文件
        if os.path.exists(current_model.model_path):
            current_backup_name = f"backup_current_{datetime.now().strftime('%Y%m%d_%H%M%S')}.keras"
            current_backup_path = os.path.join(model_type_dir, current_backup_name)
            shutil.copy2(current_model.model_path, current_backup_path)
        
        # 恢复备份文件到当前位置
        shutil.copy2(backup_path, current_model.model_path)
        
        # 更新数据库记录
        current_model.create_time = datetime.now()
        db.commit()
        
        logging.info(f"用户 {current_user.username} 恢复了模型类型 {model_type} 的备份版本: {backup_filename}")
        
        return {
            "message": f"成功恢复模型类型 {model_type} 的备份版本",
            "restored_from": backup_filename,
            "current_backup_created": current_backup_name if os.path.exists(current_model.model_path) else None
        }
        
    except Exception as e:
        logging.error(f"恢复模型备份失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"恢复模型备份失败: {str(e)}"
        )

@router.get("/performance/info")
async def get_model_performance_info(
    # current_user = Depends(check_admin_permission),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    获取模型性能信息（模拟数据，实际应用中可以从模型训练记录中获取）
    """
    models = db.query(db_models.Model).all()
    performance_info = []
    
    for model in models:
        model_type_name = MODEL_TYPE_NAMES.get(model.model_type, f"类型{model.model_type}")
        
        # 模拟性能数据（实际应用中应该从训练记录或配置文件中读取）
        performance_data = {
            "id": model.id,
            "model_type": model.model_type,
            "model_type_name": model_type_name,
            "create_time": model.create_time.isoformat(),
            "file_exists": os.path.exists(model.model_path),
            "accuracy": {
                "training": round(0.85 + (model.id % 10) * 0.01, 3),  # 模拟数据
                "validation": round(0.80 + (model.id % 8) * 0.01, 3),  # 模拟数据
                "test": round(0.75 + (model.id % 6) * 0.015, 3)  # 模拟数据
            },
            "loss": {
                "training": round(0.25 - (model.id % 5) * 0.01, 4),  # 模拟数据
                "validation": round(0.30 - (model.id % 4) * 0.01, 4)  # 模拟数据
            },
            "training_epochs": 50 + (model.id % 20),  # 模拟数据
            "model_size_mb": round(os.path.getsize(model.model_path) / (1024 * 1024), 2) if os.path.exists(model.model_path) else 0
        }
        
        performance_info.append(performance_data)
    
    return {
        "model_count": len(models),
        "performance_data": performance_info
    } 