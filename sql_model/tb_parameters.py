from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base


class Parameters(declarative_base()):
    __tablename__ = 'tb_parameters'
    eeg_location = Column(String(255), comment='脑电采集指标位置')
    frequency = Column(Integer, comment='频率')
    electrode_count = Column(Integer, comment='电极数')
    data_format = Column(Integer, comment='数据采集格式')
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)