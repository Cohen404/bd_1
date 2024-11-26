import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base


class Model(declarative_base()):
    __tablename__ = 'tb_model'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    model_type = Column(Integer,comment='0普通应激模型，1抑郁评估模型，2焦虑评估模型')
    model_path = Column(String(255),comment='模型路径')
    create_time = Column(DateTime,default=datetime.datetime.now(),comment='创建时间')
