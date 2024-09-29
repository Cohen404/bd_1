from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base


class User(declarative_base()):
    __tablename__ = 'tb_user'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    pwd = Column(String(255))
    name = Column(String(255))
    user_type = Column(Integer, nullable=False, comment='0/1,0是普通用户，1是管理员')
