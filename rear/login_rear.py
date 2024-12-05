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
import hashlib
from config import USER_STATUS_FILE, CURRENT_USER_FILE, LOG_FILE

def hash_password(password):
    """使用SHA256加密密码"""
    return hashlib.sha256(password.encode()).hexdigest()

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
        
        # 只绑定一个登录处理函数
        self.login_pushButton.clicked.connect(self.handle_login)
        self.return_pushButton.clicked.connect(self.return_index)
        
        # 添加密码框回车事件绑定
        self.pwd_lineEdit.returnPressed.connect(self.handle_login)

        # 配置基本日志格式
        logging.basicConfig(
            filename=LOG_FILE,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(userType)s - %(message)s'
        )

    def handle_login(self):
        """统一的登录处理函数"""
        try:
            # 获取用户输入
            username = self.name_lineEdit.text().strip()
            password = self.pwd_lineEdit.text().strip()

            # 验证输入不为空
            if not username or not password:
                QMessageBox.warning(self, "警告", "用户名和密码不能为空")
                return

            # 对密码进行SHA256加密
            hashed_password = hash_password(password)

            # 连接数据库验证用户
            session = SessionClass()
            try:
                user = session.query(User).filter(
                    User.username == username,
                    User.password == hashed_password
                ).first()

                if user:
                    # 保存当前用户信息
                    with open(CURRENT_USER_FILE, 'w') as f:
                        f.write(str(user.user_id))

                    # 保存用户类型
                    is_admin = '1' if user.user_type == 'admin' else '0'
                    with open(USER_STATUS_FILE, 'w') as f:
                        f.write(is_admin)

                    # 设置用户类型并更新日志过滤器
                    userType = "Administrator" if is_admin == '1' else "Regular user"
                    logger = logging.getLogger()
                    # 移除旧的过滤器
                    for filter in logger.filters:
                        if isinstance(filter, UserFilter):
                            logger.removeFilter(filter)
                    # 添加新的过滤器
                    logger.addFilter(UserFilter(userType))

                    # 更新最后登录时间
                    user.last_login = datetime.now()
                    session.commit()

                    logging.info(f"User {username} logged in successfully")

                    # 根据用户类型打开相应界面
                    if user.user_type == 'admin':
                        self.admin = admin_rear.AdminWindowActions()
                        self.admin.show()
                    else:
                        self.index = index_rear.Index_WindowActions()
                        self.index.show()

                    self.close()

                else:
                    QMessageBox.warning(self, "警告", "用户名或密码错误")
                    logging.warning(f"Failed login attempt for username: {username}")

            finally:
                session.close()

        except Exception as e:
            logging.error(f"Login error: {str(e)}")
            QMessageBox.critical(self, "错误", f"登录时发生错误：{str(e)}")

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
