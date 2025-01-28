from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .base import Base


class Data(Base):
    __tablename__ = 'tb_data'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    personnel_id = Column(String(64), nullable=False, comment='人员id')
    data_path = Column(String(255), comment='文件路径')
    upload_user = Column(Integer, nullable=False, comment='0/1,0是普通用户，1是管理员')
    personnel_name = Column(String(255), nullable=False, comment='人员姓名')
    user_id = Column(String(64), nullable=False, comment='关联用户ID')
    upload_time = Column(DateTime, default=datetime.now, comment='上传时间')