# 文件功能：用户管理界面的后端逻辑
# 该脚本实现了用户管理界面的功能，包括显示用户列表、添加用户、删除用户、修改密码等操作

import os
import sys
import logging
sys.path.append('../')
import time
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem
import state.operate_user as operate_user

# 导入本页面的前端部分
import front.user_manage as user_manage

# 导入跳转页面的后端部分
from rear import index_rear
from rear import admin_rear
from sql_model.tb_user import User
from util.db_util import SessionClass
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

class User_Manage_WindowActions(user_manage.Ui_MainWindow, QMainWindow):
    """
    用户管理窗口的主要类，继承自PyQt5的QMainWindow和前端UI类
    """

    def __init__(self):
        """
        初始化用户管理窗口
        """
        super(user_manage.Ui_MainWindow, self).__init__()
        self.setupUi(self)
        window_manager = WindowManager()
        window_manager.register_window('user_manage', self)
        self.show_table()  # 显示用户表格

        # 连接按钮事件
        self.btn_return.clicked.connect(self.return_index)  # 返回首页
        self.addButton.clicked.connect(self.add_user)  # 添加用户

        # 设置日志
        path = '../state/user_status.txt'
        user = operate_user.read(path)
        userType = "Regular user" if user == 0 else "Administrator"
        
        logging.basicConfig(
            filename='../log/log.txt',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(userType)s - %(message)s'
        )
        
        logger = logging.getLogger()
        logger.addFilter(UserFilter(userType))

    def show_table(self):
        """
        显示用户表格
        """
        session = SessionClass()
        try:
            users = session.query(User).all()
            self.tableWidget.setRowCount(len(users))
            
            for i, user in enumerate(users):
                # 用户ID
                self.tableWidget.setItem(i, 0, QTableWidgetItem(str(user.user_id)))
                # 用户名
                self.tableWidget.setItem(i, 1, QTableWidgetItem(user.username))
                # 用户类型
                self.tableWidget.setItem(i, 2, QTableWidgetItem('管理员' if user.user_type == 'admin' else '普通用户'))
                # 邮箱
                self.tableWidget.setItem(i, 3, QTableWidgetItem(user.email or ''))
                # 电话
                self.tableWidget.setItem(i, 4, QTableWidgetItem(user.phone or ''))
                # 最后登录时间
                last_login = user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else ''
                self.tableWidget.setItem(i, 5, QTableWidgetItem(last_login))
            
            logging.info("User table refreshed successfully")
        except Exception as e:
            logging.error(f"Error displaying user table: {str(e)}")
            QMessageBox.critical(self, "错误", f"显示用户表格失败：{str(e)}")
        finally:
            session.close()

    def add_user(self):
        """
        添加新用户
        """
        # 获取用户输入
        username = self.nameIN.text().strip()
        password = self.pswdIN.text().strip()
        user_type = 'admin' if self.character_comboBox.currentText() == "管理员" else 'user'

        # 验证输入
        if not username or not password:
            QMessageBox.warning(self, "输入错误", "用户名和密码不能为空！")
            logging.warning("Attempted to add user but username or password was empty")
            return

        session = SessionClass()
        try:
            # 检查用户名是否已存在
            existing_user = session.query(User).filter(User.username == username).first()
            if existing_user:
                QMessageBox.warning(self, "错误", "用户名已存在！")
                logging.warning(f"Attempted to add user but username '{username}' already exists")
                return

            # 创建新用户
            new_user = User(
                user_id=f"user{int(time.time())}",  # 使用时间戳生成唯一ID
                username=username,
                password=password,
                email=f"{username}@example.com",  # 默认邮箱
                user_type=user_type,
                created_at=datetime.now()
            )
            
            session.add(new_user)
            session.commit()
            
            QMessageBox.information(self, "成功", "用户添加成功！")
            logging.info(f"New user '{username}' added successfully")
            
            # 清空输入框
            self.nameIN.clear()
            self.pswdIN.clear()
            
            # 刷新表格
            self.show_table()
            
        except Exception as e:
            session.rollback()
            logging.error(f"Error adding new user '{username}': {str(e)}")
            QMessageBox.critical(self, "错误", f"添加用户失败：{str(e)}")
        finally:
            session.close()

    def delete_user(self, user_id):
        """
        删除用户
        """
        session = SessionClass()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                session.delete(user)
                session.commit()
                logging.info(f"User '{user.username}' deleted successfully")
                return True
            return False
        except Exception as e:
            session.rollback()
            logging.error(f"Error deleting user: {str(e)}")
            return False
        finally:
            session.close()

    def update_password(self, user_id, new_password):
        """
        更新用户密码
        """
        session = SessionClass()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                user.password = new_password
                user.updated_at = datetime.now()
                session.commit()
                logging.info(f"Password updated for user '{user.username}'")
                return True
            return False
        except Exception as e:
            session.rollback()
            logging.error(f"Error updating password: {str(e)}")
            return False
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
    app = QApplication(sys.argv)
    demo_window = User_Manage_WindowActions()
    demo_window.show()
    sys.exit(app.exec_())