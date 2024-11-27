import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sql_model.base import Base
from sql_model.tb_user import User
from sql_model.tb_data import Data
from sql_model.tb_result import Result
from sql_model.tb_model import Model
from sql_model.tb_parameters import Parameters
from datetime import datetime

# MySQL配置信息
HOST = '127.0.0.1'
PORT = 3306
DATABASE = 'sql_model'
USERNAME = 'root'
PASSWORD = 'root'

def init_database():
    # 创建数据库连接URL
    connection_string = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
    
    try:
        # 创建引擎
        engine = create_engine(connection_string)
        
        # 删除所有现有表
        Base.metadata.drop_all(engine)
        print("已删除所有现有表")
        
        # 创建所有表
        Base.metadata.create_all(engine)
        print("已创建新表")
        
        # 创建会话
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # 插入初始用户数据
        initial_users = [
            User(
                user_id='admin001',
                username='admin',
                password='123',
                email='admin@example.com',
                phone='13800000001',
                full_name='管理员',
                user_type='admin',
                created_at=datetime.now()
            ),
            User(
                user_id='user001',
                username='123',
                password='1234',
                email='user1@example.com',
                phone='13800000002',
                full_name='测试用户1',
                user_type='user',
                created_at=datetime.now()
            ),
            User(
                user_id='user002',
                username='111',
                password='111',
                email='user2@example.com',
                phone='13800000003',
                full_name='测试用户2',
                user_type='user',
                created_at=datetime.now()
            ),
            User(
                user_id='user003',
                username='222',
                password='222',
                email='user3@example.com',
                phone='13800000004',
                full_name='测试用户3',
                user_type='admin',
                created_at=datetime.now()
            )
        ]
        
        # 添加用户数据
        for user in initial_users:
            session.add(user)
        
        # 提交更改
        session.commit()
        print("已插入初始用户数据")
        
        session.close()
        print("数据库初始化完成")
        
    except Exception as e:
        print(f"初始化数据库时出错: {str(e)}")
        raise

if __name__ == '__main__':
    init_database()
