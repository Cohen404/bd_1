# -*- coding: utf-8 -*-

# 文件功能：登录界面的后端逻辑
# 该脚本实现了系统登录界面的功能，包括用户验证、登录处理、页面跳转等操作

import sys
from datetime import datetime
sys.path.append('../')
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
import state.operate_user as operate_user
# 导入本页面的前端部分
import front.login as login
from sql_model.tb_user import User
from util.db_util import SessionClass
from rear import init_login
# 导入跳转页面的后端部分
from rear import admin_rear
from rear import index_rear
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

class Login_WindowActions(login.Ui_MainWindow, QMainWindow):
    """
    登录窗口的主要类，继承自PyQt5的QMainWindow和前端UI类
    """

    def __init__(self):
        """
        初始化登录窗口
        """
        super(login.Ui_MainWindow, self).__init__()
        # 创建界面
        self.setupUi(self)
        # 初始化窗口管理器
        self.window_manager = WindowManager()
        self.window_manager.register_window('login', self)
        
        self.login_pushButton.clicked.connect(self.admin_login)  # 登录
        self.return_pushButton.clicked.connect(self.return_index)  # 返回首页
        
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

    def admin_login(self):
        """
        处理管理员登录
        验证用户名和密码，根据验证结果执行相应操作
        """
        username = self.name_lineEdit.text()
        password = self.pwd_lineEdit.text()
        session = SessionClass()
        
        try:
            # 检查用户名或密码是否为空
            if not username or not password:
                logging.warning("Login attempt failed: Username or password field is empty")
                box = QMessageBox(QMessageBox.Information, "提示", "请输入用户名和密码")
                qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
                box.exec_()
                if box.clickedButton() == qyes:
                    return

            # 使用新的字段名查询用户
            user = session.query(User).filter(
                User.username == username,
                User.password == password
            ).first()

            # 检查数据是否为None（无效凭据）
            if not user:
                logging.warning(f"Login attempt failed: Incorrect username or password for username '{username}'")
                box = QMessageBox(QMessageBox.Information, "提示", "用户名或密码错误")
                qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
                box.exec_()
                if box.clickedButton() == qyes:
                    return

            else:  # 登录成功
                logging.info(f"Login successful for username '{username}'")
                
                # 保存用户状态
                print(f"保存用户登录状态: ID={user.user_id}, 用户名={user.username}, 类型={user.user_type}")
                
                # 保存用户名到user_status.txt
                path = '../state/user_status.txt'
                operate_user.save_user(path, user.username)
                
                # 根据用户类型跳转到相应页面
                if user.user_type == 'admin':
                    self.admin = admin_rear.AdminWindowActions()
                    self.close()
                    self.admin.show()
                else:
                    self.ordinary_user = index_rear.Index_WindowActions()
                    self.close()
                    self.ordinary_user.show()

                # 更新最后登录时间
                user.last_login = datetime.now()
                session.commit()
                
                logging.info(f"User '{user.username}' logged in successfully")
                
        except Exception as e:
            logging.error(f"Login error: {str(e)}")
            QMessageBox.critical(self, "错误", f"登录失败：{str(e)}")
        finally:
            session.close()

    def return_index(self):
        """
        返回首页
        """
        self.index = init_login.Index_WindowActions()
        self.close()
        self.index.show()

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    demo_window = Login_WindowActions()
    window_manager = WindowManager()
    window_manager.register_window('login', demo_window)
    window_manager.show_window('login')
    sys.exit(app.exec_())
