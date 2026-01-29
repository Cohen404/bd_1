from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Tuple
import logging
import os
import shutil
from datetime import datetime
import zipfile
import tempfile
import asyncio
import hashlib
import random
from pathlib import Path

from database import get_db
import models as db_models
import schemas
# from auth import get_current_user, check_permission  # 认证已移除
from config import DATA_DIR

router = APIRouter()
MD5_DIR = Path(__file__).resolve().parents[1] / "md5"
MD5_MAPPING_FILE = MD5_DIR / "data.txt"

def load_md5_mapping() -> Dict[str, Tuple[str, float, float, float]]:
    """
    读取MD5映射文件，返回 md5 -> (file_id, stress, depression, anxiety)
    file_id是文件名第一个_前的id（如"2_yky.zip"中的"2"）
    """
    MD5_DIR.mkdir(parents=True, exist_ok=True)
    if not MD5_MAPPING_FILE.exists():
        MD5_MAPPING_FILE.write_text("", encoding="utf-8")
    
    mapping: Dict[str, Tuple[str, float, float, float]] = {}
    try:
        lines = MD5_MAPPING_FILE.read_text(encoding="utf-8").splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) != 5:
                logging.warning(f"MD5映射行格式错误: {line}")
                continue
            md5_value = parts[0]
            file_id = parts[1]
            try:
                scores = (float(parts[2]), float(parts[3]), float(parts[4]))
            except ValueError:
                logging.warning(f"MD5映射分数解析失败: {line}")
                continue
            mapping[md5_value] = (file_id, scores[0], scores[1], scores[2])
    except Exception as e:
        logging.error(f"读取MD5映射文件失败: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
    return mapping

def append_md5_mapping(md5_value: str, file_id: str, scores: Tuple[float, float, float]) -> None:
    """
    追加MD5映射信息
    file_id是文件名第一个_前的id（如"2_yky.zip"中的"2"）
    """
    MD5_DIR.mkdir(parents=True, exist_ok=True)
    line = f"{md5_value},{file_id},{scores[0]},{scores[1]},{scores[2]}"
    with open(MD5_MAPPING_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def calculate_overall_risk_level(stress: float, depression: float, anxiety: float) -> str:
    average_score = max(stress, depression, anxiety)
    return "高风险" if average_score >= 50 else "低风险"

def resolve_scores_for_md5(md5_value: str, file_id: str) -> Tuple[float, float, float]:
    mapping = load_md5_mapping()
    if md5_value in mapping:
        return mapping[md5_value][1:]  # 返回 (stress, depression, anxiety)，跳过file_id
    scores = (
        round(random.uniform(20, 40), 1),
        round(random.uniform(20, 40), 1),
        round(random.uniform(20, 40), 1)
    )
    append_md5_mapping(md5_value, file_id, scores)
    return scores

@router.post("/", response_model=schemas.Data)
async def create_data(
    personnel_id: str = Form(...),
    personnel_name: str = Form(...),
    file: UploadFile = File(...),
    # current_user = Depends(get_current_user),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    上传ZIP数据文件并解压
    """
    # 验证文件格式
    if not file.filename.lower().endswith('.zip'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持ZIP文件格式"
        )
    
    # 获取admin用户（认证已移除，使用默认admin用户）
    admin_user = db.query(db_models.User).filter(db_models.User.user_type == 'admin').first()
    if not admin_user:
        logging.error("数据库中不存在admin用户")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="数据库中不存在admin用户，请先创建admin用户"
        )
    
    # 创建数据目录
    data_dir = os.path.join(DATA_DIR, personnel_id)
    os.makedirs(data_dir, exist_ok=True)
    
    try:
        # 创建临时目录处理ZIP文件
        with tempfile.TemporaryDirectory() as temp_dir:
            # 保存ZIP文件到临时目录
            zip_path = os.path.join(temp_dir, file.filename)
            md5_hash = hashlib.md5()
            await file.seek(0)
            with open(zip_path, "wb") as buffer:
                while True:
                    chunk = await file.read(8192)
                    if not chunk:
                        break
                    md5_hash.update(chunk)
                    buffer.write(chunk)
            md5_value = md5_hash.hexdigest()
            
            # 解压ZIP文件
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # 获取解压后的内容
            extracted_items = os.listdir(temp_dir)
            extracted_items = [item for item in extracted_items if item != file.filename]
            
            if not extracted_items:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ZIP文件中没有有效内容"
                )
            
            # 复制解压后的内容到目标目录
            for item in extracted_items:
                source_path = os.path.join(temp_dir, item)
                dest_path = os.path.join(data_dir, item)
                
                if os.path.isdir(source_path):
                    if os.path.exists(dest_path):
                        shutil.rmtree(dest_path)
                    shutil.copytree(source_path, dest_path)
                else:
                    shutil.copy2(source_path, dest_path)
        
        # 创建数据记录
        db_data = db_models.Data(
            personnel_id=personnel_id,
            data_path=data_dir,
            upload_user=1,  # 认证已移除，默认为管理员
            personnel_name=personnel_name,
            user_id=admin_user.user_id,  # 使用动态获取的admin用户ID
            upload_time=datetime.now(),
            md5=md5_value
        )
        
        db.add(db_data)
        db.commit()
        db.refresh(db_data)

        # 使用personnel_id来匹配图片
        stress_score, depression_score, anxiety_score = resolve_scores_for_md5(md5_value, personnel_id)
        overall_risk_level = calculate_overall_risk_level(stress_score, depression_score, anxiety_score)

        existing_results = db.query(db_models.Result).filter(db_models.Result.md5 == md5_value).all()
        for result in existing_results:
            result.stress_score = stress_score
            result.depression_score = depression_score
            result.anxiety_score = anxiety_score
            result.overall_risk_level = overall_risk_level
            result.md5 = md5_value

        db_result = db_models.Result(
            stress_score=stress_score,
            depression_score=depression_score,
            anxiety_score=anxiety_score,
            user_id=admin_user.user_id,
            data_id=db_data.id,
            result_time=datetime.now(),
            personnel_id=personnel_id,
            personnel_name=personnel_name,
            active_learned=False,
            overall_risk_level=overall_risk_level,
            md5=md5_value
        )
        
        db.add(db_result)
        db.commit()
        
        logging.info(f"管理员上传了ZIP数据: {personnel_id}")  # 认证已移除
        
        return db_data
        
    except zipfile.BadZipFile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的ZIP文件"
        )
    except Exception as e:
        logging.error(f"处理ZIP文件时发生错误: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        # 清理可能已创建的目录
        if os.path.exists(data_dir):
            try:
                shutil.rmtree(data_dir)
            except:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理文件时发生错误: {str(e)}"
        )

@router.get("/", response_model=List[schemas.Data])
async def read_data(
    skip: int = 0,
    limit: int = 100,
    personnel_id: Optional[str] = None,
    personnel_name: Optional[str] = None,
    # current_user = Depends(get_current_user),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    获取数据列表
    """
    query = db.query(db_models.Data)
    
    # 普通用户只能查看自己上传的数据
    # if current_user.user_type != "admin":  # 认证已移除
        # query = query.filter(db_models.Data.user_id == current_user.user_id)  # 认证已移除
    
    # 根据参数过滤
    if personnel_id:
        query = query.filter(db_models.Data.personnel_id.ilike(f"%{personnel_id}%"))
    
    if personnel_name:
        query = query.filter(db_models.Data.personnel_name.ilike(f"%{personnel_name}%"))
    
    # 分页并获取结果
    data = query.order_by(db_models.Data.upload_time.desc()).offset(skip).limit(limit).all()
    
    return data

@router.get("/top-200", response_model=List[schemas.Data])
async def get_top_200_data(
    # current_user = Depends(get_current_user),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    获取前200条数据
    """
    query = db.query(db_models.Data)
    
    # 普通用户只能查看自己上传的数据
    # if current_user.user_type != "admin":  # 认证已移除
        # query = query.filter(db_models.Data.user_id == current_user.user_id)  # 认证已移除
    
    # 按上传时间降序获取前200条数据
    data = query.order_by(db_models.Data.upload_time.desc()).limit(200).all()
    
    return data

# 进度相关路由 - 必须在通用路由之前定义
@router.get("/progress")
async def get_batch_progress(
    data_ids: str,  # 逗号分隔的ID列表
    # current_user = Depends(get_current_user),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    获取批量数据的预处理进度
    """
    try:
        # 处理单个ID或多个ID的情况
        if not data_ids or data_ids.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="data_ids参数不能为空"
            )
        
        # 分割ID并转换为整数
        id_list = []
        for id_str in data_ids.split(','):
            id_str = id_str.strip()
            if id_str:
                try:
                    id_list.append(int(id_str))
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"无效的数据ID格式: {id_str}"
                    )
        
        if not id_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="未提供有效的数据ID"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"参数解析失败: {str(e)}"
        )
    
    data_list = db.query(db_models.Data).filter(db_models.Data.id.in_(id_list)).all()
    
    # 权限检查 - 认证已移除
    # if current_user.user_type != "admin":
    #     for data in data_list:
    #         if data.user_id != current_user.user_id:
    #             raise HTTPException(
    #                 status_code=status.HTTP_403_FORBIDDEN,
    #                 detail=f"没有权限查看数据ID: {data.id}"
    #             )
    
    results = []
    for data in data_list:
        # 计算进度百分比（支持模拟进度）
        import time
        progress_percentage = 0
        
        if data.processing_status == "completed" and data.feature_status == "completed":
            progress_percentage = 100
        elif data.processing_status == "failed" or data.feature_status == "failed":
            progress_percentage = 0
        elif data.processing_status == "pending":
            progress_percentage = 0
        elif data.processing_status == "processing" or data.feature_status == "processing":
            # 使用上传时间作为开始时间的近似值
            start_time = data.upload_time.timestamp() if data.upload_time else time.time()
            current_time = time.time()
            elapsed = current_time - start_time
            
            max_time = 60  # 60秒
            max_progress = 99  # 最大99%
            
            # 使用指数增长模拟，前期快，后期慢
            progress = min(max_progress, max_progress * (1 - pow(2.718281828, -elapsed / (max_time / 3))))
            progress_percentage = max(0, round(progress))
        
        results.append({
            "data_id": data.id,
            "personnel_name": data.personnel_name,
            "processing_status": data.processing_status,
            "feature_status": data.feature_status,
            "progress_percentage": progress_percentage,
            "message": f"预处理状态: {data.processing_status}, 特征提取状态: {data.feature_status}"
        })
    
    return results

@router.get("/progress/single/{data_id}")
async def get_data_progress(
    data_id: int,
    # current_user = Depends(get_current_user),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    获取单个数据的预处理进度
    """
    data = db.query(db_models.Data).filter(db_models.Data.id == data_id).first()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID为{data_id}的数据不存在"
        )
    
    # 普通用户只能查看自己的数据
    # if current_user.user_type != "admin" and data.user_id != current_user.user_id:  # 认证已移除
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限查看此数据"
        )
    
    # 计算进度百分比（支持模拟进度）
    import time
    progress_percentage = 0
    
    if data.processing_status == "completed" and data.feature_status == "completed":
        progress_percentage = 100
    elif data.processing_status == "failed" or data.feature_status == "failed":
        progress_percentage = 0
    elif data.processing_status == "pending":
        progress_percentage = 0
    elif data.processing_status == "processing" or data.feature_status == "processing":
        # 使用上传时间作为开始时间的近似值
        start_time = data.upload_time.timestamp() if data.upload_time else time.time()
        current_time = time.time()
        elapsed = current_time - start_time
        
        max_time = 60  # 60秒
        max_progress = 99  # 最大99%
        
        # 使用指数增长模拟，前期快，后期慢
        progress = min(max_progress, max_progress * (1 - pow(2.718281828, -elapsed / (max_time / 3))))
        progress_percentage = max(0, round(progress))
    
    return {
        "data_id": data.id,
        "personnel_name": data.personnel_name,
        "processing_status": data.processing_status,
        "feature_status": data.feature_status,
        "progress_percentage": progress_percentage,
        "message": f"预处理状态: {data.processing_status}, 特征提取状态: {data.feature_status}"
    }

@router.put("/status/{data_id}")
async def update_data_status(
    data_id: int,
    request: schemas.StatusUpdate,
    # current_user = Depends(get_current_user),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    更新数据的处理状态（内部API，供预处理进程调用）
    """
    data = db.query(db_models.Data).filter(db_models.Data.id == data_id).first()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID为{data_id}的数据不存在"
        )
    
    # 更新状态
    if request.processing_status:
        data.processing_status = request.processing_status
    if request.feature_status:
        data.feature_status = request.feature_status
    
    db.commit()
    db.refresh(data)
    
    return {
        "message": "状态更新成功",
        "processing_status": data.processing_status,
        "feature_status": data.feature_status
    }

@router.get("/{data_id}", response_model=schemas.Data)
async def read_data_by_id(
    data_id: int,
    # current_user = Depends(get_current_user),  # 认证已移除
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
    # if current_user.user_type != "admin" and db_data.user_id != current_user.user_id:  # 认证已移除
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限查看此数据"
        )
    
    return db_data

@router.delete("/{data_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_data(
    data_id: int,
    # current_user = Depends(get_current_user),  # 认证已移除
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
    # if current_user.user_type != "admin" and db_data.user_id != current_user.user_id:  # 认证已移除
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
    
    logging.info(f"管理员删除了数据ID: {data_id}")  # 认证已移除
    
    return None

@router.post("/batch-upload", response_model=schemas.BatchUploadResponse)
async def batch_upload_data(
    files: List[UploadFile] = File(...),
    # current_user = Depends(get_current_user),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    批量上传ZIP数据文件
    文件名格式应为：人员ID_姓名.zip
    """
    logging.info(f"批量上传请求开始，收到 {len(files)} 个文件")
    for file in files:
        logging.info(f"接收到的文件: {file.filename}, content_type: {file.content_type}")
    
    # 获取admin用户（认证已移除，使用默认admin用户）
    admin_user = db.query(db_models.User).filter(db_models.User.user_type == 'admin').first()
    if not admin_user:
        logging.error("数据库中不存在admin用户")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="数据库中不存在admin用户，请先创建admin用户"
        )
    
    logging.info(f"使用admin用户: {admin_user.user_id}")
    
    success_count = 0
    failed_count = 0
    uploaded_data = []
    errors = []
    
    for file in files:
        try:
            logging.info(f"开始处理文件: {file.filename}")
            
            # 验证文件格式
            if not file.filename.lower().endswith('.zip'):
                error_msg = f"{file.filename}: 只支持ZIP文件格式"
                logging.error(error_msg)
                errors.append(error_msg)
                failed_count += 1
                continue
            
            # 从文件名解析personnel_id和personnel_name
            # 文件名格式：人员ID_姓名.zip
            filename_without_ext = os.path.splitext(file.filename)[0]
            filename_parts = filename_without_ext.split('_')
            
            logging.info(f"文件名解析: {file.filename} -> personnel_id: {filename_parts[0] if filename_parts else 'N/A'}, parts: {len(filename_parts)}")
            
            if len(filename_parts) >= 2:
                personnel_id = filename_parts[0]
                personnel_name = '_'.join(filename_parts[1:])  # 支持姓名中包含下划线
            else:
                personnel_id = filename_without_ext
                personnel_name = filename_without_ext
            
            # 创建数据目录（允许同一人员上传多个文件）
            data_dir = os.path.join(DATA_DIR, personnel_id)
            os.makedirs(data_dir, exist_ok=True)
            logging.info(f"创建数据目录: {data_dir}")
            
            try:
                # 创建临时目录处理ZIP文件
                with tempfile.TemporaryDirectory() as temp_dir:
                    # 保存ZIP文件到临时目录
                    zip_path = os.path.join(temp_dir, file.filename)
                    
                    # 重置文件指针
                    await file.seek(0)
                    md5_hash = hashlib.md5()
                    with open(zip_path, "wb") as buffer:
                        while True:
                            chunk = await file.read(8192)
                            if not chunk:
                                break
                            md5_hash.update(chunk)
                            buffer.write(chunk)
                    md5_value = md5_hash.hexdigest()
                    
                    logging.info(f"ZIP文件已保存到临时目录: {zip_path}")
                    
                    # 解压ZIP文件
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    
                    logging.info(f"ZIP文件解压完成")
                    
                    # 获取解压后的内容
                    extracted_items = os.listdir(temp_dir)
                    extracted_items = [item for item in extracted_items if item != file.filename]
                    
                    logging.info(f"解压后的内容: {extracted_items}")
                    
                    if not extracted_items:
                        error_msg = f"{file.filename}: ZIP文件中没有有效内容"
                        logging.error(error_msg)
                        errors.append(error_msg)
                        failed_count += 1
                        if os.path.exists(data_dir):
                            shutil.rmtree(data_dir)
                        continue
                    
                    # 复制解压后的内容到目标目录
                    for item in extracted_items:
                        source_path = os.path.join(temp_dir, item)
                        dest_path = os.path.join(data_dir, item)
                        
                        if os.path.isdir(source_path):
                            if os.path.exists(dest_path):
                                shutil.rmtree(dest_path)
                            shutil.copytree(source_path, dest_path)
                        else:
                            shutil.copy2(source_path, dest_path)
                    
                    logging.info(f"文件已复制到目标目录: {data_dir}")
                
                # 创建数据记录
                logging.info(f"准备创建数据库记录: personnel_id={personnel_id}, personnel_name={personnel_name}")
                
                db_data = db_models.Data(
                    personnel_id=personnel_id,
                    data_path=data_dir,
                    upload_user=1,  # 认证已移除，默认为管理员
                    personnel_name=personnel_name,
                    user_id=admin_user.user_id,  # 使用动态获取的admin用户ID
                    upload_time=datetime.now(),
                    md5=md5_value
                )
                
                db.add(db_data)
                db.commit()
                db.refresh(db_data)

                stress_score, depression_score, anxiety_score = resolve_scores_for_md5(md5_value, admin_user.user_id)
                overall_risk_level = calculate_overall_risk_level(stress_score, depression_score, anxiety_score)

                existing_results = db.query(db_models.Result).filter(db_models.Result.md5 == md5_value).all()
                for result in existing_results:
                    result.stress_score = stress_score
                    result.depression_score = depression_score
                    result.anxiety_score = anxiety_score
                    result.overall_risk_level = overall_risk_level
                    result.md5 = md5_value

                db_result = db_models.Result(
                    stress_score=stress_score,
                    depression_score=depression_score,
                    anxiety_score=anxiety_score,
                    user_id=admin_user.user_id,
                    data_id=db_data.id,
                    result_time=datetime.now(),
                    personnel_id=personnel_id,
                    personnel_name=personnel_name,
                    active_learned=False,
                    overall_risk_level=overall_risk_level,
                    md5=md5_value
                )
                
                db.add(db_result)
                db.commit()
                
                logging.info(f"数据库记录创建成功，ID: {db_data.id}")
                
                uploaded_data.append(db_data)
                success_count += 1
                
                logging.info(f"管理员批量上传了ZIP数据: {personnel_id}")  # 认证已移除
                
            except zipfile.BadZipFile as e:
                error_msg = f"{file.filename}: 无效的ZIP文件 - {str(e)}"
                logging.error(error_msg)
                errors.append(error_msg)
                failed_count += 1
                if os.path.exists(data_dir):
                    shutil.rmtree(data_dir)
            except Exception as e:
                import traceback
                error_msg = f"{file.filename}: 处理文件时发生错误 - {str(e)}"
                logging.error(error_msg)
                logging.error(traceback.format_exc())
                errors.append(error_msg)
                failed_count += 1
                if os.path.exists(data_dir):
                    try:
                        shutil.rmtree(data_dir)
                    except:
                        pass
                        
        except Exception as e:
            import traceback
            error_msg = f"{file.filename}: 处理失败 - {str(e)}"
            logging.error(error_msg)
            logging.error(traceback.format_exc())
            errors.append(error_msg)
            failed_count += 1
    
    logging.info(f"管理员批量上传完成: 成功{success_count}个, 失败{failed_count}个")  # 认证已移除
    
    # 将 SQLAlchemy 对象转换为 Pydantic 模型（使用 from_orm 方法）
    uploaded_data_pydantic = [schemas.Data.from_orm(data) for data in uploaded_data]
    
    return schemas.BatchUploadResponse(
        success_count=success_count,
        failed_count=failed_count,
        uploaded_data=uploaded_data_pydantic,
        errors=errors
    ) 

@router.post("/batch-delete")
async def batch_delete_data(
    request: schemas.BatchDeleteRequest,
    # current_user = Depends(get_current_user),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    批量删除数据
    """
    if not request.data_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请提供要删除的数据ID列表"
        )
    
    # 查询要删除的数据
    data_list = db.query(db_models.Data).filter(db_models.Data.id.in_(request.data_ids)).all()
    
    # 普通用户只能删除自己上传的数据 - 认证已移除
    # if current_user.user_type != "admin":
    #     for data in data_list:
    #         if data.user_id != current_user.user_id:
    #             raise HTTPException(
    #                 status_code=status.HTTP_403_FORBIDDEN,
    #                 detail=f"没有权限删除数据ID: {data.id}"
    #             )
    
    deleted_count = 0
    errors = []
    
    for data in data_list:
        try:
            # 删除相关的结果
            db.query(db_models.Result).filter(db_models.Result.data_id == data.id).delete()
            
            # 删除数据记录
            db.delete(data)
            
            # 尝试删除数据目录
            try:
                if os.path.exists(data.data_path):
                    shutil.rmtree(data.data_path)
            except Exception as e:
                logging.warning(f"删除数据目录失败: {str(e)}")
            
            deleted_count += 1
        except Exception as e:
            errors.append(f"删除数据ID {data.id} 失败: {str(e)}")
            logging.error(f"删除数据ID {data.id} 失败: {str(e)}")
    
    if deleted_count > 0:
        db.commit()
    
    logging.info(f"管理员批量删除了{deleted_count}条数据")  # 认证已移除
    
    if errors:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"部分删除失败，成功删除{deleted_count}条，错误: {'; '.join(errors)}"
        )
    
    return {"message": f"成功删除{deleted_count}条数据"}

async def simulate_preprocess_task(data_id: int):
    """后台任务：模拟预处理过程"""
    from database import SessionLocal
    db = SessionLocal()
    try:
        # 等待 3-5 秒
        await asyncio.sleep(4)
        
        # 更新状态为已完成
        data = db.query(db_models.Data).filter(db_models.Data.id == data_id).first()
        if data:
            data.processing_status = "completed"
            data.feature_status = "completed"
            db.commit()
            logging.info(f"数据ID {data_id} 预处理完成（模拟处理）")
    except Exception as e:
        logging.error(f"模拟预处理任务失败: {e}")
        # 更新状态为失败
        data = db.query(db_models.Data).filter(db_models.Data.id == data_id).first()
        if data:
            data.processing_status = "failed"
            db.commit()
    finally:
        db.close()

@router.post("/{data_id}/preprocess")
async def preprocess_single_data(
    data_id: int,
    background_tasks: BackgroundTasks,
    # current_user = Depends(get_current_user),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    单个数据预处理（模拟处理）
    """
    # 查询数据
    data = db.query(db_models.Data).filter(db_models.Data.id == data_id).first()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID为{data_id}的数据不存在"
        )
    
    data_path = data.data_path
    if not os.path.exists(data_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"数据路径{data_path}不存在"
        )

    result = db.query(db_models.Result).filter(db_models.Result.data_id == data_id).first()
    if not result or result.blood_oxygen is None or not result.blood_pressure:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先填写血氧血压后再进行预处理"
        )
    
    try:
        # 先设置为正在处理状态
        data.processing_status = "processing"
        data.feature_status = "processing"
        db.commit()
        
        # 添加后台任务进行模拟处理
        background_tasks.add_task(simulate_preprocess_task, data_id)
        
        return {
            "data_id": data_id,
            "success": True,
            "message": "预处理已开始"
        }
        
    except Exception as e:
        import traceback
        error_msg = f"预处理数据ID {data_id} 失败: {str(e)}"
        stack_trace = traceback.format_exc()
        logging.error(f"{error_msg}\n{stack_trace}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{error_msg}\n详细错误: {str(e)}"
        )

@router.post("/batch-preprocess")
async def batch_preprocess_data(
    request: schemas.BatchPreprocessRequest,
    background_tasks: BackgroundTasks,
    # current_user = Depends(get_current_user),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    批量预处理数据（模拟处理）
    """
    if not request.data_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请提供要预处理的数据ID列表"
        )
    
    # 验证数据ID存在性
    data_list = db.query(db_models.Data).filter(db_models.Data.id.in_(request.data_ids)).all()
    if len(data_list) != len(request.data_ids):
        missing_ids = set(request.data_ids) - {data.id for data in data_list}
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"以下数据ID不存在: {missing_ids}"
        )
    
    missing_ids = []
    for data in data_list:
        result = db.query(db_models.Result).filter(db_models.Result.data_id == data.id).first()
        if not result or result.blood_oxygen is None or not result.blood_pressure:
            missing_ids.append(data.id)
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"以下数据未填写血氧血压，无法预处理: {missing_ids}"
        )

    # 先将所有数据设置为正在处理状态
    for data in data_list:
        data.processing_status = "processing"
        data.feature_status = "processing"
    db.commit()
    
    # 为每个数据添加后台任务
    for data in data_list:
        background_tasks.add_task(simulate_preprocess_task, data.id)
    
    logging.info(f"批量预处理已开始，共{len(data_list)}个数据")
    
    return {
        "success_count": len(data_list),
        "failed_count": 0,
        "results": [{"data_id": data.id, "success": True, "message": "预处理已开始"} for data in data_list]
    } 