from sqlalchemy import Column, String, DateTime
from datetime import datetime
from .base import Base


class User(Base):
    __tablename__ = 'tb_user'
    user_id = Column(String(64), primary_key=True, nullable=False)
    username = Column(String(50), nullable=False)
    password = Column(String(64), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    full_name = Column(String(255), nullable=True)
    user_type = Column(String(10), nullable=False, default='user')
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)
