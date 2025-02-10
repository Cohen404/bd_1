from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sql_model.base import Base
from sql_model.tb_user import User
from sql_model.tb_result import Result
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# PostgreSQL配置信息
HOST = os.getenv('DB_HOST', '127.0.0.1')
PORT = os.getenv('DB_PORT', 5432)
DATABASE = os.getenv('DB_NAME', 'bj_health_db')
USERNAME = os.getenv('DB_USER', 'postgres')
PASSWORD = os.getenv('DB_PASS', 'tj654478')

# 创建数据库连接
connection_string = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
engine = create_engine(connection_string)

# 创建所有表
Base.metadata.create_all(engine)

# 创建Session类
SessionClass = sessionmaker(bind=engine)
