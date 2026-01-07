# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# import models

# # 创建数据库连接URL
# DATABASE_URL = "postgresql://postgres:tj654478@127.0.0.1:5432/bj_health_db?client_encoding=GBK"

# # 创建引擎
# engine = create_engine(DATABASE_URL)

# # 创建会话类
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # 创建基类
# Base = declarative_base()

# Base.metadata.create_all(bind=engine)

from database import engine;

print('数据库连接成功' if engine.connect() else '连接失败')