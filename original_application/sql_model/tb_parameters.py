from sqlalchemy import Column, Integer, String
from .base import Base


class Parameters(Base):
    __tablename__ = 'tb_parameters'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    eeg_location = Column(String(255), comment='脑电采集指标位置')
    frequency = Column(Integer, comment='频率')
    electrode_count = Column(Integer, comment='电极数')
    data_format = Column(Integer, comment='数据采集格式')