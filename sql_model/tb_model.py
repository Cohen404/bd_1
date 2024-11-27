from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .base import Base


class Model(Base):
    __tablename__ = 'tb_model'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    model_type = Column(Integer, comment='0普通应激模型，1抑郁评估模型，2焦虑评估模型')
    model_path = Column(String(255), comment='模型路径')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
