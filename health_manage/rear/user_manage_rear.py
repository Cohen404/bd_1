import os
import sys

import logging

from sql_model.pwd_md5 import md5

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
import front.user_manage as user_manage

# 导入跳转页面的后端部分
from rear import index_rear
from data.load_data import any_pressure_curve
from rear import admin_rear
from sql_model.tb_user import User
from sql_model.tb_result import Result
from util.db_util import SessionClass
from model.CNN import Rnn
from model.classifer_8 import BasicConvResBlock
from model.classifer_8 import CNN

class UserFilter(logging.Filter):
    def __init__(self, userType):
        super().__init__()
        self.userType = userType

    def filter(self, record):
        record.userType = self.userType
        return True

class User_Manage_WindowActions(user_manage.Ui_MainWindow, QMainWindow):

    def __init__(self):
        super(user_manage.Ui_MainWindow, self).__init__()
        self.id = None
        self.setupUi(self)
        self.show_table()  # 调用show_table方法显示table的内容

        # button to connect
        self.btn_return.clicked.connect(self.return_index)  # 返回首页
        self.addButton.clicked.connect(self.add_user)

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
        session = SessionClass()
        kk = session.query(User).filter().all()
        session.close()
        info = []
        for item in kk:
            info.append([item.id, item.pwd,item.name, item.user_type])

        # 清空当前表格
        self.tableWidget.setRowCount(0)

        # 处理查询结果并将其显示在表格中
        for data in info:
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)  # 创建新的一行

            # 处理用户类型显示
            user_name = '普通用户' if data[3] == 0 else '管理员'  # 根据用户类型显示相应的名称

            # 添加表格项
            for i in range(len(self.lst) - 1):
                item = QTableWidgetItem()
                content = ''
                if i == 0:
                    content = data[0] # 用户ID
                elif i == 1:
                    content = data[2]  # 用户名
                elif i == 2:
                    # 对于密码字段，使用 QLineEdit 控件来隐藏密码
                    line_edit = QLineEdit()
                    line_edit.setEchoMode(QLineEdit.Password)
                    line_edit.setReadOnly(True)  # 设置为只读
                    line_edit.setText(data[1])  # 设置密码内容
                    self.tableWidget.setCellWidget(row, i, line_edit)
                elif i == 3:
                    content = user_name  # 用户类型

                item.setText(str(content))  # 将内容转为字符串并存入单元格
                self.tableWidget.setItem(row, i, item)

            # 在最后一个单元格中加入按钮
            self.tableWidget.setCellWidget(row, len(self.lst) - 1, self.buttonForRow())

    def buttonForRow(self):
        widget = QtWidgets.QWidget()
        # 查看
        self.check_pushButton = QtWidgets.QPushButton('删除')
        self.check_pushButton.setStyleSheet(''' text-align : center;
                                          background-color : NavajoWhite;
                                          height : 30px;
                                          border-style: outset;
                                          font : 13px  ''')
        # 删除
        self.delete_pushButton = QtWidgets.QPushButton('修改密码')
        self.delete_pushButton.setStyleSheet(''' text-align : center;
                                                  background-color : LightCoral;
                                                  height : 30px;
                                                  border-style: outset;
                                                  font : 13px  ''')

        # 查看数据功能
        self.check_pushButton.clicked.connect(self.delete_button)
        # 删除功能
        self.delete_pushButton.clicked.connect(self.updatePSWD_button)

        hLayout = QtWidgets.QHBoxLayout()
        hLayout.addWidget(self.check_pushButton)
        hLayout.addWidget(self.delete_pushButton)
        hLayout.setContentsMargins(5, 2, 5, 2)
        widget.setLayout(hLayout)
        return widget

    def delete_button(self):
        button = self.sender()
        if button:
            # 获取按钮所在的行
            row = self.tableWidget.indexAt(button.parent().pos()).row()
            id = self.tableWidget.item(row, 0).text()  # 获取当前行数据的ID值
            id = int(id)  # 确保id是整数类型

            # 检查要删除的数据是否为当前查看的数据
            if id == self.id:
                self.id = 0
                self.data_path = ''

            # 开始数据库会话
            session = SessionClass()
            try:
                # 删除result表中对应的数据
                session.query(User).filter(User.id == id).delete()
                session.commit()

                # 记录日志
                logging.info(f"User with ID {id} has been deleted from the database.")
            except Exception as e:
                session.rollback()
                logging.error(f"Error occurred while trying to delete user with ID {id}: {str(e)}")
            finally:
                session.close()

            # 从表格中移除记录
            self.tableWidget.removeRow(row)

    # 删除功能
    def updatePSWD_button(self):
        button = self.sender()  # 获取发出信号的按钮
        if button:
            # 获取按钮所在的行
            row = self.tableWidget.indexAt(button.parent().pos()).row()
            # 获取当前行的ID（假设ID在第一列）
            id = self.tableWidget.item(row, 0).text()

            # 弹出输入框，获取新密码
            new_password, ok = QInputDialog.getText(self, '修改密码', '请输入新密码:', QLineEdit.Password)
            if ok and new_password:  # 检查用户是否点击了确定并且输入了新密码
                try:
                    # 执行更新密码的逻辑
                    session = SessionClass()
                    user = session.query(User).filter(User.id == id).first()
                    if user:
                        old_password = user.pwd
                        user.pwd =new_password  # 更新密码字段
                        session.commit()

                        # 记录日志信息
                        logging.info(
                            f"Password for user ID {id} was updated successfully. Old password: {old_password}, New password: {new_password}")

                        QMessageBox.information(self, '成功', '密码修改成功！')
                        self.show_table()
                    else:
                        QMessageBox.warning(self, '错误', '用户不存在！')

                        # 记录用户不存在的情况
                        logging.warning(f"Attempted to update password for non-existent user ID {id}.")

                    session.close()
                except Exception as e:
                    session.rollback()
                    QMessageBox.critical(self, '错误', f'密码修改失败：{str(e)}')

                    # 记录错误信息
                    logging.error(f"Failed to update password for user ID {id}: {str(e)}")

    # btn_return返回首页


    def add_user(self):
        # 获取用户输入的信息
        username = self.nameIN.text().strip()
        password = self.pswdIN.text().strip()
        character = self.character_comboBox.currentText()

        # 验证输入
        if not username or not password:
            QMessageBox.warning(self, "输入错误", "用户名和密码不能为空！")
            logging.warning("Attempted to add user but username or password was empty.")
            return

        # 角色映射
        role = 0 if character == "普通用户" else 1

        # 数据库操作
        session = SessionClass()
        try:
            # 获取最大 ID
            max_id = session.query(User.id).order_by(User.id.desc()).first()
            if max_id is None:
                new_id = 1  # 如果表中没有记录，ID 从 1 开始
            else:
                new_id = max_id[0] + 1  # 最大 ID 加 1

            # 检查用户名是否已存在
            existing_user = session.query(User).filter(User.name == username).first()
            if existing_user:
                QMessageBox.warning(self, "错误", "用户名已存在，请选择其他用户名。")
                logging.warning(f"Attempted to add user but username '{username}' already exists.")
            else:
                # 创建新用户并添加到数据库
                new_user = User(id=new_id, name=username, pwd=password, user_type=role)
                session.add(new_user)
                session.commit()
                QMessageBox.information(self, "成功", "用户添加成功！")
                logging.info(f"User '{username}' added successfully with ID {new_id}.")
                # 清空输入框
                self.nameIN.clear()
                self.pswdIN.clear()
        except Exception as e:
            logging.error(f"Error adding user '{username}': {str(e)}")
            QMessageBox.critical(self, "错误", f"添加用户失败：{str(e)}")
        finally:
            session.close()
            self.show_table()

    def return_index(self):
        path = '../state/user_status.txt'
        user = operate_user.read(path)  # 0表示普通用户，1表示管理员

        if user == '0':  # 返回系统首页
            self.index = index_rear.Index_WindowActions()
            logging.info("Returned to user homepage.")
        elif user == '1':  # 返回管理员首页
            self.index = admin_rear.AdminWindowActions()
            logging.info("Returned to admin homepage.")

        self.close()
        self.index.show()


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 这里是界面的入口，在这里需要定义QApplication对象，之后界面跳转时不用再重新定义，只需要调用show()函数即可
    app = QApplication(sys.argv)
    # 显示创建的界面
    demo_window = User_Manage_WindowActions()
    demo_window.show()
    sys.exit(app.exec_())
