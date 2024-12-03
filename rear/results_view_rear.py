# 文件功能：结果查看界面的后端逻辑
# 该脚本实现了结果查看界面的功能，包括显示评估结果列表、查看详细结果、删除结果等操作

import os
import sys

import logging
from pyqt5_plugins.examplebutton import QtWidgets

sys.path.append('../')
import time
from datetime import datetime, timedelta
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsPixmapItem, QGraphicsScene, QMessageBox, 
    QTableWidgetItem, QInputDialog
)
import state.operate_user as operate_user
# 导入本页面的前端部分
import front.results_view as results_view

# 导入跳转页面的后端部分
from rear import index_rear
from rear import admin_rear
from sql_model.tb_data import Data
from sql_model.tb_result import Result
from sql_model.tb_user import User
from util.db_util import SessionClass
from sql_model.tb_user import User
from util.window_manager import WindowManager

# import admin_rear
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

class Results_View_WindowActions(results_view.Ui_MainWindow, QMainWindow):
    """
    结果查看窗口的主要类，继承自PyQt5的QMainWindow和前端UI类
    """

    def __init__(self):
        """
        初始化结果查看窗口
        """
        super(results_view.Ui_MainWindow, self).__init__()
        self.setupUi(self)
        self._index_window = None

        # 获取当前用户信息
        self.user_id, is_admin = self.get_current_user()
        self.user_type = is_admin

        # 添加通道选择下拉框
        self.channel_comboBox = QtWidgets.QComboBox(self)
        self.channel_comboBox.setGeometry(QtCore.QRect(10, 10, 200, 30))
        self.channel_comboBox.addItems([
            "Theta/Alpha/Beta/Gamma功率",
            "均分频带",
            "时域特征",
            "时频域特征",
            "微分熵"
        ])
        # 将下拉框添加到EEG特征图区域
        self.verticalLayout_2.insertWidget(1, self.channel_comboBox)  # 插入到标题和图形视图之间

        # 设置表格列
        self.tableWidget.setColumnCount(7)  # 设置为7列，包括查看按钮列
        self.tableWidget.setHorizontalHeaderLabels([
            'ID', '用户名', '评估时间', '普通应激', '抑郁', '焦虑', '操作'
        ])

        # 设置表格样式
        self.tableWidget.horizontalHeader().setStyleSheet(
            "QHeaderView::section{background-color:#5c8ac3;font-size:11pt;color:white;}")
        self.tableWidget.setStyleSheet(
            "QTableWidget{background-color:#d4e2f4; alternate-background-color:#e8f1ff;}")
        
        # 设置列宽
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)  # ID列
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)  # 用户名列
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)          # 评估时间列
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)  # 普通应激列
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)  # 抑郁列
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)  # 焦虑列
        header.setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeToContents)  # 操作列

        # 设置下拉框样式
        self.channel_comboBox.setStyleSheet('''
            QComboBox {
                background-color: white;
                border: 1px solid #5c8ac3;
                border-radius: 3px;
                padding: 1px 18px 1px 3px;
                min-width: 6em;
            }
            QComboBox:hover {
                border: 1px solid #4a7ab3;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(../resources/down_arrow.png);
                width: 12px;
                height: 12px;
            }
        ''')

        # 显示表格内容
        self.show_table()

        # 从文件中读取用户类型并设置userType
        path = '../state/user_status.txt'
        user = operate_user.read(path)
        userType = "Regular user" if user == 0 else "Administrator"

        # 配置日志
        logging.basicConfig(
            filename='../log/log.txt',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(userType)s - %(message)s'
        )
        logger = logging.getLogger()
        logger.addFilter(UserFilter(userType))

        # 连接按钮事件
        self.btn_return.clicked.connect(self.return_index)

        # 注册窗口
        window_manager = WindowManager()
        window_manager.register_window('results_view', self)

    def get_user_type(self, user_id):
        """
        获取用户类型
        """
        session = SessionClass()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                return user.user_type == 'admin'  # 返回布尔值：True表示管理员，False表示普通用户
            return False
        except Exception as e:
            logging.error(f"Error getting user type: {str(e)}")
            return False
        finally:
            session.close()

    def get_current_user(self):
        """
        获取当前用户信息
        返回: (user_id, is_admin)
        """
        try:
            # 检查文件是否存在
            import os
            if not os.path.exists('../state/current_user.txt'):
                logging.error("Current user file not found")
                QMessageBox.warning(self, "错误", "未找到当前用户信息文件")
                return None, False

            # 读取用户ID
            with open('../state/current_user.txt', 'r') as f:
                user_id = f.read().strip()
            print(f"从current_user.txt读取到用户ID: {user_id}")

            if not user_id:
                logging.error("Current user ID is empty")
                QMessageBox.warning(self, "错误", "当前用户ID为空")
                return None, False
            
            # 读取用户类型
            path = '../state/user_status.txt'
            user_type = operate_user.read(path)
            print(f"从user_status.txt读取到用户类型: {user_type}")
            is_admin = (user_type == '1')
            
            # 查询用户信息
            session = SessionClass()
            user = session.query(User).filter(User.user_id == user_id).first()
            session.close()
            
            if user:
                print(f"从数据库查询到用户信息: ID={user.user_id}, 用户名={user.username}, 类型={user.user_type}")
                # 验证用户类型是否匹配
                db_is_admin = (user.user_type == 'admin')
                if db_is_admin != is_admin:
                    print(f"警告：文件中的用户类型({is_admin})与数据库中的用户类型({db_is_admin})不匹配")
                return user.user_id, db_is_admin
            else:
                logging.error(f"User not found for ID: {user_id}")
                QMessageBox.warning(self, "错误", "在数据库中未找到当前用户")
                return None, False

        except Exception as e:
            logging.error(f"Error getting current user: {str(e)}")
            print(f"获取用户信息时出错: {str(e)}")
            QMessageBox.critical(self, "错误", f"获取当前用户信息失败：{str(e)}")
            return None, False

    def show_nav(self):
        """
        显示导航栏和状态信息
        """
        # header
        session = SessionClass()
        result = session.query(Result).order_by(Result.id.desc()).first()
        session.close()
        # 获取tb_result表中最新的一条记录，得到result对象
        if result is not None:  # result存在
            result_1 = result.result_1  # 应激状态
            result_2 = result.result_2  # 抑郁状态
            result_3 = result.result_3  # 焦虑状态

            if (result_1):
                self.health_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; border-radius: 16px; border: 2px solid white; background: red"
                )
            else:
                self.health_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; border-radius: 16px; border: 2px solid white; background: green"
                )

            if (result_2):
                self.acoustic_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; border-radius: 16px; border: 2px solid white; background: red"
                )
            else:
                self.acoustic_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; border-radius: 16px; border: 2px solid white; background: green"
                )

            if (result_3):
                self.mechanical_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; border-radius: 16px; border: 2px solid white; background: red"
                )
            else:
                self.mechanical_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; border-radius: 16px; border: 2px solid white; background: green"
                )

    def show_table(self):
        """
        显示结果表格
        """
        session = SessionClass()
        try:
            # 获取当前用户ID
            user_id = self.user_id
            if not user_id:
                QMessageBox.warning(self, "错误", "无法获取当前用户信息")
                return

            # 查询结果
            if self.user_type:  # 管理员可以看到所有结果
                results = session.query(Result).all()
            else:  # 普通用户只能看到自己的结果
                results = session.query(Result).filter(Result.user_id == user_id).all()

            # 显示结果
            self.tableWidget.setRowCount(len(results))
            for i, result in enumerate(results):
                # 获取用户信息
                user = session.query(User).filter(User.user_id == result.user_id).first()
                username = user.username if user else "未知用户"

                # 设置表格内容
                self.tableWidget.setItem(i, 0, QTableWidgetItem(str(result.id)))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(username))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(
                    result.result_time.strftime('%Y-%m-%d %H:%M:%S') if result.result_time else ''))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(str(result.result_1)))  # 显示原始值
                self.tableWidget.setItem(i, 4, QTableWidgetItem(str(result.result_2)))  # 显示原始值
                self.tableWidget.setItem(i, 5, QTableWidgetItem(str(result.result_3)))  # 显示原始值

                # 添加查看按钮
                view_btn = QtWidgets.QPushButton('查看')
                view_btn.setStyleSheet('''
                    QPushButton {
                        background-color: #5c8ac3;
                        color: white;
                        border-radius: 5px;
                        padding: 5px 15px;
                        min-width: 60px;
                        margin: 2px 10px;
                    }
                    QPushButton:hover {
                        background-color: #4a7ab3;
                    }
                ''')
                view_btn.clicked.connect(lambda checked, row=i: self.view_details(row))
                self.tableWidget.setCellWidget(i, 6, view_btn)

            # 启用表格滚动
            self.tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            
            # 更新当前评估结果显示
            self.update_current_status()

        except Exception as e:
            logging.error(f"Error displaying results table: {str(e)}")
            QMessageBox.critical(self, "错误", f"显示结果表格失败：{str(e)}")
        finally:
            session.close()

    def update_current_status(self):
        """更新当前评估结果状态显示"""
        session = SessionClass()
        try:
            # 获取最新评估结果
            result = session.query(Result).order_by(Result.result_time.desc()).first()
            if result:
                # 更新普通应激状态
                self.health_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; "
                    "border-radius: 16px; border: 2px solid white; "
                    f"background: {'red' if result.result_1 >= 50 else 'gray'}"
                )
                
                # 更新抑郁状态
                self.acoustic_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; "
                    "border-radius: 16px; border: 2px solid white; "
                    f"background: {'red' if result.result_2 >= 50 else 'gray'}"
                )
                
                # 更新焦虑状态
                self.mechanical_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; "
                    "border-radius: 16px; border: 2px solid white; "
                    f"background: {'red' if result.result_3 >= 50 else 'gray'}"
                )
        finally:
            session.close()

    def view_details(self, row):
        """查看详细信息"""
        try:
            result_id = int(self.tableWidget.item(row, 0).text())
            session = SessionClass()
            result = session.query(Result).filter(Result.id == result_id).first()
            
            if result:
                # 获取关联的数据记录
                data = session.query(Data).filter(Data.id == result_id).first()
                if data and data.data_path:
                    # 显示特征图
                    self.show_feature_plot(data.data_path)
                else:
                    QMessageBox.warning(self, "警告", "未找到相关数据文件")
            else:
                QMessageBox.warning(self, "警告", "未找到评估结果")
                
        except Exception as e:
            logging.error(f"Error viewing details: {str(e)}")
            QMessageBox.critical(self, "错误", f"查看详情失败：{str(e)}")
        finally:
            session.close()

    def show_feature_plot(self, data_path):
        """显示特征图"""
        try:
            feature_type = self.channel_comboBox.currentText()
            
            if feature_type == "Theta/Alpha/Beta/Gamma功率":
                wave_choice, ok = QInputDialog.getItem(self, "选择波段", "请选择要查看的波段：", 
                                                       ["Theta", "Alpha", "Beta", "Gamma"], 0, False)
                if ok and wave_choice:
                    image_path = os.path.join(data_path, f'{wave_choice}.png')
                    self.display_image(image_path)
            elif feature_type == "均分频带":
                band_choice, ok = QInputDialog.getItem(self, "选择频带", "请选择要查看的频带：", 
                                                       ["Band 1", "Band 2", "Band 3", "Band 4", "Band 5"], 0, False)
                if ok and band_choice:
                    band_number = int(band_choice.split()[-1])
                    image_path = os.path.join(data_path, f'frequency_band_{band_number}.png')
                    self.display_image(image_path)
            elif feature_type == "时域特征":
                time_feature_choice, ok = QInputDialog.getItem(self, "选择时域特征", "请选择要查看的时域特征：", 
                                                               ["过零率", "方差", "能量", "差分"], 0, False)
                if ok and time_feature_choice:
                    image_path = os.path.join(data_path, f'time_{time_feature_choice}.png')
                    self.display_image(image_path)
            elif feature_type == "时频域特征":
                image_path = os.path.join(data_path, 'frequency_wavelet.png')
                self.display_image(image_path)
            elif feature_type == "微分熵":
                image_path = os.path.join(data_path, 'differential_entropy.png')
                self.display_image(image_path)
                
        except Exception as e:
            logging.error(f"Error showing feature plot: {str(e)}")
            QMessageBox.critical(self, "错误", f"显示特征图失败：{str(e)}")

    def display_image(self, image_path):
        """显示图片"""
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scene = QGraphicsScene()
                pixmap_item = QGraphicsPixmapItem(pixmap)
                scene.addItem(pixmap_item)
                self.graphicsView.setScene(scene)
                self.graphicsView.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
            else:
                QMessageBox.warning(self, "警告", "无法加载图片")
        else:
            QMessageBox.warning(self, "警告", "图片文件不存在")

    def return_index(self):
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

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 这里是界面的入口，在这里需要定义QApplication对象，之后界面跳转时不用再重新定义，只需要调用show()函数即可
    app = QApplication(sys.argv)
    # 显示创建的界面
    demo_window = Results_View_WindowActions()
    demo_window.show()
    sys.exit(app.exec_())