from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
import os
import logging
from typing import List, Dict, Any
import asyncio
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import glob

from database import get_db, SessionLocal
import models as db_models
import schemas
from auth import get_current_user, check_permission
from model_inference import EegModel, BatchInferenceModel, ResultProcessor
from data_preprocess import treat
from data_feature_calculation import analyze_eeg_data, plot_serum_data, plot_scale_data
from config import DATA_DIR, RESULTS_DIR

router = APIRouter()

# 图像类型映射
IMAGE_TYPES = {
    "theta": ("Theta功率特征图", "Theta.png"),
    "alpha": ("Alpha功率特征图", "Alpha.png"),
    "beta": ("Beta功率特征图", "Beta.png"),
    "gamma": ("Gamma功率特征图", "Gamma.png"),
    "frequency_band_1": ("均分频带1特征图", "frequency_band_1.png"),
    "frequency_band_2": ("均分频带2特征图", "frequency_band_2.png"),
    "frequency_band_3": ("均分频带3特征图", "frequency_band_3.png"),
    "frequency_band_4": ("均分频带4特征图", "frequency_band_4.png"),
    "frequency_band_5": ("均分频带5特征图", "frequency_band_5.png"),
    "time_zero_crossing": ("时域特征-过零率", "time_过零率.png"),
    "time_variance": ("时域特征-方差", "time_方差.png"),
    "time_energy": ("时域特征-能量", "time_能量.png"),
    "time_difference": ("时域特征-差分", "time_差分.png"),
    "frequency_wavelet": ("时频域特征图", "frequency_wavelet.png"),
    "differential_entropy": ("微分熵特征图", "differential_entropy.png"),
    "serum_analysis": ("血清指标分析", "serum_analysis.png"),
}

@router.post("/evaluate", response_model=schemas.Result)
async def evaluate_health(
    request: schemas.HealthEvaluateRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    对指定的数据进行健康评估
    """
    # 查询数据
    data = db.query(db_models.Data).filter(db_models.Data.id == request.data_id).first()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID为{request.data_id}的数据不存在"
        )
    
    # 预处理数据
    data_path = data.data_path
    if not os.path.exists(data_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"数据路径{data_path}不存在"
        )
    
    # 检查是否有FIF文件，如果没有则进行预处理
    fif_files = [f for f in os.listdir(data_path) if f.endswith('.fif')]
    if not fif_files:
        logging.info(f"对数据ID: {request.data_id}进行预处理")
        success = treat(data_path)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="数据预处理失败"
            )
    
    try:
        # 执行特征分析和绘图
        analyze_eeg_data(data_path)
        plot_serum_data(data_path)
        plot_scale_data(data_path)
        
        # 模型推理
        eeg_model = EegModel(data_path, None)  # 使用默认模型
        scores = eeg_model.calculate_scale_scores()
        
        # 计算最终得分
        final_scores = {
            'stress_score': eeg_model.calculate_final_score(scores.get('stress_model_score', 0), scores.get('stress_scale_score', 0), 'stress'),
            'depression_score': eeg_model.calculate_final_score(scores.get('depression_model_score', 0), scores.get('depression_scale_score', 0), 'depression'),
            'anxiety_score': eeg_model.calculate_final_score(scores.get('anxiety_model_score', 0), scores.get('anxiety_scale_score', 0), 'anxiety'),
            'social_isolation_score': eeg_model.calculate_final_score(scores.get('social_model_score', 0), scores.get('social_scale_score', 0), 'social')
        }
        
        # 应激评分调整
        final_scores['stress_score'] = eeg_model.adjust_stress_score(
            final_scores['stress_score'],
            final_scores['depression_score'],
            final_scores['anxiety_score']
        )
        
        # 生成报告
        result_processor = ResultProcessor(data_path, final_scores)
        report_path = result_processor.generate_report()
        
        # 保存结果到数据库
        result = db_models.Result(
            stress_score=final_scores['stress_score'],
            depression_score=final_scores['depression_score'],
            anxiety_score=final_scores['anxiety_score'],
            social_isolation_score=final_scores['social_isolation_score'],
            user_id=current_user.user_id,
            data_id=request.data_id,
            report_path=report_path,
            result_time=datetime.now()
        )
        
        db.add(result)
        db.commit()
        db.refresh(result)
        
        logging.info(f"用户 {current_user.username} 完成了数据ID {request.data_id} 的健康评估")
        
        return result
    
    except Exception as e:
        logging.error(f"健康评估失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"健康评估失败: {str(e)}"
        )

@router.post("/batch-evaluate")
async def batch_evaluate_health(
    request: schemas.BatchHealthEvaluateRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量健康评估
    """
    # 验证数据ID存在性
    data_list = db.query(db_models.Data).filter(db_models.Data.id.in_(request.data_ids)).all()
    if len(data_list) != len(request.data_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="部分数据ID不存在"
        )
    
    # 权限检查：普通用户只能评估自己的数据
    if current_user.user_type != "admin":
        for data in data_list:
            if data.user_id != current_user.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"您没有权限评估数据ID: {data.id}"
                )
    
    # 启动后台批量评估任务
    background_tasks.add_task(
        perform_batch_evaluation,
        request.data_ids,
        current_user.user_id,
        current_user.username
    )
    
    return {
        "message": f"已启动 {len(request.data_ids)} 个数据的批量评估任务",
        "data_ids": request.data_ids,
        "status": "processing"
    }

