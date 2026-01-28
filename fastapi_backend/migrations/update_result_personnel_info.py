"""
更新数据库中已有结果记录的人员信息
运行方式: python -m migrations.update_result_personnel_info
"""

from sqlalchemy import text
from database import SessionLocal, engine

def update_result_personnel_info():
    """
    更新结果记录的人员信息
    """
    db = SessionLocal()
    try:
        # 查询所有没有人员信息的结果记录
        update_sql = text("""
            UPDATE tb_result r
            SET 
                personnel_id = d.personnel_id,
                personnel_name = d.personnel_name
            FROM tb_data d
            WHERE r.data_id = d.id
            AND (r.personnel_id IS NULL OR r.personnel_name IS NULL)
        """)
        
        result = db.execute(update_sql)
        db.commit()
        
        print(f"成功更新 {result.rowcount} 条结果记录的人员信息")
        
        # 查询更新后的数据
        check_sql = text("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN personnel_id IS NOT NULL THEN 1 ELSE 0 END) as with_personnel
            FROM tb_result
        """)
        
        check_result = db.execute(check_sql).fetchone()
        print(f"总结果数: {check_result[0]}")
        print(f"有人员信息的结果数: {check_result[1]}")
        
    except Exception as e:
        db.rollback()
        print(f"更新失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_result_personnel_info()
