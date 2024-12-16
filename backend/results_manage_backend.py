# 文件功能：结果查看界面的后端逻辑
# 该脚本实现了结果查看界面的功能，包括显示评估结果列表、查看详细结果、删除结果等操作

import os
import sys
import fitz  # PyMuPDF

import logging
from pyqt5_plugins.examplebutton import QtWidgets
from pdf2image import convert_from_path
from PyQt5.QtGui import QPainter

sys.path.append('../')
import time
from datetime import datetime, timedelta
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsPixmapItem, QGraphicsScene, QMessageBox, 
    QTableWidgetItem, QInputDialog, QPushButton, QFileDialog, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QGraphicsView, QScrollArea
)
import state.operate_user as operate_user
# 导入本页面的前端部分
import front.results_manage_UI as results_manage_UI

# 导入跳转页面的后端部分
from backend import index_backend
from backend import admin_index_backend
from sql_model.tb_data import Data
from sql_model.tb_result import Result
from sql_model.tb_user import User
from util.db_util import SessionClass
from sql_model.tb_user import User
from util.window_manager import WindowManager

from config import (
    USER_STATUS_FILE, 
    CURRENT_USER_FILE, 
    LOG_FILE, 
    MODEL_STATUS_FILE,
    DATA_DIR
)

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

