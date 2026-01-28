from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    """用户表模型类"""
    __tablename__ = 'tb_user'
    
    user_id = Column(String(64), primary_key=True, nullable=False, comment='用户ID')
    username = Column(String(50), nullable=False, unique=True, comment='用户名')
    password = Column(String(64), nullable=False, comment='密码')
    email = Column(String(100), nullable=True, comment='邮箱')
    phone = Column(String(20), nullable=True, comment='电话')
    user_type = Column(String(10), nullable=False, default='user', comment='用户类型: admin/user')
    last_login = Column(DateTime, nullable=True, comment='最后登录时间')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    roles = relationship("UserRole", back_populates="user")
    data = relationship("Data", back_populates="user")
    results = relationship("Result", back_populates="user")

class Role(Base):
    """角色表模型类"""
    __tablename__ = 'tb_role'
    
    role_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    role_name = Column(String(50), nullable=False, unique=True, comment='角色名称')
    description = Column(String(255), nullable=True, comment='角色描述')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    
    # 关系
    users = relationship("UserRole", back_populates="role")
    permissions = relationship("RolePermission", back_populates="role")

class UserRole(Base):
    """用户角色关联表模型类"""
    __tablename__ = 'tb_user_role'
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(String(64), ForeignKey('tb_user.user_id'), nullable=False)
    role_id = Column(Integer, ForeignKey('tb_role.role_id'), nullable=False)
    
    # 关系
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")

class Permission(Base):
    """权限表模型类"""
    __tablename__ = 'tb_permission'
    
    permission_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    permission_name = Column(String(50), nullable=False, unique=True, comment='权限名称')
    description = Column(String(255), nullable=True, comment='权限描述')
    resource = Column(String(50), nullable=False, comment='资源')
    action = Column(String(50), nullable=False, comment='操作')
    
    # 关系
    roles = relationship("RolePermission", back_populates="permission")

class RolePermission(Base):
    """角色权限关联表模型类"""
    __tablename__ = 'tb_role_permission'
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    role_id = Column(Integer, ForeignKey('tb_role.role_id'), nullable=False)
    permission_id = Column(Integer, ForeignKey('tb_permission.permission_id'), nullable=False)
    
    # 关系
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")

class Data(Base):
    """数据表模型类"""
    __tablename__ = 'tb_data'
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    personnel_id = Column(String(64), nullable=False, comment='人员id')
    data_path = Column(String(255), comment='文件路径')
    upload_user = Column(Integer, nullable=False, comment='0/1,0是普通用户，1是管理员')
    personnel_name = Column(String(255), nullable=False, comment='人员姓名')
    user_id = Column(String(64), ForeignKey('tb_user.user_id'), nullable=False, comment='关联用户ID')
    upload_time = Column(DateTime, default=datetime.now, comment='上传时间')
    processing_status = Column(String(20), nullable=False, default='pending', comment='预处理状态: pending/processing/completed/failed')
    feature_status = Column(String(20), nullable=False, default='pending', comment='特征提取状态: pending/processing/completed/failed')
    has_result = Column(Boolean, default=False, comment='是否有评估结果')
    active_learned = Column(Boolean, default=False, comment='是否进行过主动学习')
    
    # 关系
    user = relationship("User", back_populates="data")
    results = relationship("Result", back_populates="data")

class Result(Base):
    """结果表模型类"""
    __tablename__ = 'tb_result'
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    result_time = Column(DateTime, default=datetime.now, comment='结果计算时间')
    stress_score = Column(Float, nullable=False, comment='0-100,0不普通应激，100普通应激')
    depression_score = Column(Float, nullable=False, comment='0-100,0不抑郁，100抑郁')
    anxiety_score = Column(Float, nullable=False, comment='0-100,0不焦虑，100焦虑')
    social_isolation_score = Column(Float, nullable=False, comment='0-100,0不社交孤立，100社交孤立')
    report_path = Column(String(255), nullable=True, comment='报告路径')
    user_id = Column(String(64), ForeignKey('tb_user.user_id'), nullable=False, comment='关联用户ID')
    data_id = Column(Integer, ForeignKey('tb_data.id'), nullable=True, comment='关联数据ID')
    personnel_id = Column(String(64), nullable=True, comment='人员ID')
    personnel_name = Column(String(255), nullable=True, comment='人员姓名')
    active_learned = Column(Boolean, default=False, comment='是否进行过主动学习')
    overall_risk_level = Column(String(20), nullable=True, default='低风险', comment='总体风险等级：低风险/中等风险/高风险')
    
    # 关系
    user = relationship("User", back_populates="results")
    data = relationship("Data", back_populates="results")

class Model(Base):
    """模型表模型类"""
    __tablename__ = 'tb_model'
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    model_type = Column(Integer, comment='0普通应激模型，1抑郁评估模型，2焦虑评估模型，3社交孤立评估模型')
    model_path = Column(String(255), comment='模型路径')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')

class SystemParams(Base):
    """系统参数表模型类"""
    __tablename__ = 'system_params'
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    param_name = Column(String(50), nullable=False, unique=True, comment='参数名称')
    param_value = Column(String(255), nullable=False, comment='参数值')
    description = Column(String(255), nullable=True, comment='参数描述')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

class Parameters(Base):
    """参数表模型类"""
    __tablename__ = 'tb_parameters'
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    param_name = Column(String(50), nullable=False, comment='参数名称')
    param_value = Column(String(255), nullable=False, comment='参数值')
    param_type = Column(String(50), nullable=False, comment='参数类型')
    description = Column(String(255), nullable=True, comment='参数描述')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间') 