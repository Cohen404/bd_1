from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sql_model.base import Base
from sql_model.tb_user import User
from sql_model.tb_result import Result

# MySql配置信息
HOST = '127.0.0.1'
PORT = 3306
DATABASE = 'sql_model'
USERNAME = 'root'
PASSWORD = 'root'

connection_string = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
engine = create_engine(connection_string, encoding='utf8')

# 创建所有表
Base.metadata.create_all(engine)

# 创建Session类
SessionClass = sessionmaker(bind=engine)
