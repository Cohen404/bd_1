from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import os
import shutil
from datetime import datetime
import zipfile
import tempfile

from database import get_db
import models as db_models
import schemas
# from auth import get_current_user, check_permission  # 认证已移除
from config import DATA_DIR

router = APIRouter()

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
    
    # 创建数据目录
    data_dir = os.path.join(DATA_DIR, personnel_id)
    os.makedirs(data_dir, exist_ok=True)
    
    try:
        # 创建临时目录处理ZIP文件
        with tempfile.TemporaryDirectory() as temp_dir:
            # 保存ZIP文件到临时目录
            zip_path = os.path.join(temp_dir, file.filename)
            with open(zip_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
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
            user_id="72f220b7-f583-4034-8f44-08b5986c2835",  # 认证已移除，默认为admin用户ID
            upload_time=datetime.now()
        )
        
        db.add(db_data)
        db.commit()
        db.refresh(db_data)
        
        logging.info(f"管理员上传了ZIP数据: {personnel_id}")  # 认证已移除
        
        return db_data
        
    except zipfile.BadZipFile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的ZIP文件"
        )
    except Exception as e:
        logging.error(f"处理ZIP文件时发生错误: {str(e)}")
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
    success_count = 0
    failed_count = 0
    uploaded_data = []
    errors = []
    
    for file in files:
        try:
            # 验证文件格式
            if not file.filename.lower().endswith('.zip'):
                errors.append(f"{file.filename}: 只支持ZIP文件格式")
                failed_count += 1
                continue
            
            # 从文件名解析personnel_id和personnel_name
            # 文件名格式：人员ID_姓名.zip
            filename_without_ext = os.path.splitext(file.filename)[0]
            filename_parts = filename_without_ext.split('_')
            
            if len(filename_parts) >= 2:
                personnel_id = filename_parts[0]
                personnel_name = '_'.join(filename_parts[1:])  # 支持姓名中包含下划线
            else:
                personnel_id = filename_without_ext
                personnel_name = filename_without_ext
            
            # 检查是否已存在相同的personnel_id
            existing_data = db.query(db_models.Data).filter(
                db_models.Data.personnel_id == personnel_id
            ).first()
            
            if existing_data:
                errors.append(f"{file.filename}: 人员ID {personnel_id} 已存在")
                failed_count += 1
                continue
            
            # 创建数据目录
            data_dir = os.path.join(DATA_DIR, personnel_id)
            os.makedirs(data_dir, exist_ok=True)
            
            try:
                # 创建临时目录处理ZIP文件
                with tempfile.TemporaryDirectory() as temp_dir:
                    # 保存ZIP文件到临时目录
                    zip_path = os.path.join(temp_dir, file.filename)
                    
                    # 重置文件指针
                    await file.seek(0)
                    with open(zip_path, "wb") as buffer:
                        shutil.copyfileobj(file.file, buffer)
                    
                    # 解压ZIP文件
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    
                    # 获取解压后的内容
                    extracted_items = os.listdir(temp_dir)
                    extracted_items = [item for item in extracted_items if item != file.filename]
                    
                    if not extracted_items:
                        errors.append(f"{file.filename}: ZIP文件中没有有效内容")
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
                
                # 创建数据记录
                db_data = db_models.Data(
                    personnel_id=personnel_id,
                    data_path=data_dir,
                    upload_user=1,  # 认证已移除，默认为管理员
                    personnel_name=personnel_name,
                    user_id="72f220b7-f583-4034-8f44-08b5986c2835",  # 认证已移除，默认为admin用户ID
                    upload_time=datetime.now()
                )
                
                db.add(db_data)
                db.commit()
                db.refresh(db_data)
                
                uploaded_data.append(db_data)
                success_count += 1
                
                logging.info(f"管理员批量上传了ZIP数据: {personnel_id}")  # 认证已移除
                
            except zipfile.BadZipFile:
                errors.append(f"{file.filename}: 无效的ZIP文件")
                failed_count += 1
                if os.path.exists(data_dir):
                    shutil.rmtree(data_dir)
            except Exception as e:
                errors.append(f"{file.filename}: 处理文件时发生错误 - {str(e)}")
                failed_count += 1
                if os.path.exists(data_dir):
                    try:
                        shutil.rmtree(data_dir)
                    except:
                        pass
                        
        except Exception as e:
            errors.append(f"{file.filename}: 处理失败 - {str(e)}")
            failed_count += 1
    
    logging.info(f"管理员批量上传完成: 成功{success_count}个, 失败{failed_count}个")  # 认证已移除
    
    return schemas.BatchUploadResponse(
        success_count=success_count,
        failed_count=failed_count,
        uploaded_data=uploaded_data,
        errors=errors
    ) 

