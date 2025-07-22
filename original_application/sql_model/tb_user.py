from sqlalchemy import Column, String, DateTime
from datetime import datetime
from .base import Base


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
