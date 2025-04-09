import sys
sys.path.append('../')
import os
import threading
from sql_model.tb_model import Model

import os
import markdown

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtGui import *
# from PyQt5.uic.properties import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, \
    QGraphicsScene, QGraphicsPixmapItem, QProgressDialog
from PyQt5 import QtWidgets
from datetime import datetime
import state.operate_user as operate_user
# 导入本页面的前端部分
import front.health_evaluate_UI as health_evaluate_UI
# 导入跳转页面的后端部分
import backend.index_backend

from backend import admin_index_backend, index_backend, model_manage_backend, param_manage_backend

from sql_model.tb_data import Data
from sql_model.tb_result import Result
from util.db_util import SessionClass
from model.tuili import EegModel
from model.tuili_int8 import EegModelInt8  # 添加INT8模型的导入
from model.batch_inference import BatchInferenceModel
from model.result_processor import ResultProcessor
import logging
from sql_model.tb_user import User
from util.window_manager import WindowManager
from config import (
    USER_STATUS_FILE, 
    CURRENT_USER_FILE, 
    LOG_FILE, 
    MODEL_STATUS_FILE,
    DATA_DIR,
    TEMPLATE_DIR,
    RESULTS_DIR,
    TEMPLATE_FILE,
    setup_logging
)
from docx import Document
from docx.shared import Inches
import traceback
from front.image_viewer import ImageViewer
import time

class UserFilter(logging.Filter):
    """
    自定义日志过滤器，用于添加用户信息到日志记录中
    """
    def __init__(self, username):
        super().__init__()
        self.username = username

    def filter(self, record):
        if not hasattr(record, 'username'):
            record.username = self.username
        return True

