import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base


class Result(declarative_base()):
    __tablename__ = 'tb_result'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    result_time = Column(DateTime, default=datetime.datetime.now(), comment='结果计算时间')
    result_1 = Column(Integer, nullable=True, comment='0/1,0不普通应激，1普通应激')
    result_2 = Column(Integer, nullable=True, comment='0/1,0不抑郁，1抑郁')
    result_3 = Column(Integer, nullable=True, comment='0/1,0不焦虑，1焦虑')
    user_id = Column(Integer, nullable=False)
