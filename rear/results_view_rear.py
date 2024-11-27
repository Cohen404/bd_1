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
from util.window_manager import WindowManager

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
        self.setupUi(self)
        self._index_window = None  # 添加这一行，用于保存主页面窗口引用

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

        window_manager = WindowManager()
        window_manager.register_window('results_view', self)

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
            print(f"从current_user.txt读取到用户ID: {user_id}")

            if not user_id:
                logging.error("Current user ID is empty")
                QMessageBox.warning(self, "错误", "当前用户ID为空")
                return None, False
            
            # 读取用户类型
            path = '../state/user_status.txt'
            user_type = operate_user.read(path)
            print(f"从user_status.txt读取到用户类型: {user_type}")
            is_admin = (user_type == '1')
            
            # 查询用户信息
            session = SessionClass()
            user = session.query(User).filter(User.user_id == user_id).first()
            session.close()
            
            if user:
                print(f"从数据库查询到用户信息: ID={user.user_id}, 用户名={user.username}, 类型={user.user_type}")
                # 验证用户类型是否匹配
                db_is_admin = (user.user_type == 'admin')
                if db_is_admin != is_admin:
                    print(f"警告：文件中的用户类型({is_admin})与数据库中的用户类型({db_is_admin})不匹配")
                return user.user_id, db_is_admin
            else:
                logging.error(f"User not found for ID: {user_id}")
                QMessageBox.warning(self, "错误", "在数据库中未找到当前用户")
                return None, False

        except Exception as e:
            logging.error(f"Error getting current user: {str(e)}")
            print(f"获取用户信息时出错: {str(e)}")
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

            print(f"当前用户ID: {user_id}, 是否管理员: {self.user_type}")

            # 直接查询结果表
            if self.user_type:  # 管理员可以看到所有结果
                print("管理员查询所有结果")
                results = session.query(Result).all()
            else:  # 普通用户只能看到自己的结果
                print(f"普通用户查询自己的结果: {user_id}")
                results = session.query(Result).filter(Result.user_id == user_id).all()

            print(f"查询到 {len(results)} 条结果")

            # 显示结果
            self.tableWidget.setRowCount(len(results))
            for i, result in enumerate(results):
                print(f"处理第 {i+1} 条结果: ID={result.id}, 用户ID={result.user_id}, 时间={result.result_time}")
                
                # 获取用户信息
                user = session.query(User).filter(User.user_id == result.user_id).first()
                username = user.username if user else "未知用户"
                print(f"用户信息: {username}")

                # 结果ID
                self.tableWidget.setItem(i, 0, QTableWidgetItem(str(result.id)))
                # 用户名
                self.tableWidget.setItem(i, 1, QTableWidgetItem(username))
                # 计算时间
                time_str = result.result_time.strftime('%Y-%m-%d %H:%M:%S') if result.result_time else ''
                self.tableWidget.setItem(i, 2, QTableWidgetItem(time_str))
                # 结果1（普通应激）
                self.tableWidget.setItem(i, 3, QTableWidgetItem('是' if result.result_1 == 1 else '否'))
                # 结果2（抑郁）
                self.tableWidget.setItem(i, 4, QTableWidgetItem('是' if result.result_2 == 1 else '否'))
                # 结果3（焦虑）
                self.tableWidget.setItem(i, 5, QTableWidgetItem('是' if result.result_3 == 1 else '否'))

            logging.info(f"Results table refreshed successfully with {len(results)} rows")
            
            # 如果没有数据，显示提示
            if len(results) == 0:
                QMessageBox.information(self, "提示", "暂无评估结果数据")
                
        except Exception as e:
            logging.error(f"Error displaying results table: {str(e)}")
            print(f"错误详情: {str(e)}")  # 打印详细错误信息
            QMessageBox.critical(self, "错误", f"显示结果表格失败：{str(e)}")
        finally:
            session.close()

    def return_index(self):
        """
        返回到相应的主页面
        根据用户类型返回到管理员或普通用户页面
        """
        path = '../state/user_status.txt'
        user_status = operate_user.read(path)
        
        try:
            # 创建新窗口前先保存引用
            if user_status == '1':  # 管理员
                self._index_window = admin_rear.AdminWindowActions()
            else:  # 普通用户
                self._index_window = index_rear.Index_WindowActions()
            
            # 先显示新窗口
            self._index_window.show()
            # 再隐藏当前窗口
            self.hide()
            # 最后关闭当前窗口
            self.close()
            
            logging.info("Returned to index page successfully")
        except Exception as e:
            logging.error(f"Error in return_index: {str(e)}")
            QMessageBox.critical(self, "错误", f"返回主页时发生错误：{str(e)}")

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 这里是界面的入口，在这里需要定义QApplication对象，之后界面跳转时不用再重新定义，只需要调用show()函数即可
    app = QApplication(sys.argv)
    # 显示创建的界面
    demo_window = Results_View_WindowActions()
    demo_window.show()
    sys.exit(app.exec_())