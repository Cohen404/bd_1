"""
初始化 tb_parameters 表的默认参数
运行方式: python -m migrations.init_parameters_defaults
"""

from sqlalchemy import text
from database import SessionLocal, engine

def init_parameters_defaults():
    """
    初始化系统参数的默认值
    """
    db = SessionLocal()
    try:
        # 检查是否已有数据
        check_data_sql = text("""
            SELECT COUNT(*) as count
            FROM tb_parameters
        """)
        
        result = db.execute(check_data_sql).fetchone()
        
        if result[0] > 0:
            print(f"表 tb_parameters 已有 {result[0]} 条数据，跳过初始化")
            return
        
        # 插入默认的系统参数
        insert_defaults_sql = text("""
            INSERT INTO tb_parameters (param_name, param_value, param_type, description) VALUES
            ('max_upload_size', '104857600', 'number', '最大文件上传大小（字节）'),
            ('request_timeout', '30', 'number', 'API请求超时时间（秒）'),
            ('batch_process_limit', '50', 'number', '批量处理数量限制'),
            ('jwt_expire_days', '7', 'number', 'JWT Token过期时间（天）'),
            ('min_password_length', '6', 'number', '密码最小长度'),
            ('login_max_attempts', '5', 'number', '登录失败最大次数'),
            ('account_lock_time', '30', 'number', '账户锁定时间（分钟）'),
            ('high_risk_threshold', '70', 'number', '高风险评估阈值'),
            ('medium_risk_threshold', '45', 'number', '中等风险评估阈值'),
            ('log_retention_days', '30', 'number', '日志保留天数'),
            ('log_max_size', '104857600', 'number', '日志文件最大大小（字节）')
        """)
        
        db.execute(insert_defaults_sql)
        db.commit()
        
        print("成功插入默认系统参数")
        
        # 查询插入的数据
        check_sql = text("""
            SELECT COUNT(*) as count
            FROM tb_parameters
        """)
        
        check_result = db.execute(check_sql).fetchone()
        print(f"当前共有 {check_result[0]} 条系统参数")
        
    except Exception as e:
        db.rollback()
        print(f"初始化参数失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_parameters_defaults()
