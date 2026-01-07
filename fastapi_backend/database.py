from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS
import logging

# 创建数据库连接URL
DATABASE_URL = "postgresql://postgres:tj654478@127.0.0.1:5432/bj_health_db"

# 创建引擎
engine = create_engine(DATABASE_URL)

# 创建会话类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

# 依赖项函数，用于获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 初始化数据库
def init_db():
    try:
        # 导入模型以确保Base.metadata知道所有表
        import models
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logging.info("数据库表已创建")
    except Exception as e:
        logging.error(f"初始化数据库时出错: {e}")
        raise 