class Results_View_WindowActions(results_manage_UI.Ui_MainWindow, QMainWindow):
    """
    结果查看窗口的主要类，继承自PyQt5的QMainWindow和前端UI类
    """

    def __init__(self):
        """
        初始化结果查看窗口
        """
        super(results_manage_UI.Ui_MainWindow, self).__init__()
        self.setupUi(self)
        
        # 初始化窗口管理器并注册窗口
        window_manager = WindowManager()
        window_manager.register_window('results_view', self)

        # 获取当前用户信息
        self.user_id, is_admin = self.get_current_user()
        self.user_type = is_admin

        # 添加图片切换相关变量
        self.current_data_path = None
        self.current_image_index = 0
        self.image_types = [
            ("Theta功率特征图", "Theta.png"),
            ("Alpha功率特征图", "Alpha.png"),
            ("Beta功率特征图", "Beta.png"),
            ("Gamma功率特征图", "Gamma.png"),
            ("均分频带1特征图", "frequency_band_1.png"),
            ("均分频带2特征图", "frequency_band_2.png"),
            ("均分频带3特征图", "frequency_band_3.png"),
            ("均分频带4特征图", "frequency_band_4.png"),
            ("均分频带5特征图", "frequency_band_5.png"),
            ("时域特征-过零率", "time_过零率.png"),
            ("时域特征-方差", "time_方差.png"),
            ("时域特征-能量", "time_能量.png"),
            ("时域特征-差分", "time_差分.png"),
            ("时频域特征图", "frequency_wavelet.png"),
            ("微分熵特征图", "differential_entropy.png")
        ]

        # 连接Prev和Next按钮的点击事件
        self.pushButton.clicked.connect(self.show_previous_image)
        self.pushButton_2.clicked.connect(self.show_next_image)

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

        # 显示表格内容
        self.show_table()

        # 从文件中读取用户类型并设置userType
        path = USER_STATUS_FILE
        user = operate_user.read(path)
        userType = "Regular user" if user == 0 else "Administrator"

        # 配置日志
        logging.basicConfig(
            filename=LOG_FILE,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(userType)s - %(message)s'
        )
        logger = logging.getLogger()
        logger.addFilter(UserFilter(userType))

        # 连接按钮事件
        self.btn_return.clicked.connect(self.return_index)

        # 添加导出按钮事件连接
        self.export_btn.clicked.connect(self.export_results)

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
            if not os.path.exists(CURRENT_USER_FILE):
                logging.error("Current user file not found")
                QMessageBox.warning(self, "错误", "未找到当前用户信息文件")
                return None, False

            # 读取用户ID
            with open(CURRENT_USER_FILE, 'r') as f:
                user_id = f.read().strip()
            print(f"从current_user.txt读取到用户ID: {user_id}")

            if not user_id:
                logging.error("Current user ID is empty")
                QMessageBox.warning(self, "错误", "当前用户ID为空")
                return None, False
            
            # 读取用户类型
            path = USER_STATUS_FILE
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
                QMessageBox.warning(self, "错误", "数据库中未找到当前用户")
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
        """显示结果表格"""
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
            
            # 设置行高
            for i in range(len(results)):
                self.tableWidget.setRowHeight(i, 50)  # 设置每行高度为50像素
            
            for i, result in enumerate(results):
                # 获取用户信息
                user = session.query(User).filter(User.user_id == result.user_id).first()
                username = user.username if user else "未知用户"

                # 设置表格内容
                self.tableWidget.setItem(i, 0, QTableWidgetItem(str(result.id)))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(username))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(
                    result.result_time.strftime('%Y-%m-%d %H:%M:%S') if result.result_time else ''))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(str(result.stress_score)))  # 普通应激分数
                self.tableWidget.setItem(i, 4, QTableWidgetItem(str(result.depression_score)))  # 抑郁分数
                self.tableWidget.setItem(i, 5, QTableWidgetItem(str(result.anxiety_score)))  # 焦虑分数

                # 添加操作按钮
                self.tableWidget.setCellWidget(i, 6, self.buttonForRow(i))

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
                    f"background: {'red' if result.stress_score >= 50 else 'gray'}"
                )
                
                # 更新抑郁状态
                self.acoustic_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; "
                    "border-radius: 16px; border: 2px solid white; "
                    f"background: {'red' if result.depression_score >= 50 else 'gray'}"
                )
                
                # 更新焦虑状态
                self.mechanical_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; "
                    "border-radius: 16px; border: 2px solid white; "
                    f"background: {'red' if result.anxiety_score >= 50 else 'gray'}"
                )
        finally:
            session.close()

    def update_status_display(self, result):
        """更新状态显示"""
        # 更新普通应激状态
        self.health_label.setText(f"普通应激 ({result.stress_score})")
        self.health_label.setAlignment(Qt.AlignLeft)  # 左对齐
        self.health_led_label.setAlignment(Qt.AlignLeft)  # LED指示灯左对齐
        self.health_led_label.setStyleSheet(
            "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; "
            "border-radius: 16px; border: 2px solid white; "
            f"background: {'red' if result.stress_score >= 50 else 'gray'}; "
            "margin-left: 0px;"  # 移除左边距
        )
        
        # 更新抑郁状态
        self.acoustic_label.setText(f"抑郁状�� ({result.depression_score})")
        self.acoustic_label.setAlignment(Qt.AlignLeft)  # 左对齐
        self.acoustic_led_label.setAlignment(Qt.AlignLeft)  # LED指示灯左对齐
        self.acoustic_led_label.setStyleSheet(
            "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; "
            "border-radius: 16px; border: 2px solid white; "
            f"background: {'red' if result.depression_score >= 50 else 'gray'}; "
            "margin-left: 0px;"  # 移除左边距
        )
        
        # 更新焦虑状态
        self.mechanical_label.setText(f"焦虑状态 ({result.anxiety_score})")
        self.mechanical_label.setAlignment(Qt.AlignLeft)  # 左对齐
        self.mechanical_led_label.setAlignment(Qt.AlignLeft)  # LED指示灯左对齐
        self.mechanical_led_label.setStyleSheet(
            "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; "
            "border-radius: 16px; border: 2px solid white; "
            f"background: {'red' if result.anxiety_score >= 50 else 'gray'}; "
            "margin-left: 0px;"  # 移除左边距
        )

    def display_image(self, image_path):
        """显示图片"""
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scene = QGraphicsScene()
                
                # 添加图片
                pixmap_item = QGraphicsPixmapItem(pixmap)
                scene.addItem(pixmap_item)
                
                # 设置场景并适应视图
                self.status_graphicsView.setScene(scene)
                self.status_graphicsView.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
            else:
                QMessageBox.warning(self, "警告", "无法加载图片")
        else:
            QMessageBox.warning(self, "警告", "图片文件不存在")

    def show_current_image(self):
        """显示当前索引的图片"""
        if self.current_data_path is None:
            return

        # 获取当前图片的标题和文件名
        title, filename = self.image_types[self.current_image_index]
        image_path = os.path.join(self.current_data_path, filename)
        
        # 更新EEG特征图标题
        self.status_label.setText(title)
        
        # 显示图片
        self.display_image(image_path)

        # 更新按钮状态
        self.pushButton.setEnabled(self.current_image_index > 0)
        self.pushButton_2.setEnabled(self.current_image_index < len(self.image_types) - 1)

    def show_previous_image(self):
        """显示上一张图片"""
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.show_current_image()

    def show_next_image(self):
        """显示下一张图片"""
        if self.current_image_index < len(self.image_types) - 1:
            self.current_image_index += 1
            self.show_current_image()

    def return_index(self):
        """
        返回到相应的主页面
        根据用户类型返回到管理员或普通用户页面
        """
        path = USER_STATUS_FILE
        user_status = operate_user.read(path)
        
        try:
            window_manager = WindowManager()
            if user_status == '1':  # 管理员
                # 检查是否已存在admin窗口
                admin_window = window_manager.get_window('admin')
                if not admin_window:
                    admin_window = admin_index_backend.AdminWindowActions()
                    window_manager.register_window('admin', admin_window)
                window_manager.show_window('admin')
            else:  # 普通用户
                # 检查是否已存在index窗口
                index_window = window_manager.get_window('index')
                if not index_window:
                    index_window = index_backend.Index_WindowActions()
                    window_manager.register_window('index', index_window)
                window_manager.show_window('index')
            
            # 隐藏并关闭当前窗口
            self.hide()
            self.close()
            
            logging.info("Returned to index page successfully")
        except Exception as e:
            logging.error(f"Error in return_index: {str(e)}")
            QMessageBox.critical(self, "错误", f"返回主页时发生错误：{str(e)}")

    def buttonForRow(self, row):
        """为每一行创建操作按钮"""
        widget = QtWidgets.QWidget()
        widget.setStyleSheet("background: transparent;")  # 设置背景透明
        
        # 查看按钮
        view_btn = QtWidgets.QPushButton('查看')
        view_btn.setStyleSheet('''
            QPushButton {
                color: #2196F3;
                border: 1px solid #2196F3;
                border-radius: 3px;
                padding: 3px 10px;
                min-width: 60px;
                max-height: 24px;
                font-size: 12px;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #E3F2FD;
            }
        ''')
        view_btn.clicked.connect(lambda checked, row=row: self.view_details(row))

        # 查看报告按钮
        report_btn = QtWidgets.QPushButton('查看报告')
        report_btn.setStyleSheet('''
            QPushButton {
                color: #4CAF50;
                border: 1px solid #4CAF50;
                border-radius: 3px;
                padding: 3px 10px;
                min-width: 80px;
                max-height: 24px;
                font-size: 12px;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #E8F5E9;
            }
        ''')
        report_btn.clicked.connect(self.viewReport)

        # 创建水平布局并添加按钮
        hLayout = QtWidgets.QHBoxLayout()
        hLayout.addWidget(view_btn)
        hLayout.addWidget(report_btn)
        hLayout.setContentsMargins(0, 0, 0, 0)  # 移除所有边距
        hLayout.setSpacing(4)  # 设置按钮之间的间距
        widget.setLayout(hLayout)
        return widget

    def viewReport(self):
        """查看报告"""
        try:
            button = self.sender()
            if button:
                row = self.tableWidget.indexAt(button.parent().pos()).row()
                result_id = int(self.tableWidget.item(row, 0).text())
                
                session = SessionClass()
                try:
                    result = session.query(Result).filter(Result.id == result_id).first()
                    if not result or not result.report_path:
                        QMessageBox.warning(self, "警告", "未找到报告文件")
                        return
                    
                    if not os.path.exists(result.report_path):
                        QMessageBox.warning(self, "警告", "报告文件不存在")
                        return

                    # 创建报告查看窗口
                    self.report_viewer = ReportViewer(result.report_path)
                    self.report_viewer.show()

                finally:
                    session.close()

        except Exception as e:
            logging.error(f"Error viewing report: {str(e)}")
            QMessageBox.critical(self, "错误", f"查看报告时发生错误：{str(e)}")

    def view_details(self, row):
        """查看详细信息"""
        try:
            result_id = int(self.tableWidget.item(row, 0).text())
            session = SessionClass()
            result = session.query(Result).filter(Result.id == result_id).first()
            
            if result:
                # 更新左上角状态显示
                self.update_status_display(result)
                
                # 获取关联的数据记录
                data = session.query(Data).filter(Data.id == result_id).first()
                if data and data.data_path:
                    # 保存当前数据路径
                    self.current_data_path = data.data_path
                    # 重置图片索引
                    self.current_image_index = 0
                    # 显示第一张图片
                    self.show_current_image()
                else:
                    QMessageBox.warning(self, "警告", "未找到相关数据文件")
            else:
                QMessageBox.warning(self, "警告", "未找到评估结果")
                
        except Exception as e:
            logging.error(f"Error viewing details: {str(e)}")
            QMessageBox.critical(self, "错误", f"查看详情失败：{str(e)}")
        finally:
            session.close()

    def export_results(self):
        """导出结果到Excel文件"""
        try:
            # 获取保存路径
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出结果",
                "评估结果.xlsx",
                "Excel Files (*.xlsx)"
            )
            
            if not file_path:
                return
            
            # 确保文件扩展名正确
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'
            
            # 创建pandas DataFrame
            import pandas as pd
            
            # 获取表格数据
            rows = self.tableWidget.rowCount()
            cols = self.tableWidget.columnCount()
            headers = []
            for col in range(cols-1):  # 不包括最后一列的"操作"
                headers.append(self.tableWidget.horizontalHeaderItem(col).text())
            
            data = []
            for row in range(rows):
                row_data = []
                for col in range(cols-1):  # 不包括最后一列的"操作"
                    item = self.tableWidget.item(row, col)
                    row_data.append(item.text() if item else "")
                data.append(row_data)
            
            # 创建DataFrame并导出
            df = pd.DataFrame(data, columns=headers)
            df.to_excel(file_path, index=False, engine='openpyxl')
            
            QMessageBox.information(self, "成功", "结果已成功导出到Excel文件！")
            logging.info(f"Results exported to Excel: {file_path}")
            
        except Exception as e:
            error_msg = f"导出结果时发生错误：{str(e)}"
            logging.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)

