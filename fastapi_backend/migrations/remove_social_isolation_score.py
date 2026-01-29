"""
删除 tb_result 表中的 social_isolation_score 字段
运行方式: python -m migrations.remove_social_isolation_score
"""

from sqlalchemy import text
import traceback
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from database import SessionLocal

def remove_social_isolation_score():
    """
    删除 tb_result 表的 social_isolation_score 字段
    """
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    db = SessionLocal()
    try:
        list_fields_sql = text("""
            SELECT table_schema, column_name
            FROM information_schema.COLUMNS
            WHERE TABLE_NAME = 'tb_result'
            ORDER BY table_schema, ordinal_position
        """)
        
        columns = db.execute(list_fields_sql).fetchall()
        current_schema = db.execute(text("SELECT current_schema()")).fetchone()[0]
        current_db = db.execute(text("SELECT current_database()")).fetchone()[0]
        column_names = [f"{row[0]}.{row[1]}" for row in columns]
        print("tb_result 当前字段：")
        print(f"当前数据库: {current_db}, 当前Schema: {current_schema}")
        print("|".join(column_names))
        try:
            with open("tb_result_columns.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(column_names))
        except Exception as e:
            print(f"写入字段列表文件失败: {e}")

        check_field_sql = text("""
            SELECT COUNT(*) as count
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = current_schema()
            AND TABLE_NAME = 'tb_result'
            AND COLUMN_NAME = 'social_isolation_score'
        """)
        
        result = db.execute(check_field_sql).fetchone()
        
        if result[0] == 0:
            print("字段 social_isolation_score 不存在，无需删除")
            return
        
        drop_field_sql = text("""
            ALTER TABLE tb_result
            DROP COLUMN social_isolation_score
        """)
        
        db.execute(drop_field_sql)
        db.commit()
        print("成功删除字段 social_isolation_score")
        
    except Exception as e:
        db.rollback()
        print(f"删除字段失败: {e}")
        print(traceback.format_exc())
        raise
    finally:
        db.close()

if __name__ == "__main__":
    remove_social_isolation_score()