async def perform_batch_evaluation(data_ids: List[int], user_id: str, username: str):
    """
    执行批量评估的后台任务
    """
    def evaluate_single_data(data_id: int):
        try:
            with SessionLocal() as session:
                data = session.query(db_models.Data).filter(db_models.Data.id == data_id).first()
                if not data or not os.path.exists(data.data_path):
                    return {"data_id": data_id, "success": False, "message": "数据不存在"}
                
                data_path = data.data_path
                
                # 检查是否需要预处理
                fif_files = [f for f in os.listdir(data_path) if f.endswith('.fif')]
                if not fif_files:
                    success = treat(data_path)
                    if not success:
                        return {"data_id": data_id, "success": False, "message": "预处理失败"}
                
                # 执行特征分析和绘图
                analyze_eeg_data(data_path)
                plot_serum_data(data_path)
                plot_scale_data(data_path)
                
                # 模型推理
                eeg_model = EegModel(data_path, None)
                scores = eeg_model.calculate_scale_scores()
        
                # 计算最终得分
                final_scores = {
                    'stress_score': eeg_model.calculate_final_score(scores.get('stress_model_score', 0), scores.get('stress_scale_score', 0), 'stress'),
                    'depression_score': eeg_model.calculate_final_score(scores.get('depression_model_score', 0), scores.get('depression_scale_score', 0), 'depression'),
                    'anxiety_score': eeg_model.calculate_final_score(scores.get('anxiety_model_score', 0), scores.get('anxiety_scale_score', 0), 'anxiety'),
                    'social_isolation_score': eeg_model.calculate_final_score(scores.get('social_model_score', 0), scores.get('social_scale_score', 0), 'social')
                }
                
                # 应激评分调整
                final_scores['stress_score'] = eeg_model.adjust_stress_score(
                    final_scores['stress_score'],
                    final_scores['depression_score'],
                    final_scores['anxiety_score']
                )
                
                # 生成报告
                result_processor = ResultProcessor(data_path, final_scores)
                report_path = result_processor.generate_report()
                
                # 保存结果到数据库
                result = db_models.Result(
                    stress_score=final_scores['stress_score'],
                    depression_score=final_scores['depression_score'],
                    anxiety_score=final_scores['anxiety_score'],
                    social_isolation_score=final_scores['social_isolation_score'],
                    user_id=user_id,
                    data_id=data_id,
                    report_path=report_path,
                    result_time=datetime.now()
                )
                
                session.add(result)
                session.commit()
                session.refresh(result)
                
                return {
                    "data_id": data_id, 
                    "success": True, 
                    "message": "评估成功",
                    "result_id": result.id,
                    "scores": final_scores
                }
    
        except Exception as e:
            logging.error(f"评估数据ID {data_id} 失败: {str(e)}")
            return {"data_id": data_id, "success": False, "message": f"评估错误: {str(e)}"}
    
    # 并发处理评估任务
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(evaluate_single_data, data_ids))
    
    logging.info(f"用户 {username} 完成批量评估，共处理 {len(data_ids)} 个数据")
    return results

