# 文件功能：系统主页面的后端逻辑
# 该脚本实现了系统主页面的功能，包括界面初始化、用户状态管理、页面跳转等操作

import sys
sys.path.append('../')
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from state import operate_user as operate_user
# 导入本页面的前端部分
import front.index_UI as front_page

# 导入跳转页面的后端部分
from backend import data_manage_backend
from backend import health_evaluate_backend
from backend import results_manage_backend
from backend import login_backend
from sql_model.tb_result import Result
from util.db_util import SessionClass
import logging

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


# 注意这里定义的第一个界面的后端代码类需要继承两个类
class Index_WindowActions(front_page.Ui_MainWindow, QMainWindow):
    """
    系统主页面的主要类，继承自PyQt5的QMainWindow和前端UI类
    """

    def __init__(self):
        """
        初始化系统主页面
        """
        super(front_page.Ui_MainWindow, self).__init__()
        # 创建界面
        self.setupUi(self)
        # 打开首页将用户状态修改为0（普通用户）,确保首次打开系统为普通用户身份
        path = USER_STATUS_FILE
        user = operate_user.read(path)
        if user == '1':
            operate_user.ordinary_user(path)

        # self.show_nav()  # 调用show_nav方法显示header,bottom的内容

        # 连接按钮信号到对应的槽函数
        self.health_assess_Button.clicked.connect(self.open_health_evaluate)  # 健康评估
        self.data_view_Button.clicked.connect(self.open_data_view)  # 数据查看
        self.results_view_Button.clicked.connect(self.open_results_view)  # 结果查看
        self.admin_login_Button.clicked.connect(self.open_admin_login)  # 管理员页面

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


    def show_nav(self):
        """
        显示导航栏和状态信息（当前未使用）
        """
        # header
        session = SessionClass()
        result = session.query(Result).order_by(Result.id.desc()).first()
        session.close()

    def open_health_evaluate(self):
        """
        打开健康评估页面
        """
        self.health_evaluate = health_evaluate_backend.Health_Evaluate_WindowActions()
        logging.info("Opening health evaluation page.")
        self.close()  # 关闭当前窗口
        self.health_evaluate.show()  # 显示健康评估窗口

    def open_data_view(self):
        """
        打开数据查看页面
        """
        self.data_view = data_manage_backend.Data_View_WindowActions()
        logging.info("Opening data view page.")
        self.close()  # 关闭当前窗口
        self.data_view.show()  # 显示数据查看窗口

    def open_results_view(self):
        """
        打开结果查看页面
        """
        self.results_view = results_manage_backend.Results_View_WindowActions()
        logging.info("Opening results view page.")
        self.close()  # 关闭当前窗口
        self.results_view.show()  # 显示结果查看窗口

    def open_admin_login(self):
        """
        打开管理员登录页面
        """
        self.login = login_backend.Login_WindowActions()
        logging.info("Opening admin login page.")
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
