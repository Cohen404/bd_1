# 文件功能：结果查看界面的后端逻辑
# 该脚本实现了结果查看界面的功能，包括显示评估结果列表、查看详细结果、删除结果等操作

import os
import sys

import logging
from pyqt5_plugins.examplebutton import QtWidgets

sys.path.append('../')
import time
from datetime import datetime, timedelta
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsPixmapItem, QGraphicsScene, QMessageBox, \
    QTableWidgetItem
import state.operate_user as operate_user
# 导入本页面的前端部分
import front.results_view as results_view

# 导入跳转页面的后端部分
from rear import index_rear
from rear import admin_rear
from sql_model.tb_data import Data
from sql_model.tb_result import Result
from sql_model.tb_user import User
from util.db_util import SessionClass
from sql_model.tb_user import User

# import admin_rear
class UserFilter(logging.Filter):
    """
    自定义日志过滤器，用于添加用户类型信息到日志记录中
    """
    def __init__(self, userType):
        super().__init__()
        self.userType = userType

    def filter(self, record):
        record.userType = self.userType
        return True

class Results_View_WindowActions(results_view.Ui_MainWindow, QMainWindow):
    """
    结果查看窗口的主要类，继承自PyQt5的QMainWindow和前端UI类
    """

    def __init__(self):
        """
        初始化结果查看窗口
        """
        super(results_view.Ui_MainWindow, self).__init__()
        # 创建界面
        self.setupUi(self)

        # 获取当前用户信息
        self.user_id, is_admin = self.get_current_user()
        self.user_type = is_admin

        # 显示表格内容
        self.show_table()

        # 从文件中读取用户类型并设置userType
        path = '../state/user_status.txt'
        user = operate_user.read(path)  # 0表示普通用户，1表示管理员
        userType = "Regular user" if user == 0 else "Administrator"

        # 配置日志
        logging.basicConfig(
            filename='../log/log.txt',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(userType)s - %(message)s'
        )
        logger = logging.getLogger()
        logger.addFilter(UserFilter(userType))

        # 连接按钮事件
        self.btn_return.clicked.connect(self.return_index)  # 返回首页

    def get_user_type(self, user_id):
        """
        获取用户类型
        """
        session = SessionClass()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                return user.user_type == 'admin'  # 返回布尔值：True表示管理员，False表示普通用户
            return False
        except Exception as e:
            logging.error(f"Error getting user type: {str(e)}")
            return False
        finally:
            session.close()

    def get_current_user(self):
        """
        获取当前用户信息
        返回: (user_id, is_admin)
        """
        try:
            # 检查文件是否存在
            import os
            if not os.path.exists('../state/current_user.txt'):
                logging.error("Current user file not found")
                QMessageBox.warning(self, "错误", "未找到当前用户信息文件")
                return None, False

            # 读取用户ID
            with open('../state/current_user.txt', 'r') as f:
                user_id = f.read().strip()

            if not user_id:
                logging.error("Current user ID is empty")
                QMessageBox.warning(self, "错误", "当前用户ID为空")
                return None, False
            
            # 查询用户信息
            session = SessionClass()
            user = session.query(User).filter(User.user_id == user_id).first()
            session.close()
            
            if user:
                logging.info(f"Successfully retrieved current user: {user.username}")
                return user.user_id, user.user_type == 'admin'
            else:
                logging.error(f"User not found for ID: {user_id}")
                QMessageBox.warning(self, "错误", "在数据库中未找到当前用户")
                return None, False

        except Exception as e:
            logging.error(f"Error getting current user: {str(e)}")
            QMessageBox.critical(self, "错误", f"获取当前用户信息失败：{str(e)}")
            return None, False

    def show_nav(self):
        """
        显示导航栏和状态信息
        """
        # header
        session = SessionClass()
        result = session.query(Result).order_by(Result.id.desc()).first()
        session.close()
        # 获取tb_result表中最新的一条记录，得到result对象
        if result is not None:  # result存在
            result_1 = result.result_1  # 应激状态
            result_2 = result.result_2  # 抑郁状态
            result_3 = result.result_3  # 焦虑状态

            if (result_1):
                self.health_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; border-radius: 16px; border: 2px solid white; background: red"
                )
            else:
                self.health_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; border-radius: 16px; border: 2px solid white; background: green"
                )

            if (result_2):
                self.acoustic_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; border-radius: 16px; border: 2px solid white; background: red"
                )
            else:
                self.acoustic_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; border-radius: 16px; border: 2px solid white; background: green"
                )

            if (result_3):
                self.mechanical_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; border-radius: 16px; border: 2px solid white; background: red"
                )
            else:
                self.mechanical_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; border-radius: 16px; border: 2px solid white; background: green"
                )

    def show_table(self):
        """
        显示结果表格
        """
        session = SessionClass()
        try:
            # 获取当前用户ID
            user_id = self.user_id
            if not user_id:
                QMessageBox.warning(self, "错误", "无法获取当前用户信息")
                return

            # 查询结果
            if self.user_type:  # 管理员可以看到所有结果
                results = session.query(Result, User).join(User).all()
            else:  # 普通用户只能看到自己的结果
                results = session.query(Result, User).join(User).filter(Result.user_id == user_id).all()

            # 显示结果
            self.tableWidget.setRowCount(len(results))
            for i, (result, user) in enumerate(results):
                # 结果ID
                self.tableWidget.setItem(i, 0, QTableWidgetItem(str(result.id)))
                # 用户名
                self.tableWidget.setItem(i, 1, QTableWidgetItem(user.username))
                # 计算时间
                time_str = result.result_time.strftime('%Y-%m-%d %H:%M:%S') if result.result_time else ''
                self.tableWidget.setItem(i, 2, QTableWidgetItem(time_str))
                # 结果1（普通应激）
                self.tableWidget.setItem(i, 3, QTableWidgetItem('是' if result.result_1 == 1 else '否'))
                # 结果2（抑郁）
                self.tableWidget.setItem(i, 4, QTableWidgetItem('是' if result.result_2 == 1 else '否'))
                # 结果3（焦虑）
                self.tableWidget.setItem(i, 5, QTableWidgetItem('是' if result.result_3 == 1 else '否'))

            logging.info("Results table refreshed successfully")
        except Exception as e:
            logging.error(f"Error displaying results table: {str(e)}")
            QMessageBox.critical(self, "错误", f"显示结果表格失败：{str(e)}")
        finally:
            session.close()

    def return_index(self):
        """
        返回首页
        """
        path = '../state/user_status.txt'
        user = operate_user.read(path)

        if user == '0':  # 返回系统首页
            self.index = index_rear.Index_WindowActions()
            logging.info("Returned to user homepage")
        elif user == '1':  # 返回管理员首页
            self.index = admin_rear.AdminWindowActions()
            logging.info("Returned to admin homepage")

        self.close()
        self.index.show()

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 这里是界面的入口，在这里需要定义QApplication对象，之后界面跳转时不用再重新定义，只需要调用show()函数即可
    app = QApplication(sys.argv)
    # 显示创建的界面
    demo_window = Results_View_WindowActions()
    demo_window.show()
    sys.exit(app.exec_())