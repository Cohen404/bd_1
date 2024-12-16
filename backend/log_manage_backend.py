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
import front.log_manage_UI as log_manage_UI
# 导入跳转页面的后端部分
from backend import admin_index_backend, index_backend
from sql_model.tb_user import User
from util.db_util import SessionClass
import logging
from util.window_manager import WindowManager

from config import (
    USER_STATUS_FILE, 
    CURRENT_USER_FILE, 
    LOG_FILE, 
    MODEL_STATUS_FILE,
    DATA_DIR
)


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

class Log_Manage_WindowActions(log_manage_UI.Ui_MainWindow, QMainWindow):
    """
    日志管理窗口的主要类，继承自PyQt5的QMainWindow和前端UI类
    """

    def __init__(self):
        """
        初始化日志管理窗口
        """
        super(log_manage_UI.Ui_MainWindow, self).__init__()
        self.setupUi(self)
        self.show_log_content()  # 调用方法显示日志内容

        # button to connect
        self.btn_return.clicked.connect(self.return_index)  # 返回首页

        # 从文件中读取用户类型并设置userType
        path = USER_STATUS_FILE
        user = operate_user.read(path)  # 0表示普通用户，1表示管理员
        userType = "Regular user" if user == 0 else "Administrator"

        # 配置 logging 模块
        logging.basicConfig(
            filename=LOG_FILE,
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
        ���日志文件中读取最后200行并显示在界面上
        """
        try:
            # Read the last 100 lines of the log file
            file_path = LOG_FILE
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
        path = USER_STATUS_FILE
        user_status = operate_user.read(path)
        
        try:
            window_manager = WindowManager()
            # 创建新窗口前先保存引用
            if user_status == '1':  # 管理员
                self._index_window = admin_index_backend.AdminWindowActions()
                window_manager.register_window('admin', self._index_window)
                window_manager.show_window('admin')
            else:  # 普通用户
                self._index_window = index_backend.Index_WindowActions()
                window_manager.register_window('index', self._index_window)
                window_manager.show_window('index')
            
            # 隐藏并关闭当前窗口
            self.hide()
            self.close()
            
            logging.info("Returned to index page successfully")
        except Exception as e:
            logging.error(f"Error in return_index: {str(e)}")
            QMessageBox.critical(self, "错误", f"返回主页时发生错误：{str(e)}")



if __name__ == '__main__':
    # 启用高DPI缩放
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 这里是界面的入口，在这里需要定义QApplication对象，之后界面跳转时不用再重新定义，只需要调用show()函数即可
    app = QApplication(sys.argv)
    # 显示创建的界面
    demo_window = Log_Manage_WindowActions()
    window_manager = WindowManager()
    window_manager.register_window('log_manage', demo_window)
    window_manager.show_window('log_manage')
    
    # 进入应用的主事件循环
    sys.exit(app.exec_())
