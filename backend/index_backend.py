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
from backend.help_window_backend import HelpWindow

# 导入跳转页面的后端部分
from backend import data_manage_backend
from backend import health_evaluate_backend
from backend import results_manage_backend
from backend import login_backend
from backend import change_password_backend
from sql_model.tb_result import Result
from util.db_util import SessionClass
from util.window_manager import WindowManager
import logging

from config import (
    USER_STATUS_FILE, 
    CURRENT_USER_FILE, 
    LOG_FILE, 
    MODEL_STATUS_FILE,
    DATA_DIR
)

from sql_model.tb_user import User
from sql_model.tb_role import Role
from sql_model.tb_permission import Permission
from sql_model.tb_user_role import UserRole
from sql_model.tb_role_permission import RolePermission


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
        self.setupUi(self)
        
        # 获取当前用户ID
        with open(CURRENT_USER_FILE, 'r') as f:
            self.user_id = f.read().strip()
            
        # 获取用户权限并显示对应按钮
        self.show_buttons_by_permission()
        
        # 连接按钮信号
        self.health_assess_Button.clicked.connect(self.open_health_evaluate)
        self.data_view_Button.clicked.connect(self.open_data_view)
        self.results_view_Button.clicked.connect(self.open_results_view)
        self.btn_help.clicked.connect(self.open_help)
        self.btn_return.clicked.connect(self.return_login)
        self.change_pwd_Button.clicked.connect(self.open_change_pwd)

        # 配置日志
        path = USER_STATUS_FILE
        user = operate_user.read(path)
        userType = "Regular user" if user == 0 else "Administrator"
        logging.basicConfig(
            filename=LOG_FILE,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(userType)s - %(message)s'
        )
        logger = logging.getLogger()
        logger.addFilter(UserFilter(userType))

        window_manager = WindowManager()
        window_manager.register_window('index', self)

    def get_user_permissions(self, user_id):
        """
        获取用户的权限列表
        
        参数:
        user_id (str): 用户ID
        
        返回:
        list: 权限ID列表
        """
        session = SessionClass()
        try:
            # 获取用户角色
            user_role = session.query(UserRole).filter(UserRole.user_id == user_id).first()
            if not user_role:
                return []
                
            # 获取角色的所有权限
            role_permissions = session.query(RolePermission).filter(
                RolePermission.role_id == user_role.role_id
            ).all()
            
            # 返回权限ID列表
            return [rp.permission_id for rp in role_permissions]
        except Exception as e:
            logging.error(f"Error getting user permissions: {str(e)}")
            return []
        finally:
            session.close()
            
    def show_buttons_by_permission(self):
        """
        根据用户权限显示对应的功能按钮,并实现紧凑排列
        """
        # 获取用户权限列表
        permissions = self.get_user_permissions(self.user_id)
        
        # 默认隐藏所有按钮
        self.health_assess_Button.hide()
        self.data_view_Button.hide()
        self.results_view_Button.hide()
        self.change_pwd_Button.hide()
        
        # 获取所有可见按钮
        visible_buttons = []
        if 'PERM_DATA_COLLECTION' in permissions:
            visible_buttons.append(self.health_assess_Button)
        if 'PERM_DATA_MANAGE' in permissions:
            visible_buttons.append(self.data_view_Button)
        if 'PERM_RESULT_VIEW' in permissions:
            visible_buttons.append(self.results_view_Button)
        if 'PERM_CHANGE_PWD' in permissions:
            visible_buttons.append(self.change_pwd_Button)
        
        # 计算每行显示的按钮数量
        total_buttons = len(visible_buttons)
        buttons_per_row = (total_buttons + 1) // 2  # 向上取整,确保第一行更多
        
        # 重新排列按钮位置
        for i, button in enumerate(visible_buttons):
            row = 1 if i < buttons_per_row else 3  # 使用1和3行,保持间距
            col = (i % buttons_per_row) * 2 + 1    # 使用奇数列,保持间距
            self.gridLayout.addWidget(button, row, col, 1, 1)
            button.show()

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
        window_manager = WindowManager()
        window_manager.register_window('health_evaluate', self.health_evaluate)
        window_manager.show_window('health_evaluate')
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

    def open_change_pwd(self):
        """
        打开密码修改页面
        """
        self.change_pwd = change_password_backend.change_pwd_Controller()
        logging.info("Opening password change page.")
        window_manager = WindowManager()
        window_manager.register_window('change_pwd', self.change_pwd)
        window_manager.show_window('change_pwd')
        self.close()

    def return_login(self):
        """
        返回登录页面
        """
        self.login = login_backend.Login_WindowActions()
        logging.info("Returning to login page.")
        window_manager = WindowManager()
        window_manager.register_window('login', self.login)
        window_manager.show_window('login')
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
    demo_window = Index_WindowActions()
    # demo_window.setStyleSheet("QMainWindow{background-color:#d4e2f4}")
    demo_window.show()
    sys.exit(app.exec_())
