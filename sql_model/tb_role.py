from sqlalchemy import Column, String, DateTime
from datetime import datetime
from .base import Base

class Role(Base):
    """角色信息表"""
    __tablename__ = 'tb_role'
    
    role_id = Column(String(64), primary_key=True, nullable=False, comment='角色ID')
    role_name = Column(String(50), nullable=False, comment='角色名称')
    description = Column(String(255), nullable=True, comment='角色描述')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='角色创建时间') 