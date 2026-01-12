from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import logging
from datetime import datetime, timedelta
import re

from database import get_db
import schemas
# from auth import check_admin_permission  # 认证已移除
from config import LOG_FILE

router = APIRouter()

@router.get("/")
async def read_logs(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    username: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = 1000,
    # current_user = Depends(check_admin_permission)  # 认证已移除
):
    """
    获取日志列表
    """
    # 检查日志文件是否存在
    if not os.path.exists(LOG_FILE):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日志文件不存在"
        )
    
    # 解析日期参数
    start_datetime = None
    end_datetime = None
    
    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="开始日期格式无效，应为YYYY-MM-DD"
            )
    
    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
            # 将结束日期设置为当天的23:59:59
            end_datetime = end_datetime + timedelta(days=1, microseconds=-1)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="结束日期格式无效，应为YYYY-MM-DD"
            )
    
    # 日志级别
    valid_levels = ["INFO", "WARNING", "ERROR", "DEBUG", "CRITICAL"]
    if level and level.upper() not in valid_levels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"日志级别无效，应为以下之一: {', '.join(valid_levels)}"
        )
    
    # 读取日志文件
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        logs = f.readlines()
    
    # 日志正则表达式匹配模式
    log_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:,\d{3})?) - (\w+(?:\.\w+)*) - (\w+) - ([^-]+) - (.*)"
    
    # 过滤日志
    filtered_logs = []
    for log in logs:
        match = re.match(log_pattern, log)
        if match:
            log_datetime_str, log_module, log_level, log_username, log_message = match.groups()
            
            try:
                # 处理时间戳，兼容有无毫秒的情况
                if ',' in log_datetime_str:
                    log_datetime = datetime.strptime(log_datetime_str, "%Y-%m-%d %H:%M:%S,%f")
                else:
                    log_datetime = datetime.strptime(log_datetime_str, "%Y-%m-%d %H:%M:%S")
                
                # 根据条件过滤
                if start_datetime and log_datetime < start_datetime:
                    continue
                
                if end_datetime and log_datetime > end_datetime:
                    continue
                
                if level and log_level.upper() != level.upper():
                    continue
                
                if username and username.lower() not in log_username.lower():
                    continue
                
                # 构建日志条目
                log_entry = {
                    "timestamp": log_datetime_str,
                    "level": log_level,
                    "username": log_username.strip(),
                    "message": log_message.strip()
                }
                
                filtered_logs.append(log_entry)
            except ValueError:
                # 日期解析错误，跳过该日志条目
                continue
    
    # 按照时间倒序排序
    filtered_logs.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # 限制返回数量
    return filtered_logs[:limit] 