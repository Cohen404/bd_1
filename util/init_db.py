import sqlparse
import pymysql

# MySql配置信息
HOST = '127.0.0.1'
PORT = 3306
DATABASE = 'sql_model'
USERNAME = 'root'
PASSWORD = 'root'

def is_exist_database():
    db = pymysql.connect(host=HOST, port=int(PORT), user=USERNAME, password=PASSWORD, charset='utf8')
    cursor1 = db.cursor()
    sql = "select * from information_schema.SCHEMATA WHERE SCHEMA_NAME = '%s'  ; " % DATABASE
    res = cursor1.execute(sql)
    db.close()
    return res

def init_database():
    db = pymysql.connect(host=HOST, port=int(PORT), user=USERNAME, password=PASSWORD, charset='utf8')
    cursor1 = db.cursor()
    sql = "CREATE DATABASE IF NOT EXISTS %s CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;" % DATABASE
    res = cursor1.execute(sql)
    db.close()
    return res

def execute_fromfile(filename):
    """
    从SQL文件执行SQL语句
    """
    try:
        db = pymysql.connect(host=HOST, port=int(PORT), user=USERNAME, password=PASSWORD, database=DATABASE,
                            charset='utf8mb4')
        cursor = db.cursor()
        
        # 读取SQL文件
        print(f"正在读取SQL文件: {filename}")
        with open(filename, 'r', encoding='utf-8') as fd:
            sqlfile = fd.read()
            
        # 格式化SQL语句
        print("正在处理SQL语句...")
        sqlfile = sqlparse.format(sqlfile, strip_comments=True).strip()
        
        # 分割SQL语句
        sqlcommands = sqlfile.split(';')
        print(f"找到 {len(sqlcommands)} 条SQL语句")
        
        # 执行每条SQL语句
        for i, command in enumerate(sqlcommands, 1):
            try:
                command = command.strip()
                if command:
                    print(f"正在执行第 {i} 条SQL语句...")
                    cursor.execute(command)
                    db.commit()
                    print(f"第 {i} 条SQL语句执行成功")
            except Exception as msg:
                print(f"执行第 {i} 条SQL语句时出错:")
                print(f"SQL语句: {command}")
                print(f"错误信息: {msg}")
                db.rollback()
        
        print("所有SQL语句执行完成")
        
    except Exception as e:
        print(f"数据库操作失败: {str(e)}")
    finally:
        if 'db' in locals():
            db.close()

if __name__ == '__main__':
    if is_exist_database():
        print('数据库已经存在，正在重新初始化...')
    if init_database():
        print('数据库创建/更新成功')
    execute_fromfile('sql_model.sql')
    print('表创建成功')
