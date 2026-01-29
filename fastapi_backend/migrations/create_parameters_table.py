"""
创建 tb_parameters 表的迁移脚本
运行方式: python -m migrations.create_parameters_table
"""

from sqlalchemy import text
from database import SessionLocal, engine

def create_parameters_table():
    """
    创建 tb_parameters 表
    """
    db = SessionLocal()
    try:
        # 检查表是否已存在
        check_table_sql = text("""
            SELECT COUNT(*) as count
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = current_database()
            AND TABLE_NAME = 'tb_parameters'
        """)
        
        result = db.execute(check_table_sql).fetchone()
        
        if result[0] > 0:
            print("表 tb_parameters 已存在，无需创建")
            return
        
        # 创建表
        create_table_sql = text("""
            CREATE TABLE tb_parameters (
                id SERIAL PRIMARY KEY,
                param_name VARCHAR(50) NOT NULL,
                param_value VARCHAR(255) NOT NULL,
                param_type VARCHAR(50) NOT NULL,
                description VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        db.execute(create_table_sql)
        
        # 添加注释
        add_comments_sql = text("""
            COMMENT ON TABLE tb_parameters IS '系统参数表';
            COMMENT ON COLUMN tb_parameters.id IS '主键ID';
            COMMENT ON COLUMN tb_parameters.param_name IS '参数名称';
            COMMENT ON COLUMN tb_parameters.param_value IS '参数值';
            COMMENT ON COLUMN tb_parameters.param_type IS '参数类型';
            COMMENT ON COLUMN tb_parameters.description IS '参数描述';
            COMMENT ON COLUMN tb_parameters.created_at IS '创建时间';
            COMMENT ON COLUMN tb_parameters.updated_at IS '更新时间'
        """)
        
        db.execute(add_comments_sql)
        db.commit()
        
        print("成功创建表 tb_parameters")
        
        # 插入一些默认的系统参数
        insert_defaults_sql = text("""
            INSERT INTO tb_parameters (param_name, param_value, param_type, description) VALUES
            ('max_upload_size', '104857600', 'number', '最大文件上传大小（字节）'),
            ('request_timeout', '30', 'number', 'API请求超时时间（秒）'),
            ('batch_process_limit', '50', 'number', '批量处理数量限制'),
            ('jwt_expire_days', '7', 'number', 'JWT Token过期时间（天）'),
            ('min_password_length', '6', 'number', '密码最小长度'),
            ('login_max_attempts', '5', 'number', '登录失败最大次数'),
            ('account_lock_time', '30', 'number', '账户锁定时间（分钟）'),
            ('high_risk_threshold', '50', 'number', '高风险评估阈值'),
            ('log_retention_days', '30', 'number', '日志保留天数'),
            ('log_max_size', '104857600', 'number', '日志文件最大大小（字节）')
        """)
        
        db.execute(insert_defaults_sql)
        db.commit()
        
        print("成功插入默认系统参数")
        
    except Exception as e:
        db.rollback()
        print(f"创建表失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_parameters_table()