class ReportViewer(QMainWindow):
    """报告查看窗口"""
    def __init__(self, pdf_path):
        super().__init__()
        self.pdf_path = pdf_path
        self.current_page = 0
        self.scale_factor = 1.0
        self.images = []
        
        # 检查 PDF 文件是否存在
        if not os.path.exists(pdf_path):
            QMessageBox.critical(self, "错误", "PDF文件不存在")
            self.close()
            return
            
        self.initUI()
        
        try:
            self.loadPDF()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载PDF时发生错误：{str(e)}")
            self.close()

    def initUI(self):
        self.setWindowTitle('报告查看')
        self.setGeometry(100, 100, 800, 900)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建图片显示区域
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layout.addWidget(self.view)

        # 创建控制按钮布局
        button_layout = QHBoxLayout()
        
        # 上一页按钮
        self.prev_btn = QPushButton('上一页')
        self.prev_btn.clicked.connect(self.previousPage)
        button_layout.addWidget(self.prev_btn)
        
        # 页码显示
        self.page_label = QLabel('第 1 页')
        button_layout.addWidget(self.page_label)
        
        # 下一页按钮
        self.next_btn = QPushButton('下一页')
        self.next_btn.clicked.connect(self.nextPage)
        button_layout.addWidget(self.next_btn)
        
        # 缩放按钮
        self.zoom_in_btn = QPushButton('放大')
        self.zoom_in_btn.clicked.connect(self.zoomIn)
        self.zoom_in_btn.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(self.zoom_in_btn)
        
        self.zoom_out_btn = QPushButton('缩小')
        self.zoom_out_btn.clicked.connect(self.zoomOut)
        self.zoom_out_btn.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                background-color: #f44336;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        button_layout.addWidget(self.zoom_out_btn)
        
        # 下载按钮
        self.download_btn = QPushButton('下载报告')
        self.download_btn.clicked.connect(self.downloadReport)
        button_layout.addWidget(self.download_btn)
        
        layout.addLayout(button_layout)

    def loadPDF(self):
        """加载PDF并转换为图像"""
        try:
            # 使用 PyMuPDF 打开 PDF
            try:
                pdf_document = fitz.open(self.pdf_path)
                
                # 转换每一页为图像
                for page in pdf_document:
                    # 设置更高的缩放因子以获得更���的图像质量
                    zoom = 2.0
                    matrix = fitz.Matrix(zoom, zoom)
                    
                    # 获取页面的 pixmap
                    pixmap = page.get_pixmap(matrix=matrix)
                    
                    # 转换为 QImage
                    img_data = pixmap.samples
                    qimage = QImage(img_data, pixmap.width, pixmap.height,
                                  pixmap.stride, QImage.Format_RGB888)
                    
                    # 将 QImage 添加到图片列表
                    self.images.append(qimage)
                    
                pdf_document.close()
                
                if self.images:
                    self.updatePageDisplay()
                    self.updateNavigationButtons()
                else:
                    raise Exception("PDF文件为空或转换后没有图像")
                    
            except Exception as e:
                raise Exception(f"PDF转换失败: {str(e)}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载PDF时发生错误：{str(e)}")
            self.close()

    def updatePageDisplay(self):
        """更新当前页面显示"""
        if not self.images or self.current_page >= len(self.images):
            return
        
        try:
            self.scene.clear()
            qimage = self.images[self.current_page]
            pixmap = QPixmap.fromImage(qimage)
            
            # 应用缩放
            scaled_width = int(pixmap.width() * self.scale_factor)
            scaled_height = int(pixmap.height() * self.scale_factor)
            
            scaled_pixmap = pixmap.scaled(
                scaled_width,
                scaled_height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            pixmap_item = self.scene.addPixmap(scaled_pixmap)
            self.scene.setSceneRect(pixmap_item.boundingRect())
            
            # 更新页码显示
            self.page_label.setText(f'第 {self.current_page + 1} 页 / 共 {len(self.images)} 页')
            
            # 调整视图，但不自动适应大小
            self.view.setScene(self.scene)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"更新显示时发生错误：{str(e)}")

    def updateNavigationButtons(self):
        """更新导航按钮状态"""
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < len(self.images) - 1)

    def previousPage(self):
        """显示上一页"""
        if self.current_page > 0:
            self.current_page -= 1
            self.updatePageDisplay()
            self.updateNavigationButtons()

    def nextPage(self):
        """显示下一页"""
        if self.current_page < len(self.images) - 1:
            self.current_page += 1
            self.updatePageDisplay()
            self.updateNavigationButtons()

    def zoomIn(self):
        """放大"""
        self.scale_factor *= 1.2  # 放大20%
        self.updatePageDisplay()
        self.view.centerOn(self.scene.items()[0])  # 保持居中

    def zoomOut(self):
        """缩小"""
        self.scale_factor /= 1.2  # 缩小20%
        self.updatePageDisplay()
        self.view.centerOn(self.scene.items()[0])  # 保持居中

    def downloadReport(self):
        """下载报告"""
        try:
            file_name = os.path.basename(self.pdf_path)
            save_path, _ = QFileDialog.getSaveFileName(
                self, '保存报告', file_name, 'PDF文件 (*.pdf)'
            )
            
            if save_path:
                import shutil
                shutil.copy2(self.pdf_path, save_path)
                QMessageBox.information(self, "成功", f"报告已保存到：{save_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存报告时发生错误：{str(e)}")

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 这里是界面的入口，在这里需要定义QApplication对象，之后界面跳转不用再重新定义，只需要调用show()函数即可
    app = QApplication(sys.argv)
    # 显示创建的界面
    demo_window = Results_View_WindowActions()
    demo_window.show()
    sys.exit(app.exec_())