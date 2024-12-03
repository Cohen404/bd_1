from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .base import Base


class Result(Base):
    __tablename__ = 'tb_result'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    result_time = Column(DateTime, default=datetime.now, comment='结果计算时间')
    result_1 = Column(Integer, nullable=False, comment='0-100,0不普通应激，100普通应激')
    result_2 = Column(Integer, nullable=False, comment='0-100,0不抑郁，100抑郁')
    result_3 = Column(Integer, nullable=False, comment='0-100,0不焦虑，100焦虑')
    user_id = Column(String(64), nullable=False, comment='关联用户ID')
