from sqlalchemy import text

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from database import SessionLocal

db = SessionLocal()
try:
    # 检查血氧字段是否已存在
    check_oxygen_sql = text('''
        SELECT COUNT(*) as count
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = current_database()
        AND TABLE_NAME = 'tb_result'
        AND COLUMN_NAME = 'blood_oxygen'
    ''')
    
    result = db.execute(check_oxygen_sql).fetchone()
    
    if result[0] > 0:
        print('字段 blood_oxygen 已存在，无需添加')
    else:
        # 添加血氧字段
        add_oxygen_sql = text('''
            ALTER TABLE tb_result
                ADD COLUMN blood_oxygen FLOAT
        ''')
        
        db.execute(add_oxygen_sql)
        
        # 添加注释
        add_oxygen_comment_sql = text('''
            COMMENT ON COLUMN tb_result.blood_oxygen IS '血氧饱和度(%)'
        ''')
        
        db.execute(add_oxygen_comment_sql)
        print('成功添加字段 blood_oxygen 到 tb_result 表')
    
    # 检查血压字段是否已存在
    check_pressure_sql = text('''
        SELECT COUNT(*) as count
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = current_database()
        AND TABLE_NAME = 'tb_result'
        AND COLUMN_NAME = 'blood_pressure'
    ''')
    
    result = db.execute(check_pressure_sql).fetchone()
    
    if result[0] > 0:
        print('字段 blood_pressure 已存在，无需添加')
    else:
        # 添加血压字段
        add_pressure_sql = text('''
            ALTER TABLE tb_result
                ADD COLUMN blood_pressure VARCHAR(20)
        ''')
        
        db.execute(add_pressure_sql)
        
        # 添加注释
        add_pressure_comment_sql = text('''
            COMMENT ON COLUMN tb_result.blood_pressure IS '血压(mmHg)，格式：收缩压/舒张压'
        ''')
        
        db.execute(add_pressure_comment_sql)
        print('成功添加字段 blood_pressure 到 tb_result 表')
    
    db.commit()
    print('所有字段添加完成')
    
except Exception as e:
    db.rollback()
    print(f'添加字段失败: {e}')
    raise
finally:
    db.close()
