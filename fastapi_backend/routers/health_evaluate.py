from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
import os
import logging
from typing import List
import asyncio

from database import get_db
import models as db_models
import schemas
from auth import get_current_user, check_permission
from model_inference import EegModel, BatchInferenceModel, ResultProcessor
from data_preprocess import treat
from data_feature_calculation import analyze_eeg_data, plot_serum_data, plot_scale_data

router = APIRouter()

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
    
    # 分析EEG数据，生成特征和可视化
    try:
        fif_path = os.path.join(data_path, [f for f in os.listdir(data_path) if f.endswith('.fif')][0])
        result = analyze_eeg_data(fif_path)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="EEG数据分析失败"
            )
    except Exception as e:
        logging.error(f"EEG数据分析错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"EEG数据分析错误: {str(e)}"
        )
    
    # 绘制血清和量表数据的可视化图表
    try:
        plot_serum_data(data_path)
        plot_scale_data(data_path)
    except Exception as e:
        logging.warning(f"绘制血清或量表数据图表时出错: {str(e)}")
    
    # 加载模型并进行预测
    try:
        # 加载各类型模型
        for model_type in range(4):  # 0=应激, 1=抑郁, 2=焦虑, 3=社交孤立
            await EegModel.load_static_model(model_type, db)
        
        # 获取各模型的路径
        model_paths = {}
        for model_type in range(4):
            model_info = db.query(db_models.Model).filter(db_models.Model.model_type == model_type).first()
            if model_info:
                model_paths[model_type] = model_info.model_path
        
        # 存储各模型的预测结果
        scores = {
            "stress": 0.0,
            "depression": 0.0,
            "anxiety": 0.0,
            "social_isolation": 0.0
        }
        
        # 并行运行所有模型预测
        tasks = []
        for model_type, model_path in model_paths.items():
            model = EegModel(data_path, model_path)
            tasks.append(model.predict(model_type))
        
        # 等待所有任务完成
        scores_list = await asyncio.gather(*tasks)
        
        # 将结果赋值给相应的分数
        for i, model_type in enumerate(model_paths.keys()):
            if model_type == 0:
                scores["stress"] = scores_list[i] * 100
            elif model_type == 1:
                scores["depression"] = scores_list[i] * 100
            elif model_type == 2:
                scores["anxiety"] = scores_list[i] * 100
            elif model_type == 3:
                scores["social_isolation"] = scores_list[i] * 100
        
        # 创建结果记录
        result = db_models.Result(
            stress_score=scores["stress"],
            depression_score=scores["depression"],
            anxiety_score=scores["anxiety"],
            social_isolation_score=scores["social_isolation"],
            user_id=current_user.user_id,
            data_id=request.data_id
        )
        
        db.add(result)
        db.commit()
        db.refresh(result)
        
        # 生成报告
        result_processor = ResultProcessor(result.id, db)
        report_path = await result_processor.generate_report()
        
        if report_path:
            # 更新报告路径
            result.report_path = report_path
            db.commit()
        
        return result
    
    except Exception as e:
        logging.error(f"健康评估错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"健康评估错误: {str(e)}"
        )

@router.post("/batch-evaluate", response_model=List[schemas.Result])
async def batch_evaluate_health(
    request: schemas.BatchHealthEvaluateRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(check_permission("health", "evaluate")),
    db: Session = Depends(get_db)
):
    """
    批量健康评估
    """
    # 查询数据
    data_list = db.query(db_models.Data).filter(db_models.Data.id.in_(request.data_ids)).all()
    if not data_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="请求的数据不存在"
        )
    
    # 准备数据路径列表
    data_paths = [(data.id, data.data_path) for data in data_list]
    
    # 初始化批量推理模型
    batch_model = BatchInferenceModel()
    
    # 异步处理批量预测
    try:
        # 加载模型
        success = await batch_model.load_models(db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="加载模型失败"
            )
        
        # 启动批量预测任务
        background_tasks.add_task(batch_model.batch_predict, data_paths, db)
        
        # 返回已经存在的结果
        existing_results = db.query(db_models.Result).filter(
            db_models.Result.data_id.in_(request.data_ids)
        ).all()
        
        return existing_results
    
    except Exception as e:
        logging.error(f"批量健康评估错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量健康评估错误: {str(e)}"
        )

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