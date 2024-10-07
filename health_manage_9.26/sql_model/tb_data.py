import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base


class Data(declarative_base()):
    __tablename__ = 'tb_data'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    personnel_id = Column(Integer,nullable=False, comment='人员id')
    data_path = Column(String(255), comment='文件路径')
    upload_user = Column(Integer, nullable=False, comment='0/1,0是普通用户，1是管理员')
    personnel_name = Column(String(255), comment='人员姓名')
    user_id = Column(Integer, nullable=False)
    upload_time = Column(DateTime)  # 添加这一行