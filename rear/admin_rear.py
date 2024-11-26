"""
管理员界面的后端实现

该模块实现了管理员界面的各项功能,包括界面初始化、页面跳转等。
"""

import sys

from front import param_control_UI

sys.path.append('../')
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
import state.operate_user as operate_user
# 导入本页面的前端部分
import front.admin as admin
from rear import login_rear
# 导入跳转页面的后端部分
from rear import index_rear, change_pwd_controller, model_control_controller,  param_control, \
    user_manage_rear
from rear import data_view_rear
from rear import health_evaluate_rear
from rear import results_view_rear
from rear import log_manage_rear
from sql_model.tb_result import Result
from util.db_util import SessionClass
import logging
from util.window_manager import WindowManager

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
class AdminWindowActions(admin.Ui_MainWindow, QMainWindow):
    """
    管理员窗口操作类
    
    实现管理员界面的各项功能
    """

    def __init__(self):
        """
        初始化管理员窗口
        """
        super(admin.Ui_MainWindow, self).__init__()
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
        path = '../state/user_status.txt'
        operate_user.ordinary_user(path)  # 将flag改为0，退出管理员操作
        logging.info("Switched to regular user mode. Login page is being opened.")
        self.login=login_rear.Login_WindowActions()
        self.close()
        self.login.show()

    # 打开健康评估页面
    def open_health_evaluate(self):
        """
        打开健康评估页面
        """
        self.health_evaluate = health_evaluate_rear.Health_Evaluate_WindowActions()
        logging.info("Opening health evaluation page.")
        self.close()
        self.health_evaluate.show()

    def open_log_manage_view(self):
        """
        打开日志管理页面
        """
        self.log_manage = log_manage_rear.Log_Manage_WindowActions()
        logging.info("Opening log management page.")
        self.close()
        self.log_manage.show()

    def open_data_view(self):
        """
        打开数据查看页面
        """
        self.data_view = data_view_rear.Data_View_WindowActions()
        logging.info("Opening data view page.")
        self.close()
        self.data_view.show()

    def open_results_view(self):
        """
        打开结果查看页面
        """
        self.results_view = results_view_rear.Results_View_WindowActions()
        logging.info("Opening results view page.")
        self.close()
        self.results_view.show()

    def open_model_control_view(self):
        """
        打开模型控制页面
        """
        self.model_view = model_control_controller.model_control_Controller()
        logging.info("Opening model control page.")
        self.close()
        self.model_view.show()

    def open_change_pwd_view(self):
        """
        打开修改密码页面
        """
        self.change_pwd = change_pwd_controller.change_pwd_Controller()
        logging.info("Opening password change page.")
        self.close()
        self.change_pwd.show()

    def open_user_manage_view(self):
        """
        打开用户管理页面
        """
        self.user_manage = user_manage_rear.User_Manage_WindowActions()
        logging.info("Opening user management page.")
        self.close()
        self.user_manage.show()

    def open_param_control_view(self):
        """
        打开参数控制页面
        """
        self.param_control = param_control.ParamControl()
        logging.info("Opening parameter control page.")
        self.close()
        self.param_control.show()

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 这里是界面的入口，在这里需要定义QApplication对象，之后界面跳转时不用再重新定义，只需要调用show()函数即可
    app = QApplication(sys.argv)
    # 显示创建的界面
    demo_window = AdminWindowActions()
    demo_window.show()
    sys.exit(app.exec_())