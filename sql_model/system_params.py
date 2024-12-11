from sqlalchemy import Column, Integer, String, Float
from .base import Base

class SystemParams(Base):
    __tablename__ = 'tb_system_params'
    
    param_id = Column(String(64), primary_key=True, nullable=False)
    eeg_frequency = Column(Float, comment='脑电数据采样频率 (Hz)')
    electrode_count = Column(Integer, comment='电极数量')
    scale_question_num = Column(Integer, comment='量表问题数量')
    model_num = Column(Integer, comment='系统中可用的模型数量')
    id = Column(Integer, nullable=False) 