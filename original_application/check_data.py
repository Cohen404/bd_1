from util.db_util import SessionClass
from sql_model.tb_result import Result
from sql_model.tb_user import User

def check_data():
    session = SessionClass()
    try:
        # 检查用户表
        print("\n=== 用户表数据 ===")
        users = session.query(User).all()
        for user in users:
            print(f"用户ID: {user.user_id}, 用户名: {user.username}, 类型: {user.user_type}")

        # 检查结果表
        print("\n=== 结果表数据 ===")
        results = session.query(Result).all()
        for result in results:
            print(f"ID: {result.id}, 用户ID: {result.user_id}, 时间: {result.result_time}")
            print(f"结果: 应激={result.result_1}, 抑郁={result.result_2}, 焦虑={result.result_3}")

    except Exception as e:
        print(f"查询出错: {str(e)}")
    finally:
        session.close()

if __name__ == '__main__':
    check_data() 