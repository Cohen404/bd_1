import os
os.environ['PGCLIENTENCODING'] = 'utf8'

from sqlalchemy import create_engine, inspect
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?client_encoding=utf8"

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    inspector = inspect(engine)
    
    tables = inspector.get_table_names()
    
    if tables:
        print(f"数据库 {DB_NAME} 中的表:")
        print("-" * 50)
        for i, table_name in enumerate(tables, 1):
            print(f"{i}. {table_name}")
    else:
        print("数据库中没有表")
    
    engine.dispose()
    
except Exception as e:
    print(f"查询失败: {e}")
    import traceback
    traceback.print_exc()
