from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import os
from datetime import datetime, timedelta
import pandas as pd
import io
import zipfile
from pathlib import Path
import base64

from database import get_db
import models as db_models
import schemas
from auth import get_current_user, check_admin_permission
from model_inference import ResultProcessor
from config import RESULTS_DIR

router = APIRouter()

IMAGES_DIR = Path(__file__).resolve().parents[1] / "images"
MD5_DIR = Path(__file__).resolve().parents[1] / "md5"
MD5_MAPPING_FILE = MD5_DIR / "data.txt"

def load_md5_mapping():
    """
    读取MD5映射文件，返回 md5 -> (file_id, stress, depression, anxiety)
    file_id是文件名第一个_前的id（如"2_yky.zip"中的"2"）
    """
    MD5_DIR.mkdir(parents=True, exist_ok=True)
    if not MD5_MAPPING_FILE.exists():
        MD5_MAPPING_FILE.write_text("", encoding="utf-8")
    
    mapping = {}
    try:
        lines = MD5_MAPPING_FILE.read_text(encoding="utf-8").splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) != 5:
                continue
            md5_value = parts[0]
            file_id = parts[1]
            try:
                scores = (float(parts[2]), float(parts[3]), float(parts[4]))
                mapping[md5_value] = (file_id, scores[0], scores[1], scores[2])
            except ValueError:
                continue
    except Exception as e:
        logging.error(f"读取MD5映射文件失败: {str(e)}")
    return mapping

def get_image_for_md5(md5_value: str) -> Optional[str]:
    """
    根据MD5值获取对应的图片（base64编码）
    直接使用file_id匹配图片，如file_id为"2"则匹配"2.jpg"
    """
    try:
        mapping = load_md5_mapping()
        
        # 查找该MD5对应的file_id
        file_id = None
        if md5_value in mapping:
            file_id = mapping[md5_value][0]
        
        if not file_id:
            return None
        
        # 直接使用file_id匹配图片
        image_path = IMAGES_DIR / f"{file_id}.jpg"
        
        if not image_path.exists():
            return None
        
        # 读取图片并转换为base64
        with open(image_path, "rb") as f:
            image_data = f.read()
            return base64.b64encode(image_data).decode('utf-8')
        
    except Exception as e:
        logging.error(f"获取用户图片失败: {str(e)}")
        return None

def get_image_for_file_id(file_id: str) -> Optional[str]:
    """
    根据file_id直接获取对应的图片（base64编码）
    用于旧数据（没有md5）的情况
    """
    try:
        # 直接使用file_id匹配图片
        image_path = IMAGES_DIR / f"{file_id}.jpg"
        
        if not image_path.exists():
            return None
        
        # 读取图片并转换为base64
        with open(image_path, "rb") as f:
            image_data = f.read()
            return base64.b64encode(image_data).decode('utf-8')
        
    except Exception as e:
        logging.error(f"获取用户图片失败: {str(e)}")
        return None

@router.get("/", response_model=List[schemas.Result])
async def read_results(
    skip: int = 0,
    limit: int = 100,
    data_id: Optional[int] = None,
    user_id: Optional[str] = None,
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    min_stress_score: Optional[float] = Query(None, description="最小应激分数"),
    max_stress_score: Optional[float] = Query(None, description="最大应激分数"),
    min_depression_score: Optional[float] = Query(None, description="最小抑郁分数"),
    max_depression_score: Optional[float] = Query(None, description="最大抑郁分数"),
    # current_user = Depends(get_current_user),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    获取结果列表（支持高级过滤）
    """
    query = db.query(db_models.Result).join(
        db_models.Data,
        db_models.Result.data_id == db_models.Data.id
    ).filter(db_models.Data.has_result == True)
    
    # 认证已移除，返回所有结果
    
    # 根据参数过滤
    if data_id:
        query = query.filter(db_models.Result.data_id == data_id)
    
    if user_id:
        query = query.filter(db_models.Result.user_id == user_id)
    
    # 日期范围过滤
    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(db_models.Result.result_time >= start_datetime)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的开始日期格式，请使用 YYYY-MM-DD"
            )
    
    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(db_models.Result.result_time < end_datetime)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的结束日期格式，请使用 YYYY-MM-DD"
            )
    
    # 分数范围过滤
    if min_stress_score is not None:
        query = query.filter(db_models.Result.stress_score >= min_stress_score)
    if max_stress_score is not None:
        query = query.filter(db_models.Result.stress_score <= max_stress_score)
    if min_depression_score is not None:
        query = query.filter(db_models.Result.depression_score >= min_depression_score)
    if max_depression_score is not None:
        query = query.filter(db_models.Result.depression_score <= max_depression_score)
    
    # 分页并获取结果
    results = query.order_by(db_models.Result.result_time.desc()).offset(skip).limit(limit).all()
    
    # 为每个结果补充人员信息
    for result in results:
        if not result.personnel_id or not result.personnel_name:
            # 从关联的Data表获取人员信息
            if result.data_id:
                data = db.query(db_models.Data).filter(db_models.Data.id == result.data_id).first()
                if data:
                    result.personnel_id = data.personnel_id
                    result.personnel_name = data.personnel_name
    
    return results

@router.get("/{result_id}", response_model=schemas.Result)
async def read_result(
    result_id: int,
    # current_user = Depends(get_current_user),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    获取特定结果
    """
    result = db.query(db_models.Result).filter(db_models.Result.id == result_id).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID为{result_id}的结果不存在"
        )
    
    # 补充人员信息
    if not result.personnel_id or not result.personnel_name:
        if result.data_id:
            data = db.query(db_models.Data).filter(db_models.Data.id == result.data_id).first()
            if data:
                result.personnel_id = data.personnel_id
                result.personnel_name = data.personnel_name
    
    return result

