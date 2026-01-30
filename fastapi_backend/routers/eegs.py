from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from typing import List
import pandas as pd
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/eegs", tags=["EEG数据"])

EEGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "eegs")
EXCEL_FILE = os.path.join(EEGS_DIR, "采集记录.xlsx")
RECORDINGS_DIR = os.path.join(EEGS_DIR, "Recordings")


@router.get("/excel")
async def get_excel_data():
    """
    读取采集记录.xlsx文件，返回所有记录
    """
    try:
        if not os.path.exists(EXCEL_FILE):
            raise HTTPException(
                status_code=404,
                detail="采集记录.xlsx文件不存在"
            )
        
        df = pd.read_excel(EXCEL_FILE)
        
        records = []
        for _, row in df.iterrows():
            record = {
                "序号": int(row.get("序号", 0)),
                "脑电采集时间": str(row.get("脑电采集时间", "")),
                "文件名": str(row.get("脑电采集时间", ""))
            }
            records.append(record)
        
        return records
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"读取Excel文件失败: {str(e)}"
        )


@router.get("/txt")
async def get_txt_file(filename: str):
    """
    读取指定的txt文件内容
    """
    try:
        logger.info(f"请求读取文件: {filename}")
        
        if not filename:
            raise HTTPException(
                status_code=400,
                detail="文件名不能为空"
            )
        
        logger.info(f"搜索目录: {RECORDINGS_DIR}")
        txt_path = None
        
        for root, dirs, files in os.walk(RECORDINGS_DIR):
            logger.info(f"检查目录: {root}, 文件数: {len(files)}")
            for file in files:
                if file == filename or file == f"{filename}.txt":
                    txt_path = os.path.join(root, file)
                    logger.info(f"找到文件: {txt_path}")
                    break
            if txt_path:
                break
        
        if not txt_path:
            raise HTTPException(
                status_code=404,
                detail=f"未找到文件: {filename} (在目录: {RECORDINGS_DIR})"
            )
        
        logger.info(f"开始读取文件: {txt_path}")
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"文件读取成功，内容长度: {len(content)}")
        return content
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"读取txt文件失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"读取txt文件失败: {str(e)}"
        )