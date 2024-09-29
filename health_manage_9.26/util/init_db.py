from dotenv import dotenv_values
import sqlparse
import pymysql

# 目录不要弄错

config = dotenv_values('../.env')
# MySql配置信息
HOST = config.get('MYSQL_HOST') or '127.0.0.1'
PORT = config.get('MYSQL_PORT') or 3306
DATABASE = config.get('MYSQL_DATABASE')
USERNAME = config.get('MYSQL_USERNAME')
PASSWORD = config.get('MYSQL_PASSWORD')


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
    sql = "CREATE DATABASE IF NOT EXISTS %s CHARSET=utf8 COLLATE=utf8_general_ci;" % DATABASE
    res = cursor1.execute(sql)
    db.close()
    return res


def execute_fromfile(filename):
    db = pymysql.connect(host=HOST, port=int(PORT), user=USERNAME, password=PASSWORD, database=DATABASE,
                         charset='utf8')
    fd = open(filename, 'r', encoding='utf-8')
    cursor = db.cursor()
    sqlfile = fd.read()
    sqlfile = sqlparse.format(sqlfile, strip_comments=True).strip()

    sqlcommamds = sqlfile.split(';')

    for command in sqlcommamds:
        try:
            cursor.execute(command)
            db.commit()

        except Exception as msg:

            db.rollback()
    db.close()


# def init_db():
if __name__ == '__main__':
    if is_exist_database():
        print('数据库已经存在,为防止误初始化，请手动删除 %s 数据库' % str(DATABASE))
    else:
        if init_database():
            print('数据库%s创建成功' % str(DATABASE))
        execute_fromfile('../sql_model.sql')
        print('表创建成功')