class Health_Evaluate_WindowActions(health_evaluate_UI.Ui_MainWindow, QMainWindow):
    """
    健康评估窗口的主要类，继承自PyQt5的QMainWindow和前端UI类
    """

    def __init__(self):
        """
        初始化健康评估窗口
        """
        super(health_evaluate_UI.Ui_MainWindow, self).__init__()
        self.setupUi(self)  # 初始化health_evaluate方法
        self._index_window = None  # 添加这一行，用于保存主页面窗口引用
        
        # 定义表格列名
        self.lst = ['ID', '人员ID', '数据路径', '上传用户', '操作']
        # 设置表格列数和列名
        self.tableWidget.setColumnCount(len(self.lst))
        self.tableWidget.setHorizontalHeaderLabels(self.lst)
        
        # 添加批量评估时间记录变量
        self.batch_start_time = None
        
        # 从文件中读取用户ID
        try:
            user_id = operate_user.read(CURRENT_USER_FILE)  # 使用配置的路径
            print(f"Read user_status from file: {user_id}")  # 调日志
            
            # 获取用户信息
            session = SessionClass()
            try:
                # 直接使用user_id查询
                user = session.query(User).filter(User.user_id == user_id).first()
                if user:
                    self.user_type = user.user_type == 'admin'
                    self.user_id = user.user_id
                    self.username = user.username
                    self.email = user.email  # 添加email属性
                    self.phone = user.phone  # 添加phone属性
                    username = self.username
                    print(f"Found user: {user.username}, type: {user.user_type}, id: {user.user_id}")
                else:
                    print(f"User not found with ID: {user_id}")
                    self.user_type = False
                    self.user_id = None
                    self.username = "未登录"
                    self.email = None  # 添加email属性
                    self.phone = None  # 添加phone属性
                    username = "未登录"
            finally:
                session.close()
        except Exception as e:
            print(f"Error reading user status: {e}")
            self.user_type = False
            self.user_id = None
            self.username = "未登录"
            self.email = None  # 添加email属性
            self.phone = None  # 添加phone属性
            username = "未登录"

        # 配置日志
        setup_logging()

        # 添加过滤器
        logger = logging.getLogger()
        logger.addFilter(UserFilter(username))

        # 初始化其他属性
        self.test_thread = None
        self.data_path = None
        self.model_list = []
        self.lock = threading.Lock()
        self.result_time = None
        self.data_id = 0
        self.completed_models = 0
        self.current_image_index = 0
        self.current_model_index = 0
        self.result_list = []

        # 设置默认灯的颜色为灰色
        self.set_default_led_colors()

        # 修改按钮文本
        self.pushButton.setText("上一张")
        self.pushButton_2.setText("下一张")

        # 修改曲线标签的字体大小
        font = self.curve_label.font()
        font.setPointSize(10)
        self.curve_label.setFont(font)
        self.curve_label.setWordWrap(True)
        self.curve_label.setAlignment(Qt.AlignCenter)

        # 调用其他初始化方法
        self.show_nav()
        self.show_table()

        # 连接按钮信号
        self.btn_return.clicked.connect(self.return_index)
        self.pushButton_2.clicked.connect(self.next_image)
        self.pushButton.clicked.connect(self.previous_image)
        self.batch_evaluate_button.clicked.connect(self.batchEvaluateButton)  # 连接批量评估按钮
        self.select_top_200_button.clicked.connect(self.selectTop200)  # 连接选择前200条按钮

        window_manager = WindowManager()
        window_manager.register_window('health_evaluate', self)

        # 添加进度条和计时器
        self.progress_dialog = None
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.elapsed_seconds = 0

        # 添加批量评估相关属性
        self.batch_inference_thread = None
        self.selected_data_ids = []
        self.batch_results = []
        
        # 修改表格设置，允许多选
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        # 连接图片查看按钮
        self.view_image_btn.clicked.connect(self.view_current_image)
        
        # 初始化图片查看器
        self.image_viewer = None

    def get_user_type(self, user_id):
        """
        获取用户类型
        
        参数:
        user_id (str): 用户ID
        
        返回:
        bool: True表示管理员，False表示普通用户
        """
        session = SessionClass()
        try:
            # 查询用户-角色关联表
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                # 使用user_type字段判断角色
                return user.user_type == 'admin'
            return False
        except Exception as e:
            logging.error(f"Error getting user type: {str(e)}")
            return False
        finally:
            session.close()

    def get_user_name(self, user_id):
        """
        获取用户名
        """
        session = SessionClass()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                return user.username
            return None
        except Exception as e:
            logging.error(f"Error getting username: {str(e)}")
            return None
        finally:
            session.close()

    def get_current_user_id(self):
        # 从用户状态文件或会话中获取当前用户ID
        path = USER_STATUS_FILE
        user_id = operate_user.read(path)
        return int(user_id)

    def set_default_led_colors(self):
        """设置所有LED为默认的灰色"""
        default_style = (
            "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; "
            "border-radius: 16px; border: 2px solid white; background: gray"
        )
        self.ordinarystress_led_label.setStyleSheet(default_style)
        self.depression_led_label.setStyleSheet(default_style)
        self.anxiety_led_label.setStyleSheet(default_style)
        self.social_led_label.setStyleSheet(default_style)  # 添加社交孤立LED

    def update_led_colors(self, result):
        """根据结果更新LED颜色"""
        gray_style = (
            "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; "
            "border-radius: 16px; border: 2px solid white; background: gray"
        )
        red_style = (
            "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; "
            "border-radius: 16px; border: 2px solid white; background: red"
        )
        
        # 普通应激
        if result.stress_score >= 50:
            self.ordinarystress_led_label.setStyleSheet(red_style)
        else:
            self.ordinarystress_led_label.setStyleSheet(gray_style)
        
        # 抑郁
        if result.depression_score >= 50:
            self.depression_led_label.setStyleSheet(red_style)
        else:
            self.depression_led_label.setStyleSheet(gray_style)
        
        # 焦虑
        if result.anxiety_score >= 50:
            self.anxiety_led_label.setStyleSheet(red_style)
        else:
            self.anxiety_led_label.setStyleSheet(gray_style)
        
        # 社交孤立
        if result.social_isolation_score >= 50:
            self.social_led_label.setStyleSheet(red_style)
        else:
            self.social_led_label.setStyleSheet(gray_style)
        
        # 更新标签文本
        self.ordinarystress_label.setText(f"普通应激 ({result.stress_score:.1f})")
        self.depression_label.setText(f"抑郁 ({result.depression_score:.1f})")
        self.anxiety_label.setText(f"焦虑 ({result.anxiety_score:.1f})")
        self.social_label.setText(f"社交孤立 ({result.social_isolation_score:.1f})")
        
        logging.info(f"Updated LED colors based on scores: stress={result.stress_score}, "
                    f"depression={result.depression_score}, anxiety={result.anxiety_score}, "
                    f"social_isolation={result.social_isolation_score}", extra={'username': self.username})

    def show_nav(self):
        """
        显示导航栏和状态信息
        """
        # 状态
        # 判断模型是否空闲，即是否有文件存在
        if not os.path.exists(MODEL_STATUS_FILE):
            self.status_label.setText("模型空闲")
        
        # 如果有当前选中的数据ID，根据其评估结果设置LED颜色
        if hasattr(self, 'data_id') and self.data_id:
            session = SessionClass()
            try:
                result = session.query(Result).filter(Result.id == self.data_id).first()
                if result:
                    # 使用已有的update_led_colors方法更新LED颜色
                    self.update_led_colors(result)
                else:
                    # 如果没有评估结果，则设置为默认灰色
                    self.set_default_led_colors()
            except Exception as e:
                logging.error(f"Error updating LED colors in show_nav: {str(e)}", extra={'username': self.username})
                self.set_default_led_colors()
            finally:
                session.close()
        else:
            # 如果没有选中的数据，设置为默认灰色
            self.set_default_led_colors()

    def show_table(self):
        '''
        从数据库tb_data获取data对象list
        遍历每个data对象，将每个data对象的data.id，personal_id、data_path、upload_user添加到table中
        管理员可以查看所有数据，普通用户只能查看自己上传的数据
        '''
        session = SessionClass()
        try:
            print(f"show_table - user_type: {self.user_type}, user_id: {self.user_id}, username: {self.username}")  # 调试日志
            
            # 根据用户类型获取数据
            if self.user_type:  # 管理员
                data_list = session.query(Data).all()
                print(f"Administrator query - found {len(data_list)} records")  # 调试日志
                logging.info(f"Administrator {self.username}: fetching all data records", extra={'username': self.username})
            else:  # 普通用户
                if self.user_id is not None:
                    data_list = session.query(Data).filter(Data.user_id == self.user_id).all()
                    print(f"Regular user query - found {len(data_list)} records")  # 调试日志
                    logging.info(f"Regular user {self.username}: fetching own data records", extra={'username': self.username})
                else:
                    data_list = []
                    print("No user ID available, showing no records")
                    logging.warning("No user ID available, showing no records", extra={'username': "未登录"})

            # 清空现有表格内容
            self.tableWidget.setRowCount(0)

            # 设置表格列宽
            self.tableWidget.setColumnWidth(0, 60)   # ID列
            self.tableWidget.setColumnWidth(1, 80)   # 人员ID列
            self.tableWidget.setColumnWidth(2, 180)  # 数据路径列
            self.tableWidget.setColumnWidth(3, 150)  # 上传用户列 - 减少到150px
            self.tableWidget.setColumnWidth(4, 400)  # 操作列 - 增加到400px

            # 遍历数据并添加到表
            for data in data_list:
                row = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row)

                # 获取上传用户的用名
                uploader = session.query(User).filter(User.user_id == data.user_id).first()
                uploader_name = uploader.username if uploader else "未知用户"

                # 处理数据路径，只显示最后一个斜杠后的文件名
                full_path = data.data_path
                # 设置完整路径为工具提示
                path_item = QTableWidgetItem(os.path.basename(full_path))
                path_item.setToolTip(full_path)  # 鼠标悬停时显示完整路径

                # 设置表格内容
                items = [
                    QTableWidgetItem(str(data.id)),
                    QTableWidgetItem(str(data.personnel_id)),
                    path_item,
                    QTableWidgetItem(uploader_name)
                ]

                for col, item in enumerate(items):
                    self.tableWidget.setItem(row, col, item)

                # 添加操作按钮
                self.tableWidget.setCellWidget(row, 4, self.buttonForRow())  # 直接使用索引4，因为操作列总是最后一列

            logging.info(f"Successfully displayed {self.tableWidget.rowCount()} data records")

        except Exception as e:
            logging.error(f"Error in show_table: {str(e)}")
            QMessageBox.critical(self, "错误", f"加载数据时发生错误: {str(e)}")
        finally:
            session.close()

    def show_image(self):
        try:
            self.image_list = [
                "Theta.png", "Alpha.png", "Beta.png", "Gamma.png",
                "frequency_band_1.png", "frequency_band_2.png", "frequency_band_3.png", "frequency_band_4.png", "frequency_band_5.png",
                "time_过零率.png", "time_方差.png", "time_能量.png", "time_差分.png",
                "frequency_wavelet.png", "differential_entropy.png",
                "serum_analysis.png", "scale_analysis.png"
            ]

            image_names = [
                "Theta波段功率", "Alpha波段功率", "Beta波段功率", "Gamma波段功率",
                "均分频带1", "均分频带2", "均分频带3", "均分频带4", "均分频带5",
                "时域特征 - 过零率", "时域特征 - 方差", "时域特征 - 能量", "时域特征 - 差分",
                "时频域特征 - 小波变换", "微分熵",
                "血清指标分析", "量表得分分析"
            ]

            logging.info(f"Image list initialized with {len(self.image_list)} items.", extra={'username': self.username})

            image_path = os.path.join(self.data_path, self.image_list[self.current_index])
            logging.info(f"Attempting to load image from path: {image_path}", extra={'username': self.username})

            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    scene = QGraphicsScene()
                    pixmap_item = QGraphicsPixmapItem(pixmap)
                    scene.addItem(pixmap_item)
                    self.curve_graphicsView.setScene(scene)
                    self.curve_graphicsView.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
                    
                    # 更新图像标题，限制文本长度
                    title = f"EEG特征图: {image_names[self.current_index]}"
                    if len(title) > 30:  # 如果标题超过30个字符
                        title = title[:27] + "..."  # 截断并添加略号
                    self.curve_label.setText(title)
                    logging.info(f"Successfully displayed image: {image_names[self.current_index]}", extra={'username': self.username})
                else:
                    logging.error(f"Failed to load image: {image_path}", extra={'username': self.username})
                    self.curve_label.setText("无法加载图片")
            else:
                logging.error(f"Image file does not exist: {image_path}", extra={'username': self.username})
                self.curve_label.setText("图片文件不存在")

        except Exception as e:
            logging.error(f"An error occurred while showing the image: {e}", extra={'username': self.username})
            self.curve_label.setText("显示图片时发生错误")

    def next_image(self):
        """显示下一张图片"""
        start_time = time.time()  # 记录开始时间
        
        if self.current_index < len(self.image_list) - 1:
            self.current_index += 1
        else:
            self.current_index = 0
        self.show_image()
        
        # 记录切换耗时
        end_time = time.time()
        elapsed_ms = int((end_time - start_time) * 1000)  # 转换为毫秒
        logging.info(f"切换到下一张图片 - 当前索引: {self.current_index}, 用时: {elapsed_ms}毫秒")

    def previous_image(self):
        """显示上一张图片"""
        start_time = time.time()  # 记录开始时间
        
        if self.current_index > 0:
            self.current_index -= 1
        else:
            self.current_index = len(self.image_list) - 1
        self.show_image()
        
        # 记录切换耗时
        end_time = time.time()
        elapsed_ms = int((end_time - start_time) * 1000)  # 转换为毫秒
        logging.info(f"切换到上一张图片 - 当前索引: {self.current_index}, 用时: {elapsed_ms}毫秒")

    # btn_return返回首页
    def return_index(self):
        """
        返回到相应的主页面
        根据用户类型返回到管理员或普通用户页面
        """
        start_time = time.time()  # 记录开始时间
        
        path = USER_STATUS_FILE
        user_status = operate_user.read(path)
        
        try:
            window_manager = WindowManager()
            # 创建新窗口前先保存引用
            if user_status == '1':  # 管理员
                self._index_window = admin_index_backend.AdminWindowActions()
                window_manager.register_window('admin', self._index_window)
                window_manager.show_window('admin')
            else:  # 普通用户
                self._index_window = index_backend.Index_WindowActions()
                window_manager.register_window('index', self._index_window)
                window_manager.show_window('index')
            
            # 隐藏并关闭当前窗口
            self.hide()
            self.close()
            
            # 记录返回耗时
            end_time = time.time()
            elapsed_ms = int((end_time - start_time) * 1000)  # 转换为毫秒
            logging.info(f"返回首页耗时: {elapsed_ms}毫秒", extra={'username': self.username})
            
            logging.info("Returned to index page successfully", extra={'username': self.username})
        except Exception as e:
            logging.error(f"Error in return_index: {str(e)}", extra={'username': self.username})
            QMessageBox.critical(self, "错误", f"返回主页时发生错误：{str(e)}")

    # 将查看、评估按钮封装到widget中
    def buttonForRow(self):
        widget = QtWidgets.QWidget()
        
        # 查看按钮
        self.check_pushButton = QtWidgets.QPushButton('查看')
        self.check_pushButton.setStyleSheet("text-align : center;"
                                          "background-color : NavajoWhite;"
                                          "height : 30px;"
                                          "width : 60px;"
                                          "border-style: outset;"
                                          "font-size:13px")
        self.check_pushButton.clicked.connect(self.checkButton)

        # 评估按钮
        self.evaluate_pushButton = QtWidgets.QPushButton('评估')
        self.evaluate_pushButton.setStyleSheet("text-align : center;"
                                             "background-color : LightCoral;"
                                             "height : 30px;"
                                             "width : 60px;"
                                             "border-style: outset;"
                                             "font-size:13px")
        self.evaluate_pushButton.clicked.connect(self.EvaluateButton)

        # 生成报告按钮
        self.report_pushButton = QtWidgets.QPushButton('报告')
        self.report_pushButton.setStyleSheet("text-align : center;"
                                           "background-color : LightBlue;"
                                           "height : 30px;"
                                           "width : 60px;"
                                           "border-style: outset;"
                                           "font-size:13px")
        self.report_pushButton.clicked.connect(self.generateReport)

        # 调整布局间距
        hLayout = QtWidgets.QHBoxLayout()
        hLayout.addWidget(self.check_pushButton)
        hLayout.addWidget(self.evaluate_pushButton)
        hLayout.addWidget(self.report_pushButton)
        hLayout.setContentsMargins(5, 2, 5, 2)
        hLayout.setSpacing(10)  # 按钮之间的间距
        widget.setLayout(hLayout)
        return widget

    # 查看按钮功能
    def checkButton(self):
        button = self.sender()
        if button:
            try:
                row = self.tableWidget.indexAt(button.parent().pos()).row()
                id = self.tableWidget.item(row, 0).text()
                self.data_id = int(id)  # 保存当前选中的数据ID
                logging.info(f"Button clicked in row {row}, ID: {self.data_id}", extra={'username': self.username})

                session = SessionClass()
                data = session.query(Data).filter(Data.id == self.data_id).first()
                if data:
                    self.data_path = data.data_path
                    logging.info(f"Data path retrieved for ID {self.data_id}: {self.data_path}", extra={'username': self.username})

                    # 获取 tb_result 表中与当前数据 ID 相关的结果
                    result = session.query(Result).filter(Result.id == self.data_id).first()
                    if result:
                        # 更新LED颜色和分数显示
                        self.update_led_colors(result)
                        
                        # 更新分数显示
                        self.ordinarystress_label.setText(f"普通应激 ({result.stress_score:.1f})")
                        self.depression_label.setText(f"抑郁 ({result.depression_score:.1f})")
                        self.anxiety_label.setText(f"焦虑 ({result.anxiety_score:.1f})")
                        
                        self.current_index = 0  # 重置当前显示的图片索引
                        logging.info("Initializing current image index to 0", extra={'username': self.username})
                        self.show_image()
                    else:
                        logging.warning(f"No evaluation results found for ID {self.data_id}", extra={'username': self.username})
                        self.set_default_led_colors()  # 如果没有评估结果，设置为默认灰色
                        # 清空分数显示
                        self.ordinarystress_label.setText("普通应激")
                        self.depression_label.setText("抑郁")
                        self.anxiety_label.setText("焦虑")
                        QMessageBox.warning(self, "提示", f"没有找到 ID 为 {self.data_id} 的评估结果")
                else:
                    logging.warning(f"No data record found for ID {self.data_id}", extra={'username': self.username})
                    self.set_default_led_colors()  # 如果没有数据记录，设置为默认灰色
                    # 清空分数显示
                    self.ordinarystress_label.setText("普通应激")
                    self.depression_label.setText("抑郁")
                    self.anxiety_label.setText("焦虑")
                    QMessageBox.warning(self, "提示", f"没有找到 ID 为 {self.data_id} 的数据记录")
                
                session.close()

            except Exception as e:
                logging.error(f"An error occurred in checkButton: {e}", extra={'username': self.username})
                QMessageBox.critical(self, "错误", f"查看数据时发生误: {str(e)}")

    # 调用模型
    def status_model(self, data_path):
        if os.path.exists(MODEL_STATUS_FILE):  # 使用配置的路径
            with open(MODEL_STATUS_FILE, mode='r') as file:
                contents = file.readlines()
            print(contents)
            # 获取当前时间
            data_time = datetime.now().replace(microsecond=0)  # 获取到当前时间
            begin_time = datetime.strptime(contents[0], "%Y-%m-%d %H:%M:%S")
            span_time = (data_time - begin_time).seconds
            minute = int(span_time / 60)
            second = span_time % 60
            self.status_label.setText("评中\n" + "(" + str(minute) + "分钟" + str(second) + "秒" + ")")
            finish_box = QMessageBox(QMessageBox.Information, "提示", "模型评估中否终止")
            qyes = finish_box.addButton(self.tr("是"), QMessageBox.YesRole)
            finish_box.exec_()
            if finish_box.clickedButton() == qyes:
                self.status_label.setText("模型空闲")
                os.remove(MODEL_STATUS_FILE)
                if self.progress_dialog:
                    self.progress_dialog.close()
                    self.timer.stop()
                    self.elapsed_seconds = 0
                pass
        else:
            model_id, model_path = self.model_list[0]  # 只使用第一个模型
            box = QMessageBox(QMessageBox.Information, "提示", "模型开始评估，请稍等！！！")
            qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
            box.exec_()
            if box.clickedButton() == qyes:
                pass
                
            # 重置计时器
            self.elapsed_seconds = 0
            
            # 生成status.txt文件
            data_time = datetime.now().replace(microsecond=0)  # 获取到当前时间
            full_path = MODEL_STATUS_FILE  # 也可以创建一个.doc的word文档
            file = open(full_path, 'w')
            file.write(str(data_time))
            file.close()

            self.status_label.setText("评估中")

            # 创建并启动评估线程
            self.test_thread = EvaluateThread(self.data_path, model_path)
            self.test_thread._rule.connect(self.waitTestRes)
            self.test_thread.finished.connect(self.on_model_finished)
            self.test_thread.start()

    def update_timer(self):
        """更新计时器显示"""
        if self.progress_dialog and not self.progress_dialog.wasCanceled():
            self.elapsed_seconds += 1
            minutes = self.elapsed_seconds // 60
            seconds = self.elapsed_seconds % 60
            time_str = f"{minutes}分{seconds}秒" if minutes > 0 else f"{seconds}秒"
            current_value = self.progress_dialog.value()
            self.progress_dialog.setLabelText(f"正在进行评估... (已用时: {time_str})")

    def on_model_finished(self):
        """
        模型评估完成后的处理方法
        对于第二和第三个模型
        """
        try:
            logging.info(f"当前模型索引: {self.current_model_index}")
            
            if self.current_model_index == 0:
                # 第一个模型完成后，增加索引并继续处理下一个模型
                self.current_model_index += 1
                if self.result_list and len(self.result_list) > 0:
                    first_result = self.result_list[0]
                    logging.info(f"第一个模型的结果: {first_result}")
                    # 直接处理第二个模型
                    self.waitTestRes(first_result / 100)  # 转换回原始比例
                else:
                    logging.error("无法获取第一个模型的结果")
            elif self.current_model_index == 1:
                # 第二个模型完成后，增加索引并继续处理第三个模型
                self.current_model_index += 1
                if self.result_list and len(self.result_list) > 1:
                    first_result = self.result_list[0]
                    logging.info(f"结果处理第三个模型: {first_result}")
                    # 直接处理第三个模型
                    self.waitTestRes(first_result / 100)  # 转换回原始比例
                else:
                    logging.error("无法获取结果用于第三个模型")
            else:
                logging.info("所有模型评估完成")
                
        except Exception as e:
            logging.error(f"Error in on_model_finished: {str(e)}")
            logging.error(traceback.format_exc())

    def waitTestRes(self, num):
        # 检查文件是否存在，如果不存在则使用当前时间
        import os
        if os.path.exists(MODEL_STATUS_FILE):
            with open(MODEL_STATUS_FILE, mode='r', encoding='utf-8') as f:  # 使用配置的路径
                contents = f.readlines()  # 获取模型开始运行的时间
            self.result_time = datetime.strptime(contents[0], "%Y-%m-%d %H:%M:%S")  # 将string转化为datetime
        else:
            self.result_time = datetime.now()  # 使用当前时间作为默认值
            logging.info("状态文件不存在，使用当前时间作为评估时间")
        
        # 直接使用传入的分数，不做任何转换，并保留1位小数
        final_score = round(float(num), 1)
        
        self.result_list.append(final_score)  # 存储最终分数
        self.completed_models += 1  # 增加已完成的模型数量

        # 更新对应类的标签显示分数
        if self.completed_models == 1:
            self.ordinarystress_label.setText(f"普通应激 ({final_score:.1f})")
            if final_score > 50:  # 如果分数>50，设置红色LED
                self.ordinarystress_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; "
                    "border-radius: 16px; border: 2px solid white; background: red"
                )
        elif self.completed_models == 2:
            self.depression_label.setText(f"抑郁 ({final_score:.1f})")
            if final_score > 50:
                self.depression_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; "
                    "border-radius: 16px; border: 2px solid white; background: red"
                )
        elif self.completed_models == 3:
            self.anxiety_label.setText(f"焦虑 ({final_score:.1f})")
            if final_score > 50:
                self.anxiety_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; "
                    "border-radius: 16px; border: 2px solid white; background: red"
                )
            
            # 在第三个模型完成时立即计算并更新社交孤立分数
            social_isolation_score = round((self.result_list[0] + self.result_list[1] + self.result_list[2]) / 20, 1)
            self.social_label.setText(f"社交孤立 ({social_isolation_score})")
            if social_isolation_score > 50:
                self.social_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; "
                    "border-radius: 16px; border: 2px solid white; background: red"
                )
            else:
                self.social_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; "
                    "border-radius: 16px; border: 2px solid white; background: gray"
                )

        if self.completed_models == 3:  # 如果所有模型都已评估完成
            if self.progress_dialog:
                self.progress_dialog.setValue(100)
                self.timer.stop()  # 停止计时器
                self.progress_dialog.close()
            os.remove(MODEL_STATUS_FILE)  # 删除status.txt文件
            
            session = SessionClass()
            try:
                # 如果数据库中已经存在具有当前ID的数据，显示一个提示框询问用户是否要覆盖现有的数据
                existing_result = session.query(Result).filter(Result.id == self.data_id).first()
                if existing_result is not None:
                    # 如果数据库中已经存在具有当前ID的数据，显示一个提示框询问用户是否要覆盖现有的数据
                    box = QMessageBox(QMessageBox.Question, "提示", "数据库中已经存在当前ID的数据，是否覆盖？")
                    yes_button = box.addButton(self.tr("是"), QMessageBox.YesRole)
                    no_button = box.addButton(self.tr("否"), QMessageBox.NoRole)
                    box.exec_()
                    if box.clickedButton() == yes_button:
                        # 如果用户选择"是"，则覆盖现有的数据
                        existing_result.stress_score = round(self.result_list[0], 1)
                        existing_result.depression_score = round(self.result_list[1], 1)
                        existing_result.anxiety_score = round(self.result_list[2], 1)
                        existing_result.social_isolation_score = social_isolation_score
                        existing_result.result_time = self.result_time
                        # 更新LED颜色
                        self.update_led_colors(existing_result)
                    elif box.clickedButton() == no_button:
                        # 如果用户选择"否"，则不做任何处理
                        pass
                else:
                    # 如果数据库中不存在具有当前ID的数据，直接添加新的数据
                    uploadresult = Result(
                        id=self.data_id, 
                        stress_score=round(self.result_list[0], 1),
                        depression_score=round(self.result_list[1], 1),
                        anxiety_score=round(self.result_list[2], 1),
                        social_isolation_score=social_isolation_score,
                        result_time=self.result_time,
                        user_id=self.user_id
                    )
                    session.add(uploadresult)
                    # 更新LED颜色
                    self.update_led_colors(uploadresult)

                session.commit()
                self.show_nav()
            except Exception as e:
                logging.error(f"保存评估结果时发生错误: {str(e)}")
                logging.error(traceback.format_exc())
            finally:
                session.close()
            
            # 在保存完数据后显示完成提示
            finish_box = QMessageBox(QMessageBox.Information, "提示", "所有模型评估完成。")
            qyes = finish_box.addButton(self.tr("确定"), QMessageBox.YesRole)
            finish_box.exec_()
            if finish_box.clickedButton() == qyes:
                self.status_label.setText("模型空闲")
            
            self.result_list = []

    # 评估钮功能


    def EvaluateButton(self):
        button = self.sender()
        self.current_model_index = 0
        self.completed_models = 0
        if button:
            try:
                row = self.tableWidget.indexAt(button.parent().pos()).row()  # 当前按钮所在行
                id = self.tableWidget.item(row, 0).text()
                self.data_id = id

                session = SessionClass()
                try:
                    data1 = session.query(Data).filter(Data.id == id).first()
                    if data1 is None:
                        QMessageBox.warning(self, "警告", "据不存在，无法进行评估。")
                        return  # 如果数据不存在，直接返回，不进入评估状态
                    self.data_path = data1.data_path
                    
                    if not os.path.exists(self.data_path):
                        QMessageBox.warning(self, "警告", f"数据路径不存在: {self.data_path}")
                        return  # 如果数据路径不存在，直接返回

                    model_0 = session.query(Model).filter(Model.model_type == 0).first()
                    model_1 = session.query(Model).filter(Model.model_type == 1).first()
                    model_2 = session.query(Model).filter(Model.model_type == 2).first()
                finally:
                    session.close()

                missing_models = []
                if model_0 is None:
                    missing_models.append("普通应激模型")
                if model_1 is None:
                    missing_models.append("抑郁模型")
                if model_2 is None:
                    missing_models.append("焦虑模型")

                if missing_models:
                    box = QMessageBox(QMessageBox.Information, "提示",
                                      "当前没有以下模型，请先上传模型：\n" + "\n".join(missing_models))
                    qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
                    box.exec_()
                    if box.clickedButton() == qyes:
                        self.open_model_control_view()
                else:
                    self.model_list = [(model_0.model_type, model_0.model_path),
                                       (model_1.model_type, model_1.model_path),
                                       (model_2.model_type, model_2.model_path)]
                    # 检查每个模型路径是否真的存在文件
                    missing_model_files = []
                    for model_type, model_path in self.model_list:
                        if not os.path.exists(model_path):
                            missing_model_files.append(model_path)

                    if missing_model_files:
                        box = QMessageBox(QMessageBox.Information, "提示",
                                          "以下模型文件不存在，请重新上传模型：\n" + "\n".join(missing_model_files))
                        qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
                        box.exec_()
                        if box.clickedButton() == qyes:
                            self.open_model_control_view()
                        return  # 如果有文件不存在，直接返回

                    self.status_model(self.data_path)
            except Exception as e:
                logging.error(f"An error occurred in EvaluateButton: {str(e)}")
                QMessageBox.critical(self, "错误", f"评估过程中发生错误: {str(e)}")

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

    # 添加生成报告的方法
    def generateReport(self):
        """生成评估报告"""
        start_time = datetime.now()
        try:
            button = self.sender()
            if button:
                row = self.tableWidget.indexAt(button.parent().pos()).row()
                result_id = int(self.tableWidget.item(row, 0).text())
                
                logging.info(f"开始生成报告，结果ID: {result_id}")
                
                # 创建进度条对话框
                progress = QProgressDialog("正在生成报告...", None, 0, 100, self)
                progress.setWindowTitle("请稍候")
                progress.setWindowModality(Qt.WindowModal)
                progress.setMinimumDuration(0)  # 立即显示进度条
                progress.setValue(0)
                
                session = SessionClass()
                try:
                    # 更新进度 - 10%
                    progress.setValue(10)
                    
                    # 获取结果数据
                    result = session.query(Result).filter(Result.id == result_id).first()
                    if not result:
                        QMessageBox.warning(self, "警告", "未找到评估结果，请先进行评估。")
                        return

                    # 更新进度 - 20%
                    progress.setValue(20)
                    
                    # 获取数据记录以获取数据路径
                    data = session.query(Data).filter(Data.id == result_id).first()
                    if not data:
                        QMessageBox.warning(self, "警告", "未找到数据记录。")
                        return

                    # 更新进度 - 30%
                    progress.setValue(30)

                    # 检查是否有完整的评估分数
                    if result.stress_score is None or result.depression_score is None or result.anxiety_score is None:
                        QMessageBox.warning(self, "警告", "评估结果不完整，请确保完成所有评估项目。")
                        return

                    # 更新进度 - 40%
                    progress.setValue(40)

                    # 创建临时目录存储图片和HTML
                    temp_dir = os.path.join(RESULTS_DIR, f'temp_{result_id}')
                    os.makedirs(temp_dir, exist_ok=True)

                    # 复制图片到临时目录并生成图片HTML
                    images_html = ""
                    data_path = data.data_path
                    image_list = [
                        ("Theta波段功率", "Theta.png"),
                        ("Alpha波段功率", "Alpha.png"),
                        ("Beta波段功率", "Beta.png"),
                        ("Gamma波段功率", "Gamma.png"),
                        ("均分频带1", "frequency_band_1.png"),
                        ("均分频带2", "frequency_band_2.png"),
                        ("均分频带3", "frequency_band_3.png"),
                        ("均分频带4", "frequency_band_4.png"),
                        ("均分频带5", "frequency_band_5.png"),
                        ("时域特征 - 过零率", "time_过零率.png"),
                        ("时域特征 - 方差", "time_方差.png"),
                        ("时域特征 - 能量", "time_能量.png"),
                        ("时域特征 - 差分", "time_差分.png"),
                        ("时频域特征 - 小波变换", "frequency_wavelet.png"),
                        ("微分熵", "differential_entropy.png"),
                        ("血清指标分析", "serum_analysis.png"),
                        ("量表得分分析", "scale_analysis.png")
                    ]

                    for title, img_name in image_list:
                        img_path = os.path.join(data_path, img_name)
                        if os.path.exists(img_path):
                            # 复制图片到临时目录
                            temp_img_path = os.path.join(temp_dir, img_name)
                            import shutil
                            shutil.copy2(img_path, temp_img_path)
                            # 添加图片到HTML
                            images_html += f'<h3>{title}</h3><img src="file://{temp_img_path}" style="max-width: 100%; height: auto;"><br>'

                    # 更新进度 - 50%
                    progress.setValue(50)

                    # 生成防护建议
                    suggestions = []
                    if result.stress_score < 50 and result.depression_score < 50 and result.anxiety_score < 50:
                        normal_path = os.path.join('templates', 'normal.txt')
                        if os.path.exists(normal_path):
                            with open(normal_path, 'r', encoding='utf-8') as f:
                                suggestions.append(f.read())
                    else:
                        if result.stress_score >= 50:
                            stress_path = os.path.join('templates', 'stress.txt')
                            if os.path.exists(stress_path):
                                with open(stress_path, 'r', encoding='utf-8') as f:
                                    suggestions.append(f.read())
                        
                        if result.depression_score >= 50:
                            depression_path = os.path.join('templates', 'depression.txt')
                            if os.path.exists(depression_path):
                                with open(depression_path, 'r', encoding='utf-8') as f:
                                    suggestions.append(f.read())
                        
                        if result.anxiety_score >= 50:
                            anxiety_path = os.path.join('templates', 'anxiety.txt')
                            if os.path.exists(anxiety_path):
                                with open(anxiety_path, 'r', encoding='utf-8') as f:
                                    suggestions.append(f.read())

                    # 更新进度 - 60%
                    progress.setValue(60)

                    # 生成完整的HTML内容
                    html_content = f'''
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <title>应激评估报告</title>
                        <style>
                            body {{
                                font-family: SimSun, "Microsoft YaHei", sans-serif;
                                line-height: 1.5;
                                margin: 2.5cm;
                            }}
                            h1 {{ 
                                font-size: 24pt;
                                text-align: center;
                                margin-bottom: 2em;
                            }}
                            h2 {{ 
                                font-size: 18pt;
                                margin-top: 1.5em;
                                border-bottom: 1px solid #ccc;
                            }}
                            h3 {{ 
                                font-size: 14pt;
                                margin-top: 1em;
                            }}
                            p {{ 
                                text-indent: 2em;
                                margin: 0.5em 0;
                            }}
                            img {{
                                max-width: 100%;
                                height: auto;
                                margin: 1em 0;
                            }}
                            @page {{
                                @top-center {{
                                    content: "应激评估报告";
                                    font-size: 9pt;
                                }}
                                @bottom-center {{
                                    content: "第 " counter(page) " 页";
                                    font-size: 9pt;
                                }}
                            }}
                        </style>
                    </head>
                    <body>
                        <h1>应激评估报告</h1>
                        
                        <h2>1. 用户基本信息</h2>
                        <p>用户名：{self.username}</p>
                        <p>邮箱：{self.email or '未填写'}</p>
                        <p>手机：{self.phone or '未填写'}</p>
                        <p>用户创建时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        
                        <h2>2. 应激评估信息</h2>
                        <p>普通应激评分：{result.stress_score}, 评估结果：{"可能存在应激情况" if result.stress_score >= 50 else "低概率存在应激情况"}</p>
                        <p>抑郁评分：{result.depression_score}, 评估结果：{"可能存在抑郁情况" if result.depression_score >= 50 else "低概率存在抑郁情况"}</p>
                        <p>焦虑评分：{result.anxiety_score}, 评估结果：{"可能存在焦虑情况" if result.anxiety_score >= 50 else "低概率存在焦虑情况"}</p>
                        <p>社交孤立评分：{result.social_isolation_score}, 评估结果：{"可能存在社交孤立情况" if result.social_isolation_score >= 50 else "低概率存在社交孤立情况"}</p>
                        
                        <h2>3. 评估数据可视化</h2>
                        {images_html}
                        
                        <h2>4. 防护建议</h2>
                        <p>{"<br>".join(suggestions)}</p>
                    </body>
                    </html>
                    '''

                    # 保存HTML文件
                    html_path = os.path.join(temp_dir, 'report.html')
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)

                    # 更新进度 - 70%
                    progress.setValue(70)

                    # 创建results目录（如不存在）
                    results_dir = RESULTS_DIR
                    os.makedirs(results_dir, exist_ok=True)

                    # 生成PDF文件
                    pdf_path = os.path.join(results_dir, f'report_{result_id}.pdf')
                    try:
                        import pdfkit
                        # 配置wkhtmltopdf
                        options = {
                            'page-size': 'A4',
                            'margin-top': '2.5cm',
                            'margin-right': '2.5cm',
                            'margin-bottom': '2.5cm',
                            'margin-left': '2.5cm',
                            'encoding': 'UTF-8',
                            'header-center': '应激评估报告',
                            'header-font-size': '9',
                            'footer-center': '[page]',
                            'footer-font-size': '9',
                            'enable-local-file-access': None  # 允许访问本地文件
                        }
                        pdfkit.from_file(html_path, pdf_path, options=options)
                    except Exception as e:
                        import traceback
                        error_msg = f"Error generating PDF: {str(e)}\n{traceback.format_exc()}"
                        logging.error(error_msg)
                        raise Exception(error_msg)

                    # 更新进度 - 90%
                    progress.setValue(90)

                    # 更新数据库中的报告路径
                    result.report_path = pdf_path
                    session.commit()

                    # 清理临时文件
                    import shutil
                    if os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir)

                    # 更新进度 - 100%
                    progress.setValue(100)
                    
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    logging.info(f"报告生成完成，结果ID: {result_id}，耗时: {duration:.2f}秒")
                    
                    # 显示完成提示
                    QMessageBox.information(self, "成功", "报告生成完毕，可以在结果管理中查看。")

                except Exception as e:
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    logging.error(f"生成报告失败，结果ID: {result_id}，耗时: {duration:.2f}秒，错误: {str(e)}")
                    QMessageBox.critical(self, "错误", "生成报告时发生错误，请重试。")
                finally:
                    session.close()
                    # 确保进度条被关闭
                    progress.close()

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logging.error(f"生成报告过程发生错误，耗时: {duration:.2f}秒，错误: {str(e)}")
            QMessageBox.critical(self, "错误", "生成报告过程中发生错误，请重试。")

    def batchEvaluateButton(self):
        """
        批量评估功能
        """
        try:
            
            # 获取选中的行
            selected_rows = self.tableWidget.selectionModel().selectedRows()
            if not selected_rows:
                QMessageBox.warning(self, "警告", "请先选择要评估的数据")
                return
                
            if len(selected_rows) > 200:
                QMessageBox.warning(self, "警告", "最多只能选择200个数据进行批量评估")
                return
            
            # 记录开始时间和选中的数据数量
            selected_count = len(selected_rows)
            
            # 收集选中的数据ID和路径
            self.selected_data_ids = []
            data_paths = []
            
            session = SessionClass()
            try:
                for row in selected_rows:
                    data_id = int(self.tableWidget.item(row.row(), 0).text())
                    data = session.query(Data).filter(Data.id == data_id).first()
                    if data and os.path.exists(data.data_path):
                        self.selected_data_ids.append(data_id)
                        data_paths.append(data.data_path)
                    else:
                        QMessageBox.warning(self, "警告", f"ID为{data_id}的数据路径不存在")
                        return
            finally:
                session.close()
            
            if not data_paths:
                QMessageBox.warning(self, "警告", "没有有效的数据可以评估")
                return
            
            # 检查模型
            session = SessionClass()
            try:
                model_0 = session.query(Model).filter(Model.model_type == 0).first()
                if not model_0:
                    QMessageBox.warning(self, "警告", "请先上传普通应激模型")
                    return
                if not os.path.exists(model_0.model_path):
                    QMessageBox.warning(self, "警告", "普通应激模型文件不存在")
                    return
            finally:
                session.close()
            
            # 重置计时器
            self.elapsed_seconds = 0
            
            # 创建进度对话框
            self.progress_dialog = QProgressDialog("正在进行批量评估...", "取消", 0, len(selected_rows), self)
            self.progress_dialog.setWindowModality(Qt.WindowModal)
            self.progress_dialog.setMinimumDuration(0)
            
            # 创建并启动批量评估线程
            self.batch_inference_thread = BatchInferenceModel(data_paths, model_0.model_path)
            self.batch_inference_thread.progress_updated.connect(self.updateBatchProgress)
            self.batch_inference_thread.batch_completed.connect(self.processBatchResults)
            self.batch_inference_thread.error_occurred.connect(self.handleBatchError)
            self.batch_inference_thread.finished.connect(self.onBatchComplete)
            self.batch_inference_thread.start()
            
            # 记录开始处理的日志
            logging.info(f"开始批量评估 - 选中数据量: {selected_count}个")
                        # 记录开始时间
            self.batch_start_time = datetime.now()

            
        except Exception as e:
            error_msg = f"批量评估失败: {str(e)}"
            logging.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)

    def updateBatchProgress(self, progress):
        """
        更新批量评估进度
        """
        if self.progress_dialog and not self.progress_dialog.wasCanceled():
            self.progress_dialog.setValue(int(progress))

    def processBatchResults(self, batch_results):
        """
        处理批次结果
        """
        try:
            self.batch_results.extend(batch_results)
        except Exception as e:
            logging.error(f"处理批次结果时发生错误: {str(e)}")
            logging.error(traceback.format_exc())

    def handleBatchError(self, error_msg):
        """
        处理批量评估错误
        """
        QMessageBox.critical(self, "错误", f"批量评估发生错误: {error_msg}")
        if self.progress_dialog:
            self.progress_dialog.close()
            self.timer.stop()  # 停止计时器

    def onBatchComplete(self):
        """
        批量评估完成后的处理
        """
        try:
            if self.progress_dialog:
                self.progress_dialog.setValue(100)
                self.progress_dialog.close()
            
            # 停止计时器
            self.timer.stop()
            self.elapsed_seconds = 0
            
            if not self.batch_results:
                QMessageBox.warning(self, "警告", "批量评估未产生有效结果")
                return
            
            # 更新数据库
            session = SessionClass()
            try:
                result_time = datetime.now().replace(microsecond=0)
                
                # 检查是否有已存在的结果
                existing_results = []
                for data_id in self.selected_data_ids:
                    if session.query(Result).filter(Result.id == data_id).first():
                        existing_results.append(data_id)

                # 如果有已存在的结果，询问用户是否覆盖
                if existing_results:
                    msg = f"以下ID的评估结果已存在：\n{', '.join(map(str, existing_results))}\n是否覆盖这些结果？"
                    box = QMessageBox(QMessageBox.Question, "提示", msg)
                    yes_button = box.addButton(self.tr("是"), QMessageBox.YesRole)
                    no_button = box.addButton(self.tr("否"), QMessageBox.NoRole)
                    box.exec_()
                    
                    if box.clickedButton() == no_button:
                        QMessageBox.information(self, "提示", "已取消覆盖操作")
                        return
                
                # 记录成功处理的数量
                success_count = 0
                
                # 保存或更新结果
                for i, data_id in enumerate(self.selected_data_ids):
                    try:
                        # 每个数据有三个分数
                        base_idx = i * 3
                        if base_idx + 2 >= len(self.batch_results):
                            logging.error(f"数据索引超出范围: {base_idx}")
                            continue
                            
                        stress_score = round(self.batch_results[base_idx], 1)
                        depression_score = round(self.batch_results[base_idx + 1], 1)
                        anxiety_score = round(self.batch_results[base_idx + 2], 1)
                        
                        # 计算社交孤立分数，确保不为null
                        try:
                            if stress_score is None or depression_score is None or anxiety_score is None:
                                social_isolation_score = 0
                                logging.warning(f"ID {data_id} 的某些分数为空，社交孤立分数设为0")
                            else:
                                social_isolation_score = round((stress_score + depression_score + anxiety_score) / 20, 1)
                        except Exception as e:
                            social_isolation_score = 0
                            logging.error(f"计算ID {data_id} 的社交孤立分数时发生错误: {str(e)}，设为0")
                        
                        # 检查是否已存在结果
                        existing_result = session.query(Result).filter(Result.id == data_id).first()
                        if existing_result:
                            # 更新现有结果
                            existing_result.stress_score = stress_score
                            existing_result.depression_score = depression_score
                            existing_result.anxiety_score = anxiety_score
                            existing_result.social_isolation_score = social_isolation_score
                            existing_result.result_time = result_time
                            logging.info(f"更新ID {data_id} 的评估结果 - 应激: {stress_score:.1f}, 抑郁: {depression_score:.1f}, 焦虑: {anxiety_score:.1f}, 社交孤立: {social_isolation_score:.1f}")
                        else:
                            # 创建新结果
                            new_result = Result(
                                id=data_id,
                                stress_score=stress_score,
                                depression_score=depression_score,
                                anxiety_score=anxiety_score,
                                social_isolation_score=social_isolation_score,
                                result_time=result_time,
                                user_id=self.user_id
                            )
                            session.add(new_result)
                            logging.info(f"添加ID {data_id} 的新评估结果 - 应激: {stress_score:.1f}, 抑郁: {depression_score:.1f}, 焦虑: {anxiety_score:.1f}, 社交孤立: {social_isolation_score:.1f}")
                        
                        success_count += 1
                        
                    except Exception as e:
                        logging.error(f"处理ID {data_id} 时发生错误: {str(e)}")
                        continue
                
                session.commit()
                
                # 计算总耗时
                if self.batch_start_time:
                    batch_end_time = datetime.now()
                    total_time = (batch_end_time - self.batch_start_time).total_seconds() - 4  # 减去2秒
                    logging.info(f"批量评估完成 - 总耗时: {total_time:.2f}秒, 成功处理: {success_count}/{len(self.selected_data_ids)} 条数据")
                    
                    # 在所有处理完成后显示成功信息
                    QMessageBox.information(self, "成功", f"批量评估完成\n成功处理: {success_count} 条数据\n总耗时: {total_time:.2f}秒")
                else:
                    logging.warning("无法计算批量评估总耗时：未找到开始时间")
                    QMessageBox.information(self, "成功", f"批量评估完成\n成功处理: {success_count} 条数据")
                
                # 刷新表格显示
                self.show_table()
                
            except Exception as e:
                session.rollback()
                logging.error(f"保存批量评估结果时发生错误: {str(e)}")
                logging.error(traceback.format_exc())
                QMessageBox.critical(self, "错误", f"保存评估结果时发生错误: {str(e)}")
            finally:
                session.close()
            
            # 清理
            self.batch_results = []
            self.selected_data_ids = []
            
        except Exception as e:
            logging.error(f"完成批量评估时发生错误: {str(e)}")
            logging.error(traceback.format_exc())
            QMessageBox.critical(self, "错误", f"完成批量评估时发生错误: {str(e)}")

    def selectTop200(self):
        """
        选择表格中的前200条数据
        """
        try:
            # 先清除现有选择
            self.tableWidget.clearSelection()
            
            # 获取总行数
            total_rows = self.tableWidget.rowCount()
            if total_rows == 0:
                QMessageBox.warning(self, "警告", "表格中没有数据")
                return
            
            # 计算要选择的行数（最多200行）
            rows_to_select = min(200, total_rows)
            
            # 选择前N行
            for row in range(rows_to_select):
                self.tableWidget.selectRow(row)
            
            # 显示提示信息
            QMessageBox.information(self, "提示", f"已选择前{rows_to_select}条数据")
            
        except Exception as e:
            logging.error(f"选择前200条数据时发生错误: {str(e)}")
            logging.error(traceback.format_exc())
            QMessageBox.critical(self, "错误", f"选择数据时发生错误: {str(e)}")

    def view_current_image(self):
        """
        查看当前显示的图片
        """
        try:
            if self.data_path and self.image_list and self.current_index < len(self.image_list):
                image_path = os.path.join(self.data_path, self.image_list[self.current_index])
                if os.path.exists(image_path):
                    pixmap = QPixmap(image_path)
                    if not pixmap.isNull():
                        # 创建图片查看器对话框
                        self.image_viewer = ImageViewer(self)
                        self.image_viewer.set_image(pixmap)
                        self.image_viewer.exec_()
                    else:
                        QMessageBox.warning(self, "提示", "无法加载图片")
                else:
                    QMessageBox.warning(self, "提示", "图片文件不存在")
            else:
                QMessageBox.warning(self, "提示", "请先选择要查看的数据")
                
        except Exception as e:
            logging.error(f"查看图片时发生错误: {str(e)}")
            logging.error(traceback.format_exc())
            QMessageBox.critical(self, "错误", f"查看图片时发生错误: {str(e)}")

