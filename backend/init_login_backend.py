# 文件功能：初始登录界面的后端逻辑
# 该脚本实现了系统初始登录界面的功能，包括界面初始化、用户登录跳转等操作

import sys
sys.path.append('../')
import os
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from state import operate_user as operate_user
# 导入本页面的前端部分
import front.init_login_UI as front_page

# 导入跳转页面的后端部分
from backend import login_backend
import logging
from util.window_manager import WindowManager
from config import USER_STATUS_FILE, LOG_FILE
from model.tuili import EegModel
from model.tuili_int8 import EegModelInt8  # 添加INT8模型的导入
from util.db_util import SessionClass
from sql_model.tb_model import Model
import traceback

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
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename=LOG_FILE,  # 使用配置文件中定义的日志路径
            filemode='a',  # 追加模式
            force=True  # 强制重新配置日志
        )
        
        # 同时将日志输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)
        
        logging.info("初始化登录界面...")
        
        # 创建界面
        self.setupUi(self)
        # 连接用户登录按钮到对应的槽函数
        self.user_login_Button.clicked.connect(self.open_user_login)  # 用户登录
        
        # 注册窗口到WindowManager
        window_manager = WindowManager()
        window_manager.register_window('init_login', self)

        logging.info("开始预加载模型...")
        # 预加载应激评估模型
        self.preload_model()

    def preload_model(self):
        """
        预加载应激评估模型
        """
        try:
            logging.info("正在检查数据库中的模型信息...")
            # 检查数据库中的模型信息
            session = SessionClass()  # 使用正确的SessionClass
            model_info = session.query(Model).filter(Model.model_type == 0).first()
            session.close()
            
            if model_info:
                logging.info(f"找到模型信息: model_type=0, path={model_info.model_path}")
                if os.path.exists(model_info.model_path):
                    logging.info("模型文件存在，开始加载...")
                else:
                    logging.error(f"模型文件不存在: {model_info.model_path}")
                    return
            else:
                logging.error("数据库中未找到model_type=0的模型信息")
                return
                
            # 使用INT8量化模型的静态方法加载模型
            if EegModelInt8.load_static_model():
                logging.info("成功预加载量化模型")
            else:
                logging.error("预加载量化模型失败")
        except Exception as e:
            logging.error(f"模型预加载过程中发生错误: {str(e)}")
            logging.error(traceback.format_exc())

    def open_user_login(self):
        """
        打开用户登录页面
        """
        self.login = login_backend.Login_WindowActions()
        logging.info("Opening user login page.")
        window_manager = WindowManager()
        window_manager.register_window('login', self.login)
        window_manager.show_window('login')
        self.close()

if __name__ == '__main__':
    # 启用高DPI缩放
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    
    # 这里是界面的入口，在这里需要定义QApplication对象，之后界面跳转时不用再重新定义，只需要调用show()函数即可
    app = QApplication(sys.argv)
    
    # 显示创建的界面
    demo_window = Index_WindowActions()
    window_manager = WindowManager()
    window_manager.register_window('init_login', demo_window)
    window_manager.show_window('init_login')
    
    # 进入应用的主事件循环
    sys.exit(app.exec_())
