# 文件功能：初始登录界面的后端逻辑
# 该脚本实现了系统初始登录界面的功能，包括界面初始化、用户登录跳转等操作

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

# 注意这里定义的第一个界面的后端代码类需要继承两个类
class Index_WindowActions(front_page.Ui_MainWindow, QMainWindow):
    """
    初始登录界面的主要类，继承自PyQt5的QMainWindow和前端UI类
    """

    def __init__(self):
        """
        初始化初始登录界面
        """
        super(front_page.Ui_MainWindow, self).__init__()
        # 创建界面
        self.setupUi(self)
        # 连接用户登录按钮到对应的槽函数
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
        """
        打开用户登录页面
        """
        self.login = login_rear.Login_WindowActions()
        logging.info("Opening user login page.")
        self.close()  # 关闭当前窗口
        self.login.show()  # 显示登录窗口

if __name__ == '__main__':
    # 启用高DPI缩放
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    
    # 这里是界面的入口，在这里需要定义QApplication对象，之后界面跳转时不用再重新定义，只需要调用show()函数即可
    app = QApplication(sys.argv)
    
    # 显示创建的界面
    demo_window = Index_WindowActions()
    # demo_window.setStyleSheet("QMainWindow{background-color:#d4e2f4}")  # 设置主窗口背景颜色（当前被注释）
    demo_window.show()
    
    # 进入应用的主事件循环
    sys.exit(app.exec_())