@router.delete("/{result_id}")
async def delete_result(
    result_id: int,
    # # current_user = Depends(check_admin_permission),  # 认证已移除  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    删除特定结果（仅管理员）
    """
    result = db.query(db_models.Result).filter(db_models.Result.id == result_id).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID为{result_id}的结果不存在"
        )
    
    # 删除报告文件
    if result.report_path and os.path.exists(result.report_path):
        try:
            os.remove(result.report_path)
        except Exception as e:
            logging.warning(f"删除报告文件失败: {str(e)}")
    
    # 删除数据库记录
    db.delete(result)
    db.commit()
    
    return {"message": f"结果ID {result_id} 删除成功"}

@router.put("/{result_id}")
async def update_result(
    result_id: int,
    blood_oxygen: Optional[float] = None,
    blood_pressure: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    更新结果（血氧、血压等）
    """
    result = db.query(db_models.Result).filter(db_models.Result.id == result_id).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID为{result_id}的结果不存在"
        )
    
    # 更新字段
    if blood_oxygen is not None:
        result.blood_oxygen = blood_oxygen
    
    if blood_pressure is not None:
        result.blood_pressure = blood_pressure
    
    db.commit()
    db.refresh(result)
    
    return result

@router.post("/export")
async def export_results(
    request: schemas.ResultExportRequest,
    # current_user = Depends(get_current_user),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    导出结果数据
    """
    # 查询要导出的结果
    results = db.query(db_models.Result).filter(db_models.Result.id.in_(request.result_ids)).all()
    
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="没有找到要导出的结果"
        )
    
    # 准备导出数据
    export_data = []
    for result in results:
        # 获取关联的数据信息
        data = db.query(db_models.Data).filter(db_models.Data.id == result.data_id).first()
        user = db.query(db_models.User).filter(db_models.User.user_id == result.user_id).first()
        
        export_data.append({
            "结果ID": result.id,
            "数据ID": result.data_id,
            "人员ID": data.personnel_id if data else result.personnel_id,
            "人员姓名": data.personnel_name if data else result.personnel_name,
            "评估用户": user.username if user else "",
            "应激评分": result.stress_score,
            "抑郁评分": result.depression_score,
            "焦虑评分": result.anxiety_score,
            "评估时间": result.result_time.strftime("%Y-%m-%d %H:%M:%S"),
            "报告路径": result.report_path or "",
            "主动学习": "是" if result.active_learned else "否"
        })
    
    # 根据导出格式处理
    if request.export_format.lower() == "excel":
        # 导出为Excel
        df = pd.DataFrame(export_data)
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='评估结果', index=False)
        
        output.seek(0)
        filename = f"评估结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return Response(
            content=output.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    elif request.export_format.lower() == "csv":
        # 导出为CSV
        df = pd.DataFrame(export_data)
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        
        filename = f"评估结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return Response(
            content=output.getvalue().encode('utf-8-sig'),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    elif request.export_format.lower() == "pdf":
        # 导出为PDF报告包
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="没有找到PDF报告"
            )
        
        # 创建ZIP文件包含所有PDF报告
        output = io.BytesIO()
        
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for result in results:
                if result.report_path and os.path.exists(result.report_path):
                    # 生成更清晰的文件名
                    data = db.query(db_models.Data).filter(db_models.Data.id == result.data_id).first()
                    pdf_filename = f"评估报告_ID{result.id}_{data.personnel_name if data else 'Unknown'}_{result.result_time.strftime('%Y%m%d_%H%M%S')}.pdf"
                    zipf.write(result.report_path, pdf_filename)
        
        output.seek(0)
        filename = f"评估报告包_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        return Response(
            content=output.getvalue(),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的导出格式: {request.export_format}"
        )

@router.get("/report/{result_id}")
async def view_report(
    result_id: int,
    # current_user = Depends(get_current_user),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    查看PDF报告
    """
    from fastapi.responses import FileResponse
    
    result = db.query(db_models.Result).filter(db_models.Result.id == result_id).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID为{result_id}的结果不存在"
        )
    
    if not result.report_path or not os.path.exists(result.report_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告文件不存在"
        )
    
    return FileResponse(
        path=result.report_path,
        media_type="application/pdf",
        filename=f"评估报告_ID{result_id}.pdf"
    )

