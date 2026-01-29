"""
添加 md5 字段到 tb_data 和 tb_result 表的迁移脚本
运行方式: python -m migrations.add_md5_fields
"""

from sqlalchemy import text
import traceback
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from database import SessionLocal

def add_md5_fields():
    """
    添加 md5 字段到 tb_data 和 tb_result
    """
    db = SessionLocal()
    try:
        check_data_sql = text("""
            SELECT COUNT(*) as count
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = current_database()
            AND TABLE_NAME = 'tb_data'
            AND COLUMN_NAME = 'md5'
        """)
        result = db.execute(check_data_sql).fetchone()
        if result[0] == 0:
            db.execute(text("""
                ALTER TABLE tb_data
                ADD COLUMN md5 VARCHAR(32)
            """))
            db.execute(text("""
                COMMENT ON COLUMN tb_data.md5 IS '文件MD5'
            """))
            print("成功添加字段 md5 到 tb_data 表")
        else:
            print("字段 md5 在 tb_data 已存在，无需添加")

        check_result_sql = text("""
            SELECT COUNT(*) as count
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = current_database()
            AND TABLE_NAME = 'tb_result'
            AND COLUMN_NAME = 'md5'
        """)
        result = db.execute(check_result_sql).fetchone()
        if result[0] == 0:
            db.execute(text("""
                ALTER TABLE tb_result
                ADD COLUMN md5 VARCHAR(32)
            """))
            db.execute(text("""
                COMMENT ON COLUMN tb_result.md5 IS '文件MD5'
            """))
            print("成功添加字段 md5 到 tb_result 表")
        else:
            print("字段 md5 在 tb_result 已存在，无需添加")

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"添加 md5 字段失败: {e}")
        print(traceback.format_exc())
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_md5_fields()