@router.delete("/batch-delete")
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

@router.post("/{data_id}/preprocess")
async def preprocess_single_data(
    data_id: int,
    # current_user = Depends(get_current_user),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    单个数据预处理
    """
    from data_preprocess import treat
    from data_feature_calculation import analyze_eeg_data, plot_serum_data, plot_scale_data
    
    # 查询数据
    data = db.query(db_models.Data).filter(db_models.Data.id == data_id).first()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID为{data_id}的数据不存在"
        )
    
    # 普通用户只能预处理自己上传的数据
    # if current_user.user_type != "admin" and data.user_id != current_user.user_id:  # 认证已移除
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限预处理此数据"
        )
    
    data_path = data.data_path
    if not os.path.exists(data_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"数据路径{data_path}不存在"
        )
    
    try:
        # 检查是否已经有特征图片（说明已经预处理过了）
        required_images = [
            'time_过零率.png', 'time_方差.png', 'time_能量.png', 'time_差分.png',
            'frequency_band_1.png', 'frequency_band_2.png', 'frequency_band_3.png',
            'frequency_band_4.png', 'frequency_band_5.png',
            'frequency_wavelet.png', 'differential_entropy.png',
            'Theta.png', 'Alpha.png', 'Beta.png', 'Gamma.png'
        ]
        
        # 检查当前目录或子目录中是否已有所有图片
        has_all_images = all(os.path.exists(os.path.join(data_path, img)) for img in required_images)
        
        if not has_all_images:
            # 检查子目录
            for item in os.listdir(data_path):
                item_path = os.path.join(data_path, item)
                if os.path.isdir(item_path):
                    sub_has_all_images = all(os.path.exists(os.path.join(item_path, img)) for img in required_images)
                    if sub_has_all_images:
                        has_all_images = True
                        break
        
        if has_all_images:
            # 如果已经有所有图片，说明已经预处理完成
            logging.info(f"数据ID {data_id} 已经预处理完成（存在所有特征图片）")
            # 更新状态为已完成
            data.processing_status = "completed"
            data.feature_status = "completed"
            db.commit()
        else:
            # 更新状态为正在处理
            data.processing_status = "processing"
            data.feature_status = "pending"
            db.commit()
            
            # 如果没有图片，执行数据预处理
            success = treat(data_path)
            if not success:
                # 更新状态为失败
                data.processing_status = "failed"
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="数据预处理失败，找不到支持的脑电数据文件或预处理过程出错"
                )
            
            # 预处理完成，更新状态
            data.processing_status = "completed"
            data.feature_status = "processing"
            db.commit()
            
            # 检查是否有FIF文件
            fif_files = [f for f in os.listdir(data_path) if f.endswith('.fif')]
            if fif_files:
                # 执行特征分析和生成可视化图片
                fif_path = os.path.join(data_path, fif_files[0])
                analyze_eeg_data(fif_path)
                plot_serum_data(data_path)
                plot_scale_data(data_path)
                
                # 特征提取完成，更新状态
                data.feature_status = "completed"
                db.commit()
        
        logging.info(f"管理员完成了数据ID {data_id} 的预处理")  # 认证已移除
        
        return {
            "data_id": data_id,
            "success": True,
            "message": "预处理完成"
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
    # current_user = Depends(get_current_user),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    批量预处理数据
    """
    from data_preprocess import treat
    from data_feature_calculation import analyze_eeg_data, plot_serum_data, plot_scale_data
    from concurrent.futures import ThreadPoolExecutor
    
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
    
    # 权限检查：普通用户只能预处理自己的数据 - 认证已移除
    # if current_user.user_type != "admin":
    #     for data in data_list:
    #         if data.user_id != current_user.user_id:
    #             raise HTTPException(
    #                 status_code=status.HTTP_403_FORBIDDEN,
    #                 detail=f"您没有权限预处理数据ID: {data.id}"
    #             )
    
    def process_single_data(data):
        """处理单个数据的预处理"""
        try:
            data_path = data.data_path
            if not os.path.exists(data_path):
                # 更新状态为失败
                data.processing_status = "failed"
                db.commit()
                return {
                    "data_id": data.id,
                    "success": False,
                    "message": f"数据路径不存在: {data_path}"
                }
            
            # 检查是否已经有特征图片（说明已经预处理过了）
            required_images = [
                'time_过零率.png', 'time_方差.png', 'time_能量.png', 'time_差分.png',
                'frequency_band_1.png', 'frequency_band_2.png', 'frequency_band_3.png',
                'frequency_band_4.png', 'frequency_band_5.png',
                'frequency_wavelet.png', 'differential_entropy.png',
                'Theta.png', 'Alpha.png', 'Beta.png', 'Gamma.png'
            ]
            
            # 检查当前目录或子目录中是否已有所有图片
            has_all_images = all(os.path.exists(os.path.join(data_path, img)) for img in required_images)
            
            if not has_all_images:
                # 检查子目录
                for item in os.listdir(data_path):
                    item_path = os.path.join(data_path, item)
                    if os.path.isdir(item_path):
                        sub_has_all_images = all(os.path.exists(os.path.join(item_path, img)) for img in required_images)
                        if sub_has_all_images:
                            has_all_images = True
                            break
            
            if has_all_images:
                # 如果已经有所有图片，说明已经预处理完成
                logging.info(f"数据ID {data.id} 已经预处理完成（存在所有特征图片）")
                # 更新状态为已完成
                data.processing_status = "completed"
                data.feature_status = "completed"
                db.commit()
                return {
                    "data_id": data.id,
                    "success": True,
                    "message": "预处理完成（已存在特征图片）"
                }
            else:
                # 更新状态为正在处理
                data.processing_status = "processing"
                data.feature_status = "pending"
                db.commit()
                
                # 如果没有图片，执行数据预处理
                success = treat(data_path)
                if not success:
                    # 更新状态为失败
                    data.processing_status = "failed"
                    db.commit()
                    return {
                        "data_id": data.id,
                        "success": False,
                        "message": "数据预处理失败，找不到支持的脑电数据文件或预处理过程出错"
                    }
                
                # 预处理完成，更新状态
                data.processing_status = "completed"
                data.feature_status = "processing"
                db.commit()
                
                # 检查是否有FIF文件
                fif_files = [f for f in os.listdir(data_path) if f.endswith('.fif')]
                if fif_files:
                    # 执行特征分析和生成可视化图片
                    fif_path = os.path.join(data_path, fif_files[0])
                    analyze_eeg_data(fif_path)
                    plot_serum_data(data_path)
                    plot_scale_data(data_path)
                    
                    # 特征提取完成，更新状态
                    data.feature_status = "completed"
                    db.commit()
                
                return {
                    "data_id": data.id,
                    "success": True,
                    "message": "预处理完成"
                }
            
        except Exception as e:
            import traceback
            error_msg = f"预处理失败: {str(e)}"
            stack_trace = traceback.format_exc()
            logging.error(f"预处理数据ID {data.id} 失败: {error_msg}\n{stack_trace}")
            return {
                "data_id": data.id,
                "success": False,
                "message": error_msg
            }
    
    # 使用线程池并发处理
    results = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(process_single_data, data_list))
    
    success_count = sum(1 for result in results if result['success'])
    failed_count = len(results) - success_count
    
    logging.info(f"管理员完成批量预处理，成功{success_count}个，失败{failed_count}个")  # 认证已移除
    
    return {
        "message": f"批量预处理完成，成功{success_count}个，失败{failed_count}个",
        "success_count": success_count,
        "failed_count": failed_count,
        "results": results
    } 