@router.get("/reports/{result_id}", response_model=schemas.Result)
async def get_evaluate_report(
    result_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取评估报告
    """
    # 查询结果
    result = db.query(db_models.Result).filter(db_models.Result.id == result_id).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID为{result_id}的结果不存在"
        )
    
    # 检查权限
    if result.user_id != current_user.user_id and current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限查看此报告"
        )
    
    # 如果报告不存在，生成报告
    if not result.report_path or not os.path.exists(result.report_path):
        result_processor = ResultProcessor(result.id, db)
        report_path = await result_processor.generate_report()
        
        if report_path:
            # 更新报告路径
            result.report_path = report_path
            db.commit()
    
    return result 

@router.get("/led-status/{result_id}", response_model=schemas.LEDStatus)
async def get_led_status(
    result_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取评估结果的LED状态
    """
    result = db.query(db_models.Result).filter(db_models.Result.id == result_id).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID为{result_id}的结果不存在"
        )
    
    # 权限检查
    if current_user.user_type != "admin" and result.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限查看此结果"
        )
    
    # 根据分数确定LED状态
    def get_led_color(score: float) -> str:
        return "red" if score >= 50 else "gray"
    
    return schemas.LEDStatus(
        stress_led=get_led_color(result.stress_score),
        depression_led=get_led_color(result.depression_score),
        anxiety_led=get_led_color(result.anxiety_score),
        social_led=get_led_color(result.social_isolation_score),
        stress_score=result.stress_score,
        depression_score=result.depression_score,
        anxiety_score=result.anxiety_score,
        social_isolation_score=result.social_isolation_score
    )

@router.get("/images/{data_id}", response_model=List[schemas.ImageInfo])
async def get_data_images(
    data_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取数据的所有可用图像列表
    """
    data = db.query(db_models.Data).filter(db_models.Data.id == data_id).first()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID为{data_id}的数据不存在"
        )
    
    # 权限检查
    if current_user.user_type != "admin" and data.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限查看此数据"
        )
    
    images = []
    data_path = data.data_path
    
    # 检查每种图像类型是否存在
    for image_key, (description, filename) in IMAGE_TYPES.items():
        image_path = os.path.join(data_path, filename)
        
        # 首先检查当前目录
        if os.path.exists(image_path):
            images.append(schemas.ImageInfo(
                image_type=image_key,
                image_name=filename,
                image_path=image_path,
                description=description
            ))
        else:
            # 如果当前目录没有，检查子目录
            for item in os.listdir(data_path):
                item_path = os.path.join(data_path, item)
                if os.path.isdir(item_path):
                    sub_image_path = os.path.join(item_path, filename)
                    if os.path.exists(sub_image_path):
                        images.append(schemas.ImageInfo(
                            image_type=image_key,
                            image_name=filename,
                            image_path=sub_image_path,
                            description=description
                        ))
                        break  # 找到后就停止搜索
    
    return images

@router.get("/image/{data_id}/{image_type}")
async def view_image(
    data_id: int,
    image_type: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查看特定类型的图像
    """
    from fastapi.responses import FileResponse
    
    data = db.query(db_models.Data).filter(db_models.Data.id == data_id).first()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID为{data_id}的数据不存在"
        )
    
    # 权限检查
    if current_user.user_type != "admin" and data.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限查看此数据"
        )
    
    # 检查图像类型是否有效
    if image_type not in IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的图像类型: {image_type}"
        )
    
    # 构建图像路径
    filename = IMAGE_TYPES[image_type][1]
    image_path = os.path.join(data.data_path, filename)
    
    # 如果当前目录没有图片，搜索子目录
    if not os.path.exists(image_path):
        found = False
        for item in os.listdir(data.data_path):
            item_path = os.path.join(data.data_path, item)
            if os.path.isdir(item_path):
                sub_image_path = os.path.join(item_path, filename)
                if os.path.exists(sub_image_path):
                    image_path = sub_image_path
                    found = True
                    break
        
        if not found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"图像文件不存在: {filename}"
            )
    
    return FileResponse(
        path=image_path,
        media_type="image/png",
        filename=filename
    )

@router.get("/status/{data_id}", response_model=schemas.EvaluationStatus)
async def get_evaluation_status(
    data_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取数据的评估状态
    """
    data = db.query(db_models.Data).filter(db_models.Data.id == data_id).first()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID为{data_id}的数据不存在"
        )
    
    # 权限检查
    if current_user.user_type != "admin" and data.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限查看此数据"
        )
    
    # 检查是否有评估结果
    result = db.query(db_models.Result).filter(db_models.Result.data_id == data_id).first()
    
    if result:
        return schemas.EvaluationStatus(
            data_id=data_id,
            status="completed",
            progress=1.0,
            message="评估已完成",
            result_id=result.id
        )
    else:
        # 检查是否有预处理文件
        fif_files = glob.glob(os.path.join(data.data_path, "*.fif"))
        if fif_files:
            return schemas.EvaluationStatus(
                data_id=data_id,
                status="pending",
                progress=0.5,
                message="数据已预处理，等待评估"
            )
        else:
            return schemas.EvaluationStatus(
                data_id=data_id,
                status="pending",
                progress=0.0,
                message="等待预处理和评估"
            ) 