@router.get("/summary/statistics")
async def get_result_statistics(
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    # current_user = Depends(get_current_user),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    获取结果统计信息
    """
    query = db.query(db_models.Result)
    
    # 日期范围过滤
    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(db_models.Result.result_time >= start_datetime)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的开始日期格式"
            )
        
    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(db_models.Result.result_time < end_datetime)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的结束日期格式"
            )
        
    results = query.all()
    
    if not results:
        return {
            "total_count": 0,
            "avg_stress_score": 0,
            "avg_depression_score": 0,
            "avg_anxiety_score": 0,
            "high_risk_count": 0,
            "recent_count": 0
        }
    
    # 计算统计信息
    total_count = len(results)
    avg_stress = sum(r.stress_score for r in results) / total_count
    avg_depression = sum(r.depression_score for r in results) / total_count
    avg_anxiety = sum(r.anxiety_score for r in results) / total_count
    
    # 高风险计数（任一分数>=50）
    high_risk_count = sum(1 for r in results if any([
        r.stress_score >= 50,
        r.depression_score >= 50,
        r.anxiety_score >= 50
    ]))
    
    # 最近7天的评估数量
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_count = sum(1 for r in results if r.result_time >= seven_days_ago)
    
    return {
        "total_count": total_count,
        "avg_stress_score": round(avg_stress, 2),
        "avg_depression_score": round(avg_depression, 2),
        "avg_anxiety_score": round(avg_anxiety, 2),
        "high_risk_count": high_risk_count,
        "high_risk_percentage": round((high_risk_count / total_count) * 100, 2),
        "recent_count": recent_count
    }

@router.get("/users/list")
async def get_result_users(
    # current_user = Depends(check_admin_permission),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    获取有评估结果的用户列表（仅管理员）
    """
    # 查询有结果的用户
    users_with_results = db.query(db_models.User).join(
        db_models.Result, db_models.User.user_id == db_models.Result.user_id
    ).distinct().all()
    
    return [
        {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "user_type": user.user_type
        }
        for user in users_with_results
    ]

@router.post("/regenerate-report/{result_id}")
async def regenerate_report(
    result_id: int,
    # current_user = Depends(get_current_user),  # 认证已移除
    db: Session = Depends(get_db)
):
    """
    重新生成评估报告
    """
    result = db.query(db_models.Result).filter(db_models.Result.id == result_id).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID为{result_id}的结果不存在"
        )
    
    # 获取关联的数据
    data = db.query(db_models.Data).filter(db_models.Data.id == result.data_id).first()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关联的数据不存在"
        )
    
    try:
        # 重新生成报告
        scores = {
            'stress_score': result.stress_score,
            'depression_score': result.depression_score,
            'anxiety_score': result.anxiety_score
        }
        
        result_processor = ResultProcessor(data.data_path, scores)
        new_report_path = result_processor.generate_report()
        
        # 删除旧报告文件
        if result.report_path and os.path.exists(result.report_path):
            try:
                os.remove(result.report_path)
            except Exception as e:
                logging.warning(f"删除旧报告文件失败: {str(e)}")
        
        # 更新报告路径
        result.report_path = new_report_path
        db.commit()
        
        logging.info(f"重新生成了结果ID {result_id} 的报告")
        
        return {"message": "报告重新生成成功", "report_path": new_report_path}
        
    except Exception as e:
        logging.error(f"重新生成报告失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重新生成报告失败: {str(e)}"
        )

@router.get("/user-image/{result_id}")
async def get_user_image(
    result_id: int,
    db: Session = Depends(get_db)
):
    """
    根据结果ID获取用户对应的图片
    """
    result = db.query(db_models.Result).filter(db_models.Result.id == result_id).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID为{result_id}的结果不存在"
        )
    
    # 直接使用result_id匹配图片
    image_base64 = get_image_for_file_id(str(result_id))
    
    if not image_base64:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到对应的图片"
        )
    
    return {"image": f"data:image/jpeg;base64,{image_base64}"} 