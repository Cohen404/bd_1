"""
管理员界面的后端实现

该模块实现了管理员界面的各项功能,包括界面初始化、页面跳转等。
"""

import sys

from front import param_manage_UI

sys.path.append('../')
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
import state.operate_user as operate_user
# 导入本页面的前端部分
import front.admin_index_UI as admin_index_UI
from backend import change_password_backend, index_backend, login_backend, model_manage_backend, param_manage_backend
from backend.help_window_backend import HelpWindow
# 导入跳转页面的后端部分
from backend import user_manage_backend
from backend import data_manage_backend
from backend import health_evaluate_backend
from backend import results_manage_backend
from backend import log_manage_backend
from sql_model.tb_result import Result
from util.db_util import SessionClass
import logging
from util.window_manager import WindowManager
from config import USER_STATUS_FILE, LOG_FILE

class UserFilter(logging.Filter):
    """
    用户类型日志过滤器
    """
    def __init__(self, userType):
        super().__init__()
        self.userType = userType

    def filter(self, record):
        record.userType = self.userType
        return True

# 注意这里定义的第一个界面的后端代码类需要继承两个类
class AdminWindowActions(admin_index_UI.Ui_MainWindow, QMainWindow):
    """
    管理员窗口操作类
    
    实现管理员界面的各项功能
    """

    def __init__(self):
        """
        初始化管理员窗口
        """
        super(admin_index_UI.Ui_MainWindow, self).__init__()
        # 创建界面
        self.setupUi(self)
        self.show_nav()  # 调用show_nav方法显示header,bottom的内容

        # 连接按钮点击事件
        self.btn_return.clicked.connect(self.return_index)  # 返回首页
        self.health_assess_Button.clicked.connect(self.open_health_evaluate)  # 健康评估
        self.data_view_Button.clicked.connect(self.open_data_view)  # 数据查看
        self.results_view_Button.clicked.connect(self.open_results_view)  # 结果查看
        self.model_manage_pushButton.clicked.connect(self.open_model_control_view)
        self.user_manage_pushButton.clicked.connect(self.open_user_manage_view)
        self.parameter_pushButton.clicked.connect(self.open_param_control_view)
        self.change_pwd_Button.clicked.connect(self.open_change_pwd_view)
        self.log_manage_pushButton.clicked.connect(self.open_log_manage_view)
        self.btn_help.clicked.connect(self.open_help)  # 帮助按钮

        # 使用配置文件中的路径
        user = operate_user.read(USER_STATUS_FILE)
        userType = "Regular user" if user == 0 else "Administrator"

        # 配置 logging 模块，使用配置文件中的路径
        logging.basicConfig(
            filename=LOG_FILE,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(userType)s - %(message)s'
        )

        # 添加过滤器
        logger = logging.getLogger()
        logger.addFilter(UserFilter(userType))

        window_manager = WindowManager()
        window_manager.register_window('admin', self)

    def show_nav(self):
        """
        显示导航栏
        """
        session = SessionClass()
        result = session.query(Result).order_by(Result.id.desc()).first()
        session.close()

    # btn_return返回首页
    def return_index(self):
        """
        返回首页
        """
        operate_user.ordinary_user(USER_STATUS_FILE)  # 使用配置文件中的路径
        logging.info("Switched to regular user mode. Login page is being opened.")
        self.login = login_backend.Login_WindowActions()
        window_manager = WindowManager()
        window_manager.register_window('login', self.login)
        window_manager.show_window('login')
        self.close()

    # 打开健康评估页面
    def open_health_evaluate(self):
        """
        打开健康评估页面
        """
        self.health_evaluate = health_evaluate_backend.Health_Evaluate_WindowActions()
        logging.info("Opening health evaluation page.")
        window_manager = WindowManager()
        window_manager.register_window('health_evaluate', self.health_evaluate)
        window_manager.show_window('health_evaluate')
        self.close()

    def open_log_manage_view(self):
        """
        打开日志管理页面
        """
        self.log_manage = log_manage_backend.Log_Manage_WindowActions()
        logging.info("Opening log management page.")
        window_manager = WindowManager()
        window_manager.register_window('log_manage', self.log_manage)
        window_manager.show_window('log_manage')
        self.close()

    def open_data_view(self):
        """
        打开数据查看页面
        """
        self.data_view = data_manage_backend.Data_View_WindowActions()
        logging.info("Opening data view page.")
        window_manager = WindowManager()
        window_manager.register_window('data_view', self.data_view)
        window_manager.show_window('data_view')
        self.close()

    def open_results_view(self):
        """
        打开结果查看页面
        """
        self.results_view = results_manage_backend.Results_View_WindowActions()
        logging.info("Opening results view page.")
        window_manager = WindowManager()
        window_manager.register_window('results_view', self.results_view)
        window_manager.show_window('results_view')
        self.close()

    def open_model_control_view(self):
        """
        打开模型控制页面
        """
        self.model_view = model_manage_backend.model_control_Controller()
        logging.info("Opening model control page.")
        window_manager = WindowManager()
        window_manager.register_window('model_control', self.model_view)
        window_manager.show_window('model_control')
        self.close()

    def open_change_pwd_view(self):
        """
        打开修改密码页面
        """
        self.change_pwd = change_password_backend.change_pwd_Controller()
        logging.info("Opening password change page.")
        window_manager = WindowManager()
        window_manager.register_window('change_pwd', self.change_pwd)
        window_manager.show_window('change_pwd')
        self.close()

    def open_user_manage_view(self):
        """
        打开用户管理页面
        """
        self.user_manage = user_manage_backend.User_Manage_WindowActions()
        logging.info("Opening user management page.")
        window_manager = WindowManager()
        window_manager.register_window('user_manage', self.user_manage)
        window_manager.show_window('user_manage')
        self.close()

    def open_param_control_view(self):
        """
        打开参数控制页面
        """
        self.param_control = param_manage_backend.ParamControl()
        logging.info("Opening parameter control page.")
        window_manager = WindowManager()
        window_manager.register_window('param_control', self.param_control)
        window_manager.show_window('param_control')
        self.close()

    def open_help(self):
        """
        打开帮助窗口
        """
        self.help_window = HelpWindow()
        logging.info("Opening help window.")
        # 不需要使用 WindowManager，因为帮助窗口是独立的
        # 不需要关闭当前窗口
        # 帮助窗口会在 HelpWindow 类的 __init__ 中自动显示

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 这里是界面的入口，在这里需要定义QApplication对象，之后界面跳转时不用再重新定义，只需要调用show()函数即可
    app = QApplication(sys.argv)
    # 显示创建的界面
    demo_window = AdminWindowActions()
    window_manager = WindowManager()
    window_manager.register_window('admin', demo_window)
    window_manager.show_window('admin')
    sys.exit(app.exec_())