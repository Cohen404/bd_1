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
    QGraphicsPixmapItem, QGraphicsScene, QInputDialog, QLineEdit
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
        self.show_table()  # 调用show_table方法显示table的内容

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

    # 定义通道选择对应的事件（没用但不能删）
    def WrittingNotOfOther(self, tag):
        if tag == 0:
            print('点到了第1项 ...')
        if tag == 1:
            print('点到了第2项 ...')
        if tag == 2:
            print('点到了第3项 ...')
        if tag == 3:
            print('点到了第4项 ...')
        if tag == 4:
            print('点到了第5项 ...')
        if tag == 5:
            print('点到了第6项 ...')
        if tag == 6:
            print('点到了第7项 ...')
        if tag == 7:
            print('点到了第8项 ...')
        if tag == 8:
            print('点到了第9项 ...')
        if tag == 9:
            print('点到了第10项 ...')

    def show_table(self):
        # 测试用例
        info = [[1, 'admin','2024.0711 22.01' , '../log/log.txt'],
                ]# info用作测试用，到时候是data对象的各个值

        for data in info:
            row = self.tableWidget.rowCount()  # 当前form有多少行，最后一行是第row-1行
            self.tableWidget.insertRow(row)  # 创建新的行

            for i in range(len(self.lst) - 1):
                item = QTableWidgetItem()
                # 获得上传数据信息，将其添加到form中
                content = ''
                if i == 0:
                    content = data[0]  # data[0]对应data.id
                elif i == 1:
                    content = data[1]
                elif i == 2:
                    content = data[2]
                elif i == 3:
                    content = data[3]
                item.setText(str(content))  # 将content转为string类型才能存入单元格，否则报错。
                self.tableWidget.setItem(row, i, item)
            self.tableWidget.setCellWidget(row, len(self.lst) - 1, self.buttonForRow())  # 在最后一个单元格中加入按钮

    def buttonForRow(self):
        widget = QtWidgets.QWidget()
        # 查看
        self.check_pushButton = QtWidgets.QPushButton('查看')
        self.check_pushButton.setStyleSheet(''' text-align : center;
                                          background-color : NavajoWhite;
                                          height : 30px;
                                          border-style: outset;
                                          font : 13px  ''')
        # 删除
        self.delete_pushButton = QtWidgets.QPushButton('删除')
        self.delete_pushButton.setStyleSheet(''' text-align : center;
                                                  background-color : LightCoral;
                                                  height : 30px;
                                                  border-style: outset;
                                                  font : 13px  ''')

        # 查看数据功能
        self.check_pushButton.clicked.connect(self.checkbutton)
        # 删除功能
        self.delete_pushButton.clicked.connect(self.deletebutton)

        hLayout = QtWidgets.QHBoxLayout()
        hLayout.addWidget(self.check_pushButton)
        hLayout.addWidget(self.delete_pushButton)
        hLayout.setContentsMargins(5, 2, 5, 2)
        widget.setLayout(hLayout)
        return widget

    def checkbutton(self):
        try:
            # 记录按钮点击事件到日志文件
            logging.info("checkbutton was clicked.")

            # 使用系统的记事本打开文件
            file_path = '../log/log.txt'
            if os.path.exists(file_path):
                os.system(f'notepad.exe {file_path}')
            else:
                logging.warning("Log file not found.")
                print("Log file not found.")
        except Exception as e:
            # 处理其他潜在的错误，并记录到日志文件
            logging.error(f"An error occurred: {str(e)}")
            print(f"An error occurred: {str(e)}")

    # 删除功能
    def deletebutton(self):
        # 弹出确认对话框
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除日志记录吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        # 如果用户点击了 "Yes"
        if reply == QMessageBox.Yes:
            try:
                # 清空日志文件内容，但不删除文件
                file_path = '../log/log.txt'
                if os.path.exists(file_path):
                    with open(file_path, 'w') as file:
                        file.truncate(0)  # 清空文件内容

                    # 记录日志信息
                    logging.info("Log file cleared by user.")

                    # 弹出日志记录已清除的对话框
                    QMessageBox.information(self, "日志清除", "日志记录已清除")
                else:
                    QMessageBox.warning(self, "错误", "日志文件未找到")

            except Exception as e:
                logging.error(f"Error while clearing log file: {str(e)}")
                QMessageBox.critical(self, "错误", f"清除日志时发生错误: {str(e)}")


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
