# 文件功能：日志管理界面的后端逻辑
# 该脚本实现了日志管理界面的功能，包括显示日志内容、返回首页等操作

import sys
sys.path.append('../')
import os
from datetime import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QWidget, QPushButton, QHBoxLayout
import state.operate_user as operate_user
# 导入本页面的前端部分
import front.log_manage as log_manage
# 导入跳转页面的后端部分
from rear import index_rear, admin_rear
from sql_model.tb_user import User
from util.db_util import SessionClass
import logging
from util.window_manager import WindowManager

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

class Log_Manage_WindowActions(log_manage.Ui_MainWindow, QMainWindow):
    """
    日志管理窗口的主要类，继承自PyQt5的QMainWindow和前端UI类
    """

    def __init__(self):
        """
        初始化日志管理窗口
        """
        super(log_manage.Ui_MainWindow, self).__init__()
        self.setupUi(self)
        self.show_log_content()  # 调用方法显示日志内容

        # button to connect
        self.btn_return.clicked.connect(self.return_index)  # 返回首页

        # 从文件中读取用户类型并设置userType
        path = '../state/user_status.txt'
        user = operate_user.read(path)  # 0表示普通用户，1表示管理员
        userType = "Regular user" if user == 0 else "Administrator"

        # 配置 logging 模块
        logging.basicConfig(
            filename='../log/log.txt',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(userType)s - %(message)s'
        )

        # 添加过滤器
        logger = logging.getLogger()
        logger.addFilter(UserFilter(userType))

        # 初始化窗口管理器
        window_manager = WindowManager()
        window_manager.register_window('log_manage', self)

    def show_log_content(self):
        """
        显示日志内容
        从日志文件中读取最后200行并显示在界面上
        """
        try:
            # Read the last 100 lines of the log file
            file_path = '../log/log.txt'
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as log_file:
                    lines = log_file.readlines()
                    last_200_lines = lines[-200:]  # Get the last 100 lines
                    self.displayBox.setText(''.join(last_200_lines))
            else:
                self.displayBox.setText("Log file not found.")
                logging.warning("Log file not found.")
        except Exception as e:
            logging.error(f"An error occurred while reading the log file: {str(e)}")
            self.displayBox.setText(f"An error occurred: {str(e)}")

    # btn_return返回首页
    def return_index(self):
        """
        返回到相应的主页面
        根据用户类型返回到管理员或普通用户页面
        """
        path = '../state/user_status.txt'
        user_status = operate_user.read(path)
        
        session = SessionClass()
        try:
            # 先尝试直接用用户名查询
            user = session.query(User).filter(User.username == user_status).first()
            if not user:
                # 如果找不到，尝试将user_status转换为整数作为user_id查询
                try:
                    user_id = int(user_status)
                    user = session.query(User).filter(User.user_id == user_id).first()
                except ValueError:
                    user = None
            
            if user and user.user_type == 'admin':
                index_window = admin_rear.AdminWindowActions()
                logging.info("Returning to admin homepage")
            else:
                index_window = index_rear.Index_WindowActions()
                logging.info("Returning to user homepage")
            
            self.close()
            index_window.show()
            
        except Exception as e:
            logging.error(f"Error in return_index: {str(e)}")
            QMessageBox.critical(self, "错误", f"返回主页时发生错误：{str(e)}")
        finally:
            session.close()


if __name__ == '__main__':
    # 启用高DPI缩放
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 这里是界面的入口，在这里需要定义QApplication对象，之后界面跳转时不用再重新定义，只需要调用show()函数即可
    app = QApplication(sys.argv)
    # 显示创建的界面
    demo_window = Log_Manage_WindowActions()
    demo_window.show()
    
    # 进入应用的主事件循环
    sys.exit(app.exec_())
