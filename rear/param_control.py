# 文件功能：参数控制界面的后端逻辑
# 该脚本实现了参数控制界面的功能，包括参数显示、保存、更新等操作，以及与数据库的交互

import os
import sys
import time
import front.param_control_UI as Ui_param_Control
from PyQt5 import QtCore
sys.path.append('../')
from datetime import datetime
from functools import partial
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QRadioButton, QTableWidgetItem, QWidget, QPushButton, QHBoxLayout, \
    QMessageBox, QFileDialog, QInputDialog
import shutil
from front.model_control_UI import Ui_model_Control
from rear import index_rear, admin_rear
from state import operate_user
from util.db_util import SessionClass
from sql_model.tb_parameters import Parameters
from sql_model.tb_user import User

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

class ParamControl(Ui_param_Control.Ui_param_Control, QWidget):
    """
    参数控制界面的主要类，继承自前端UI类和QWidget
    """
    def __init__(self):
        """
        初始化参数控制界面
        """
        super(Ui_param_Control.Ui_param_Control, self).__init__()
        self.init_ui()
        self.SHOWUi()

        self.return_btn.clicked.connect(self.returnIndex)
        self.save_button.clicked.connect(self.savetoDB)
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

        # 添加��滤器
        logger = logging.getLogger()
        logger.addFilter(UserFilter(userType))

    # btn_return返回首页
    def returnIndex(self):
        """
        返回到相应的主页面
        根据用户类型返回到管理员或普通用户页面
        """
        path = '../state/user_status.txt'
        user_status = operate_user.read(path)
        
        try:
            # 创建新窗口前先保存引用
            if user_status == '1':  # 管理员
                self._index_window = admin_rear.AdminWindowActions()
            else:  # 普通用户
                self._index_window = index_rear.Index_WindowActions()
            
            # 先显示新窗口
            self._index_window.show()
            # 再隐藏当前窗口
            self.hide()
            # 最后关闭当前窗口
            self.close()
            
            logging.info("Returned to index page successfully")
        except Exception as e:
            logging.error(f"Error in return_index: {str(e)}")
            QMessageBox.critical(self, "错误", f"返回主页时发生错误：{str(e)}")


    def savetoDB(self):
        """
        保存参数到数据库的处理函数
        """
        logging.info("Starting database save operation.")

        session = SessionClass()

        # 查找现有记录
        existing_data = session.query(Parameters).filter(Parameters.id == 0).first()

        if existing_data is not None:
            # 更新现有记录
            logging.info("Updating existing Parameters record.")
            existing_data.frequency = int(self.sample_freq.text())
            existing_data.electrode_count = int(self.electrode_numbers.text())
            existing_data.eeg_location = str(self.eeg_location.text())
            existing_data.data_format = 1  # 或者 self.data_format.currentText()
            logging.info(
                f"Updated frequency to {existing_data.frequency}, electrode_count to {existing_data.electrode_count}, "
                f"eeg_location to {existing_data.eeg_location}, data_format to {existing_data.data_format}.")
        else:
            # 创建新记录
            logging.info("Creating new Parameters record.")
            new_data = Parameters(
                eeg_location=str(self.eeg_location.text()),
                frequency=int(self.sample_freq.text()),
                electrode_count=int(self.electrode_numbers.text()),
                data_format=1  # 或者 self.data_format.currentText()
            )
            session.add(new_data)
            logging.info(f"Added new Parameters record with frequency {new_data.frequency}, "
                         f"electrode_count {new_data.electrode_count}, eeg_location {new_data.eeg_location}, "
                         f"data_format {new_data.data_format}.")

        try:
            session.commit()
            logging.info("Database transaction committed successfully.")
        except Exception as e:
            session.rollback()
            logging.error(f"Failed to commit database transaction: {e}")
            raise  # Re-raise the exception after logging

        finally:
            session.close()
            logging.info("Database session closed.")

        self.SHOWUi()
        logging.info("SHOWUi method called after database operation.")

    def SHOWUi(self):
        """
        显示参数控制界面的UI，并从数据库加载最新的参数值
        """
        session = SessionClass()
        data = session.query(Parameters).first()  # 获取最新的记录
        session.close()
        if data is not None:
            # 将数据库中的值设置到相应的输入框中
            self.eeg_location.setText(str(data.eeg_location))
            self.sample_freq.setText(str(data.frequency))
            self.electrode_numbers.setText(str(data.electrode_count))
            # index = self.data_format.findText(str(data.data_format), QtCore.Qt.MatchFixedString)
            # if index >= 0:
            #     self.data_format.setCurrentIndex(index)
