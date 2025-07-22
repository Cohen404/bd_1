from sqlalchemy import Column, String, ForeignKey
from .base import Base

class UserRole(Base):
    """用户角色关联表"""
    __tablename__ = 'tb_user_role'
    
    user_id = Column(String(64), ForeignKey('tb_user.user_id'), primary_key=True, nullable=False, comment='用户ID')
    role_id = Column(String(64), ForeignKey('tb_role.role_id'), primary_key=True, nullable=False, comment='角色ID') 