import os
import sys

os.environ['PGCLIENTENCODING'] = 'utf8'

import psycopg2
from psycopg2 import sql

try:
    conn = psycopg2.connect(
        host='127.0.0.1',
        port='5432',
        database='bj_health_db',
        user='postgres',
        password='tj654478',
        client_encoding='utf8'
    )
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    tables = cursor.fetchall()
    
    if tables:
        print("数据库 bj_health_db 中的表:")
        print("-" * 50)
        for i, (table_name,) in enumerate(tables, 1):
            print(f"{i}. {table_name}")
    else:
        print("数据库中没有表")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"查询失败: {e}")
    import traceback
    traceback.print_exc()
