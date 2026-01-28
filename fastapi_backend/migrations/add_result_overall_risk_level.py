"""
添加 overall_risk_level 字段到 tb_result 表的迁移脚本
运行方式: python -m migrations.add_result_overall_risk_level
"""

from sqlalchemy import text
from database import SessionLocal, engine

def add_result_overall_risk_level_field():
    """
    添加字段到 tb_result 表
    """
    db = SessionLocal()
    try:
        # 检查字段是否已存在
        check_field_sql = text("""
            SELECT COUNT(*) as count
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = current_database()
            AND TABLE_NAME = 'tb_result'
            AND COLUMN_NAME = 'overall_risk_level'
        """)
        
        result = db.execute(check_field_sql).fetchone()
        
        if result[0] > 0:
            print("字段 overall_risk_level 已存在，无需添加")
            return
        
        # 添加字段
        add_field_sql = text("""
            ALTER TABLE tb_result
            ADD COLUMN overall_risk_level VARCHAR(20) DEFAULT '低风险'
        """)
        
        db.execute(add_field_sql)
        
        # 添加注释
        add_comment_sql = text("""
            COMMENT ON COLUMN tb_result.overall_risk_level IS '总体风险等级：低风险/中等风险/高风险'
        """)
        
        db.execute(add_comment_sql)
        db.commit()
        
        print("成功添加字段到 tb_result 表")
        
    except Exception as e:
        db.rollback()
        print(f"添加字段失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_result_overall_risk_level_field()
