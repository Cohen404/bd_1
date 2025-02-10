import os
import sys
import hashlib
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sql_model.base import Base
from sql_model.tb_user import User
from sql_model.tb_data import Data
from sql_model.tb_result import Result
from sql_model.tb_model import Model
from sql_model.tb_parameters import Parameters
from sql_model.system_params import SystemParams
from sql_model.tb_role import Role
from sql_model.tb_permission import Permission
from sql_model.tb_user_role import UserRole
from sql_model.tb_role_permission import RolePermission
from datetime import datetime

# PostgreSQL配置信息
HOST = '127.0.0.1'
PORT = 5432
DATABASE = 'bj_health_db'
USERNAME = 'postgres'
PASSWORD = 'tj654478'

def hash_password(password):
    """使用SHA-256对密码进行哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_database():
    # 创建数据库连接URL
    connection_string = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
    
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
                password=hash_password('123456'),
                email='admin@example.com',
                phone='13800000001',
                user_type='admin',  # 管理员角色ID
                created_at=datetime.now()
            ),
            User(
                user_id='user001',
                username='user1',
                password=hash_password('123456'),
                email='user1@example.com',
                phone='13800000002',
                user_type='user',  # 普通用户角色ID
                created_at=datetime.now()
            ),
            User(
                user_id='user002',
                username='user2',
                password=hash_password('123456'),
                email='user2@example.com',
                phone='13800000003',
                user_type='user',  # 普通用户角色ID
                created_at=datetime.now()
            ),
            User(
                user_id='user003',
                username='user3',
                password=hash_password('123456'),
                email='user3@example.com',
                phone='13800000004',
                user_type='admin',  # 管理员角色ID
                created_at=datetime.now()
            )
        ]
        
        # 添加用户数据
        for user in initial_users:
            session.add(user)
            
        # 添加系统参数
        initial_params = SystemParams(
            param_id='PARAM_001',
            eeg_frequency=500.0,
            electrode_count=64,
            scale_question_num=40,
            model_num=3,
            id=1
        )
        session.add(initial_params)
        
        # 添加初始模型数据
        initial_models = [
            Model(
                id=1,
                model_type=0,
                model_path='./model/yingji/subject-1_yingji_quantized.tflite',
                create_time=datetime.now()
            ),
            Model(
                id=2,
                model_type=1,
                model_path='./model/yiyu/subject-1 yiyu.keras',
                create_time=datetime.now()
            ),
            Model(
                id=3,
                model_type=2,
                model_path='./model/jiaolv/subject-1jiaolv.keras',
                create_time=datetime.now()
            )
        ]
        for model in initial_models:
            session.add(model)

        # 添加角色数据
        initial_roles = [
            Role(
                role_id='admin',
                role_name='管理员',
                description='系统管理员，拥有所有权限',
                created_at=datetime.now()
            ),
            Role(
                role_id='user',
                role_name='普通用户',
                description='普通用户，拥有基本操作权限',
                created_at=datetime.now()
            )
        ]
        for role in initial_roles:
            session.add(role)

        # 添加权限数据
        initial_permissions = [
            Permission(
                permission_id='PERM_USER_MANAGE',
                permission_name='用户管理',
                page_url='/user_manage',
                description='用户管理页面访问权限',
                created_at=datetime.now()
            ),
            Permission(
                permission_id='PERM_ROLE_MANAGE',
                permission_name='角色管理',
                page_url='/role_manage',
                description='角色管理页面访问权限',
                created_at=datetime.now()
            ),
            Permission(
                permission_id='PERM_DATA_MANAGE',
                permission_name='数据管理',
                page_url='/data_manage',
                description='数据管理页面访问权限',
                created_at=datetime.now()
            ),
            Permission(
                permission_id='PERM_MODEL_MANAGE',
                permission_name='模型管理',
                page_url='/model_manage',
                description='模型管理页面访问权限',
                created_at=datetime.now()
            ),
            Permission(
                permission_id='PERM_CHANGE_PWD',
                permission_name='修改密码',
                page_url='/change_pwd',
                description='修改密码页面访问权限',
                created_at=datetime.now()
            ),
            Permission(
                permission_id='PERM_STRESS_ASSESSMENT',
                permission_name='应激评估',
                page_url='/stress_assessment',
                description='应激评估页面访问权限',
                created_at=datetime.now()
            ),
            Permission(
                permission_id='PERM_RESULT_VIEW',
                permission_name='结果查看',
                page_url='/result_view',
                description='结果查看页面访问权限',
                created_at=datetime.now()
            ),
            Permission(
                permission_id='PERM_PARAM_MANAGE',
                permission_name='参数管理',
                page_url='/param_manage',
                description='参数管理页面访问权限',
                created_at=datetime.now()
            ),
            Permission(
                permission_id='PERM_LOG_MANAGE',
                permission_name='日志管理',
                page_url='/log_manage',
                description='日志管理页面访问权限',
                created_at=datetime.now()
            )
        ]
        for permission in initial_permissions:
            session.add(permission)

        # 添加用户角色关联
        initial_user_roles = [
            UserRole(user_id='admin001', role_id='admin'),
            UserRole(user_id='user001', role_id='user'),
            UserRole(user_id='user002', role_id='user'),
            UserRole(user_id='user003', role_id='admin')
        ]
        for user_role in initial_user_roles:
            session.add(user_role)

        # 添加角色权限关联
        initial_role_permissions = [
            # 管理员拥有所有权限
            RolePermission(role_id='admin', permission_id='PERM_USER_MANAGE'),
            RolePermission(role_id='admin', permission_id='PERM_ROLE_MANAGE'),
            RolePermission(role_id='admin', permission_id='PERM_DATA_MANAGE'),
            RolePermission(role_id='admin', permission_id='PERM_MODEL_MANAGE'),
            RolePermission(role_id='admin', permission_id='PERM_CHANGE_PWD'),
            RolePermission(role_id='admin', permission_id='PERM_STRESS_ASSESSMENT'),
            RolePermission(role_id='admin', permission_id='PERM_RESULT_VIEW'),
            RolePermission(role_id='admin', permission_id='PERM_PARAM_MANAGE'),
            RolePermission(role_id='admin', permission_id='PERM_LOG_MANAGE'),
            
            # 普通用户只有基本权限
            RolePermission(role_id='user', permission_id='PERM_STRESS_ASSESSMENT'),
            RolePermission(role_id='user', permission_id='PERM_CHANGE_PWD'),
            RolePermission(role_id='user', permission_id='PERM_RESULT_VIEW'),
            RolePermission(role_id='user', permission_id='PERM_DATA_MANAGE')
        ]
        for role_permission in initial_role_permissions:
            session.add(role_permission)
        
        # 提交更改
        session.commit()
        print("已插入初始数据")
        
        session.close()
        print("数据库初始化完成")
        
    except Exception as e:
        print(f"初始化数据库时出错: {str(e)}")
        raise

if __name__ == '__main__':
    init_database()
