import os
import sys

import logging
sys.path.append('../')
import time

import numpy as np
import scipy.io as scio
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFileDialog, QMessageBox, QTableWidgetItem, \
    QGraphicsPixmapItem, QGraphicsScene, QInputDialog, QLineEdit, QTextEdit
from PyQt5 import QtWidgets
from datetime import datetime
import state.operate_user as operate_user

# 导入本页面的前端部分
import front.log_manage as log_manage

# 导入跳转页面的后端部分
from rear import index_rear
from rear import admin_rear

class UserFilter(logging.Filter):
    def __init__(self, userType):
        super().__init__()
        self.userType = userType

    def filter(self, record):
        record.userType = self.userType
        return True

class Log_Manage_WindowActions(log_manage.Ui_MainWindow, QMainWindow):

    def __init__(self):
        super(log_manage.Ui_MainWindow, self).__init__()
        self.setupUi(self)
        self.show_log_content()  # Call the new method to display log content

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

    def show_log_content(self):
        # # Replace table with a QTextEdit widget to display log content
        # self.log_display = QTextEdit(self.centralwidget)
        # self.log_display.setReadOnly(True)  # Set it as read-only
        # self.mainVLayout.addWidget(self.log_display)

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
        try:
            path = '../state/user_status.txt'
            user = operate_user.read(path)  # 0表示普通用户，1表示管理员

            if user == '0':  # 返回系统首页
                self.index = index_rear.Index_WindowActions()
                logging.info("Regular user returned to the system homepage.")
            elif user == '1':  # 返回管理员首页
                self.index = admin_rear.AdminWindowActions()
                logging.info("Administrator returned to the admin homepage.")
            else:
                logging.warning(f"Unexpected user status found in {path}: {user}")

            self.close()
            self.index.show()
        except Exception as e:
            logging.error(f"Error while returning to index: {str(e)}")


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 这里是界面的入口，在这里需要定义QApplication对象，之后界面跳转时不用再重新定义，只需要调用show()函数即可
    app = QApplication(sys.argv)
    # 显示创建的界面
    demo_window = Log_Manage_WindowActions()
    demo_window.show()
    sys.exit(app.exec_())
