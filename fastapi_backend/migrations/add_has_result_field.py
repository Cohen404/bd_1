"""
添加 has_result 字段到 tb_data 表的迁移脚本
运行方式: python -m migrations.add_has_result_field
"""

from sqlalchemy import text
from database import SessionLocal, engine

def add_has_result_field():
    """
    添加 has_result 字段到 tb_data 表
    """
    db = SessionLocal()
    try:
        # 检查字段是否已存在
        check_field_sql = text("""
            SELECT COUNT(*) as count
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = current_database()
            AND TABLE_NAME = 'tb_data'
            AND COLUMN_NAME = 'has_result'
        """)
        
        result = db.execute(check_field_sql).fetchone()
        
        if result[0] > 0:
            print("字段 has_result 已存在，无需添加")
            return
        
        # 添加字段
        add_field_sql = text("""
            ALTER TABLE tb_data
            ADD COLUMN has_result BOOLEAN DEFAULT FALSE
        """)
        
        db.execute(add_field_sql)
        
        # 添加注释
        add_comment_sql = text("""
            COMMENT ON COLUMN tb_data.has_result IS '是否有评估结果'
        """)
        
        db.execute(add_comment_sql)
        db.commit()
        
        print("成功添加 has_result 字段到 tb_data 表")
        
    except Exception as e:
        db.rollback()
        print(f"添加字段失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_has_result_field()
