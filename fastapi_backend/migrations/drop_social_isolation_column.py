#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迁移脚本：删除tb_result表中的social_isolation_score列
因为前端已经不再使用社交孤立评估功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from database import engine, SessionLocal
from sqlalchemy import text

def drop_social_isolation_column():
    """
    删除tb_result表中的social_isolation_score列
    """
    session = SessionLocal()
    
    try:
        # 检查列是否存在
        check_column_sql = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'tb_result' 
            AND column_name = 'social_isolation_score'
        """)
        
        result = session.execute(check_column_sql).fetchone()
        
        if result and result[0]:
            print("发现social_isolation_score列，准备删除...")
            
            # 删除列
            drop_column_sql = text("ALTER TABLE tb_result DROP COLUMN IF EXISTS social_isolation_score")
            session.execute(drop_column_sql)
            session.commit()
            
            print("✓ 成功删除social_isolation_score列")
        else:
            print("social_isolation_score列不存在，无需删除")
    
    except Exception as e:
        print(f"✗ 删除列时出错: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == '__main__':
    print("开始迁移：删除social_isolation_score列")
    print("=" * 50)
    drop_social_isolation_column()
    print("=" * 50)
    print("迁移完成")
