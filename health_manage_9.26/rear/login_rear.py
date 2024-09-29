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

# 注意这里定义的第一个界面的后端代码类需要继承两个类
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
        self.login_pushButton.clicked.connect(self.admin_login)  # 登录
        self.return_pushButton.clicked.connect(self.return_index)  # 返回首页
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

    # 输入账号密码，登录管理员页面
    def admin_login(self):
        """
        处理管理员登录
        验证用户名和密码，根据验证结果执行相应操作
        """
        name = self.name_lineEdit.text()
        pwd = self.pwd_lineEdit.text()
        session = SessionClass()
        data = session.query(User).filter(User.name == name, User.pwd == pwd).first()
        session.close()

        # 检查用户名或密码是否为空
        if not name or not pwd:
            logging.warning("Admin login attempt failed: Username or password field is empty.")
            box = QMessageBox(QMessageBox.Information, "提示", "请输入用户名和密码")
            qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
            box.exec_()
            if box.clickedButton() == qyes:
                return

        # 检查数据是否为None（无效凭据）
        elif data is None:
            logging.warning(f"Admin login attempt failed: Incorrect username or password for username '{name}'.")
            box = QMessageBox(QMessageBox.Information, "提示", "用户名或密码错误")
            qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
            box.exec_()
            if box.clickedButton() == qyes:
                return

        else:  # 登录成功
            logging.info(f"Admin login successful for username '{name}'.")
            path = '../state/user_status.txt'
            if data.user_type == 1:
                operate_user.admin_user(path)  # 设置标志为1表示管理员访问

                # 进入管理员页面
                self.admin = admin_rear.AdminWindowActions()
                self.close()
                self.admin.show()
            else:
                operate_user.ordinary_user(path)  # 设置标志为0表示普通用户访问
                self.ordinary_user = index_rear.Index_WindowActions()
                self.close()
                self.ordinary_user.show()
                # 将当前用户名写入current_user.txt
            with open('../state/current_user.txt', 'w') as f:
                f.write(name)

            logging.info(f"Username '{name}' set as current user.")

    # 返回首页
    def return_index(self):
        """
        返回初始登录页面
        """
        self.index = init_login.Index_WindowActions()
        self.close()
        self.index.show()

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 这里是界面的入口，在这里需要定义QApplication对象，之后界面跳转时不用再重新定义，只需要调用show()函数即可
    app = QApplication(sys.argv)
    # 显示创建的界面
    demo_window = Login_WindowActions()
    demo_window.show()
    sys.exit(app.exec_())
