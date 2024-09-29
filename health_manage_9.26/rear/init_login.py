import sys
sys.path.append('../')
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from state import operate_user as operate_user
# 导入本页面的前端部分
import front.init_login as front_page

# 导入跳转页面的后端部分

from rear import login_rear
import logging

class UserFilter(logging.Filter):
    def __init__(self, userType):
        super().__init__()
        self.userType = userType

    def filter(self, record):
        record.userType = self.userType
        return True


# 注意这里定义的第一个界面的后端代码类需要继承两个类
class Index_WindowActions(front_page.Ui_MainWindow, QMainWindow):

    def __init__(self):
        super(front_page.Ui_MainWindow, self).__init__()
        # 创建界面
        self.setupUi(self)
        self.user_login_Button.clicked.connect(self.open_user_login)  # 用户登录
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
    def open_user_login(self):
        self.login = login_rear.Login_WindowActions()
        logging.info("Opening user login page.")
        self.close()  # 关闭当前窗口
        self.login.show()  # 显示登录窗口



if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 这里是界面的入口，在这里需要定义QApplication对象，之后界面跳转时不用再重新定义，只需要调用show()函数即可
    app = QApplication(sys.argv)
    # 显示创建的界面
    demo_window = Index_WindowActions()
    # demo_window.setStyleSheet("QMainWindow{background-color:#d4e2f4}")
    demo_window.show()
    sys.exit(app.exec_())
