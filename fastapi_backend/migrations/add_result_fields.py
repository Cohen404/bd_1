"""
添加 personnel_id, personnel_name, active_learned 字段到 tb_result 表的迁移脚本
运行方式: python -m migrations.add_result_fields
"""

from sqlalchemy import text
from database import SessionLocal, engine

def add_result_fields():
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
            AND COLUMN_NAME = 'personnel_id'
        """)
        
        result = db.execute(check_field_sql).fetchone()
        
        if result[0] > 0:
            print("字段 personnel_id 已存在，无需添加")
            return
        
        # 添加字段
        add_fields_sql = text("""
            ALTER TABLE tb_result
            ADD COLUMN personnel_id VARCHAR(64),
            ADD COLUMN personnel_name VARCHAR(255),
            ADD COLUMN active_learned BOOLEAN DEFAULT FALSE
        """)
        
        db.execute(add_fields_sql)
        
        # 添加注释
        add_comments_sql = text("""
            COMMENT ON COLUMN tb_result.personnel_id IS '人员ID';
            COMMENT ON COLUMN tb_result.personnel_name IS '人员姓名';
            COMMENT ON COLUMN tb_result.active_learned IS '是否进行过主动学习'
        """)
        
        db.execute(add_comments_sql)
        db.commit()
        
        print("成功添加字段到 tb_result 表")
        
    except Exception as e:
        db.rollback()
        print(f"添加字段失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_result_fields()
