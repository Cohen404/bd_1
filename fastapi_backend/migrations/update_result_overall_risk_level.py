"""
更新数据库中已有结果记录的总体风险等级
运行方式: python -m migrations.update_result_overall_risk_level
"""

from sqlalchemy import text
from database import SessionLocal, engine

def update_result_overall_risk_level():
    """
    更新结果记录的总体风险等级
    """
    db = SessionLocal()
    try:
        # 查询所有没有总体风险等级的结果记录
        update_sql = text("""
            UPDATE tb_result
            SET overall_risk_level = CASE
                WHEN (stress_score + depression_score + anxiety_score + social_isolation_score) / 4 >= 50 THEN '高风险'
                WHEN (stress_score + depression_score + anxiety_score + social_isolation_score) / 4 >= 30 THEN '中等风险'
                ELSE '低风险'
            END
            WHERE overall_risk_level IS NULL OR overall_risk_level = ''
        """)
        
        result = db.execute(update_sql)
        db.commit()
        
        print(f"成功更新 {result.rowcount} 条结果记录的总体风险等级")
        
        # 查询更新后的数据
        check_sql = text("""
            SELECT overall_risk_level, COUNT(*) as count
            FROM tb_result
            GROUP BY overall_risk_level
        """)
        
        check_result = db.execute(check_sql).fetchall()
        print("\n总体风险等级分布:")
        for row in check_result:
            print(f"  {row[0]}: {row[1]} 条")
        
    except Exception as e:
        db.rollback()
        print(f"更新失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_result_overall_risk_level()
