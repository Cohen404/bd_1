from sqlalchemy import create_engine
from dotenv import dotenv_values
from sqlalchemy.orm import sessionmaker

# 目录不要弄错,这个要和调用该方法的文件在同一路径下，比如你在db_util中调用方法，那么.env在上一目录，需要改成../
config = dotenv_values('../.env')
# MySql配置信息
HOST = config.get('MYSQL_HOST') or '127.0.0.1'
PORT = config.get('MYSQL_PORT') or 3306
DATABASE = config.get('MYSQL_DATABASE')
USERNAME = config.get('MYSQL_USERNAME')
PASSWORD = config.get('MYSQL_PASSWORD')
connection_string = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
engine = create_engine(connection_string, encoding='utf8')
# 创建Session类
SessionClass = sessionmaker(bind=engine)