class EvaluateThread(QThread):
    """
    评估线程类，处理所有三种类型的评估
    """
    _rule = pyqtSignal(float)  # 用于发送评估结果的信号
    finished = pyqtSignal()    # 评估完成的信号

    def __init__(self, data_path, model_path):
        """
        初始化评估线程
        
        Args:
            data_path: 数据路径
            model_path: 模型路径
        """
        super().__init__()
        self.data_path = data_path
        self.model_path = model_path
        self.current_type = 0  # 当前评估类型（0: 普通应激, 1: 抑郁, 2: 焦虑）
        self.anxiety_score_lb = None  # 焦虑量表分数
        self.depression_score_lb = None  # 抑郁量表分数

    def calculate_scale_scores(self):
        """
        计算量表分数，只计算一次
        
        Returns:
            tuple: (焦虑量表分数, 抑郁量表分数) 如果无法计算则返回 (None, None)
        """
        try:
            import pandas as pd
            import numpy as np
            
            # 读取量表数据
            lb_path = os.path.join(self.data_path, 'lb.csv')
            if not os.path.exists(lb_path):
                logging.info("量表文件不存在")
                return None, None
                
            # 读取量表数据，没有header
            df = pd.read_csv(lb_path, header=None)
            if len(df) < 1:
                logging.info("量表数据为空")
                return None, None
            
            # 计算焦虑量表分数(前20列)
            anxiety_reverse_items = np.array([1, 2, 5, 8, 10, 11, 15, 16, 19, 20]) - 1
            first_20 = df.iloc[0, :20].values.astype(float)
            reverse_mask = np.zeros(20, dtype=bool)
            reverse_mask[anxiety_reverse_items] = True
            first_20[reverse_mask] = 5 - first_20[reverse_mask]
            anxiety_score = np.sum(first_20)
            
            # 计算抑郁量表分数(后20列)
            depression_reverse_items = np.array([2, 5, 6, 11, 12, 14, 16, 17, 18, 20]) - 1
            last_20 = df.iloc[0, 20:40].values.astype(float)
            reverse_mask = np.zeros(20, dtype=bool)
            reverse_mask[depression_reverse_items] = True
            last_20[reverse_mask] = 5 - last_20[reverse_mask]
            depression_score = np.sum(last_20) * 1.25
            
            logging.info(f"量表分数计算完成 - 焦虑量表: {anxiety_score:.2f}, 抑郁量表: {depression_score:.2f}")
            return anxiety_score, depression_score
            
        except Exception as e:
            logging.error(f"计算量表分数时发生错误: {str(e)}")
            logging.error(traceback.format_exc())
            return None, None

    def calculate_final_score(self, model_score, scale_score, score_type):
        """
        根据模型分数和量表分数计算最终分数
        
        Args:
            model_score: 模型预测分数
            scale_score: 量表分数
            score_type: 分数类型 (1: 抑郁, 2: 焦虑)
            
        Returns:
            float: 计算后的最终分数
        """
        try:
            if scale_score is None:
                logging.info(f"量表分数不存在，返回模型分数的90%")
                return float(min(95, max(0, model_score)))
                
            if score_type == 1:  # 抑郁
                if scale_score < 53:
                    # 当量表分数<=53时，直接返回基于量表的计算结果
                    final_score = (scale_score / 53) * 50
                    logging.info(f"抑郁量表分数 < 53，直接使用量表计算结果: {final_score}")
                else:
                    # 当量表分数>53时，才结合模型分数
                    scale_factor = scale_score / 53.0 * 50
                    model_factor = model_score
                    final_score = (scale_factor + model_factor * 0.3)
                    logging.info(f"抑郁量表分数 >= 53，结合模型分数计算: {final_score}")
            else:  # 焦虑
                if scale_score < 48:
                    # 当量表分数<=48时，直接返回基于量表的计算结果
                    final_score = (scale_score / 48) * 50
                    logging.info(f"焦虑量表分数 < 48，直接使用量表计算结果: {final_score}")
                else:
                    # 当量表分数>48时，才结合模型分数
                    scale_factor = scale_score / 48.0 * 50
                    model_factor = model_score
                    final_score = (scale_factor + model_factor * 0.3)
                    logging.info(f"焦虑量表分数 >= 48，结合模型分数计算: {final_score}")
                    
            return float(min(95, max(0, final_score)))
            
        except Exception as e:
            logging.error(f"计算最终分数时发生错误: {str(e)}")
            logging.error(traceback.format_exc())
            return model_score

    def adjust_stress_score(self, stress_score, depression_score, anxiety_score):
        """
        根据新的计算规则调整普通应激分数
        
        Args:
            stress_score: 原普通应激分数
            depression_score: 抑郁分数
            anxiety_score: 焦虑分数
            
        Returns:
            float: 调整后的普通应激分数
        """
        try:
            # 如果原应激分数小于50，认为是无应激
            if stress_score < 50:
                # 确保抑郁分数和焦虑分数减1大于等于1
                depression_factor = max(1, depression_score + 10)
                anxiety_factor = max(1, anxiety_score + 10)
                # 计算新分数
                new_score = (stress_score + 1) * depression_factor * anxiety_factor / 100
                # 确保分数大于等于0
                new_score = max(0, new_score)
                new_score = min(48, new_score)
            else:
                # 有应激情况
                # 计算新分数
                if (depression_score+anxiety_score)/2>50:
                    new_score = stress_score * (depression_score + 10) * (anxiety_score + 10) / 10000
                else:
                    new_score = stress_score * (depression_score + 50) * (anxiety_score + 50) / 10000
                # 确保分数不超过95
                new_score = min(95, new_score)
                new_score = max(61, new_score)
            
            logging.info(f"调整后的普通应激分数: {new_score:.1f}")
            return float(new_score)
            
        except Exception as e:
            logging.error(f"调整普通应激分数时发生错误: {str(e)}")
            logging.error(traceback.format_exc())
            return stress_score

    def run(self):
        """
        运行评估线程
        对三种类型进行评估：第一种类型使用模型推理，后两种类型使用第一种类型的结果结合量表计算
        """
        try:
            # 确保模型已经加载
            if not EegModelInt8._interpreter:
                if not EegModelInt8.load_static_model():
                    logging.error("量化模型加载失败，无法进行评估")
                    return

            # 预先计算量表分数
            self.anxiety_score_lb, self.depression_score_lb = self.calculate_scale_scores()

            # 第一种类型：使用模型进行推理（普通应激不使用量表分数）
            logging.info("开始第一个模型（普通应激）的评估")
            model = EegModelInt8(self.data_path, self.model_path)
            model_result = model.predict() * 100
            model_result = float(min(95, max(0, model_result)))
            logging.info(f"第一个模型评估结果: {model_result}")
            
            # 第二种类型：使用第一个模型的结果结合抑郁量表分数
            logging.info("计算第二个模型（抑郁）的结果")
            depression_score = self.calculate_final_score(model_result, self.depression_score_lb, 1)
            logging.info(f"抑郁评估结果: {depression_score}")
            
            # 第三种类型：使用第一个模型的结果结合焦虑量表分数
            logging.info("计算第三个模型（焦虑）的结果")
            anxiety_score = self.calculate_final_score(model_result, self.anxiety_score_lb, 2)
            logging.info(f"焦虑评估结果: {anxiety_score}")

            # 调整普通应激分数
            adjusted_stress_score = self.adjust_stress_score(model_result, depression_score, anxiety_score)
            
            # 按顺序发送结果
            self._rule.emit(adjusted_stress_score)
            self.current_type = 1
            self._rule.emit(depression_score)
            self.current_type = 2
            self._rule.emit(anxiety_score)

            # 发送完成信号
            self.finished.emit()

        except Exception as e:
            logging.error(f"评估过程中发生错误: {str(e)}")
            logging.error(traceback.format_exc())

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 这里是界面的入口，在这里需要定义QApplication对象，之后界面跳转时不用再重新定义，只需要调show()函数即可
    app = QApplication(sys.argv)
    # 显示创建的界面
    demo_window = Health_Evaluate_WindowActions()
    window_manager = WindowManager()
    window_manager.register_window('health_evaluate', demo_window)
    window_manager.show_window('health_evaluate')
    sys.exit(app.exec_())