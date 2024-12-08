from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime
from .base import Base


class Result(Base):
    __tablename__ = 'tb_result'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    result_time = Column(DateTime, default=datetime.now, comment='结果计算时间')
    stress_score = Column(Float, nullable=False, comment='0-100,0不普通应激，100普通应激')
    depression_score = Column(Float, nullable=False, comment='0-100,0不抑郁，100抑郁')
    anxiety_score = Column(Float, nullable=False, comment='0-100,0不焦虑，100焦虑')
    report_path = Column(String(255), nullable=True, comment='报告路径')
    user_id = Column(String(64), nullable=False, comment='关联用户ID')
