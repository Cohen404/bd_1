from sqlalchemy import Column, String, DateTime
from datetime import datetime
from .base import Base

class Permission(Base):
    """权限表"""
    __tablename__ = 'tb_permission'
    
    permission_id = Column(String(64), primary_key=True, nullable=False, comment='权限ID')
    permission_name = Column(String(100), nullable=False, comment='权限名称')
    page_url = Column(String(255), nullable=False, comment='访问的页面URL')
    description = Column(String(255), nullable=True, comment='权限描述')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='权限创建时间') 