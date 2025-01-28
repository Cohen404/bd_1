from sqlalchemy import Column, String, ForeignKey
from .base import Base

class RolePermission(Base):
    """角色权限关联表"""
    __tablename__ = 'tb_role_permission'
    
    role_id = Column(String(64), ForeignKey('tb_role.role_id'), primary_key=True, nullable=False, comment='角色ID')
    permission_id = Column(String(64), ForeignKey('tb_permission.permission_id'), primary_key=True, nullable=False, comment='权限ID') 