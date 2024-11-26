import sys
sys.path.append('../')
import os
import threading
from sql_model.tb_model import Model

import os

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtGui import *
# from PyQt5.uic.properties import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, \
    QGraphicsScene, QGraphicsPixmapItem
from PyQt5 import QtWidgets
from datetime import datetime
import state.operate_user as operate_user
# 导入本页面的前端部分
import front.health_evaluate as health_evaluate
# 导入跳转页面的后端部分
import index_rear

from rear import admin_rear, param_control, model_control_controller

from sql_model.tb_data import Data
from sql_model.tb_result import Result
from util.db_util import SessionClass
from model.tuili import EegModel
import logging
from sql_model.tb_user import User
from util.window_manager import WindowManager

class UserFilter(logging.Filter):
    """
    自定义日志过滤器，用于添加用户类型信息到日志记录中
    """
    def __init__(self, userType):
        super().__init__()
        self.userType = userType

    def filter(self, record):
        if not hasattr(record, 'userType'):
            record.userType = self.userType
        return True

class Health_Evaluate_WindowActions(health_evaluate.Ui_MainWindow, QMainWindow):
    """
    健康评估窗口的主要类，继承自PyQt5的QMainWindow和前端UI类
    """

    def __init__(self):
        """
        初始化健康评估窗口
        """
        super(health_evaluate.Ui_MainWindow, self).__init__()
        self.setupUi(self)  # 初始化health_evaluate方法
        
        # 从文件中读取用户ID
        path = '../state/user_status.txt'
        user_status = operate_user.read(path)
        print(f"Read user_status from file: {user_status}")  # 调试日志
        
        # 获取用户类型
        session = SessionClass()
        try:
            # 先尝试直接用用户名查询
            user = session.query(User).filter(User.username == user_status).first()
            if not user:
                # 如果找不到，尝试将user_status转换为整数作为user_id查询
                try:
                    user_id = int(user_status)
                    user = session.query(User).filter(User.user_id == user_id).first()
                except ValueError:
                    print(f"Invalid user status: {user_status}")
                    user = None

            if user:
                self.user_type = user.user_type == 'admin'
                self.user_id = user.user_id
                self.username = user.username
                userType = "Administrator" if self.user_type else "Regular user"
                print(f"Found user: {user.username}, type: {user.user_type}, id: {user.user_id}")
            else:
                self.user_type = False
                self.user_id = None
                self.username = None
                userType = "Unknown user"
                print(f"User not found in database: {user_status}")
        finally:
            session.close()

        # 配置 logging 模块
        logging.basicConfig(
            filename='../log/log.txt',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(userType)s - %(message)s'
        )

        # 添加过滤器
        logger = logging.getLogger()
        logger.addFilter(UserFilter(userType))

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

        window_manager = WindowManager()
        window_manager.register_window('health_evaluate', self)

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
        path = '../state/user_status.txt'
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

    def update_led_colors(self, result):
        """根据结果更新LED颜色"""
        red_style = (
            "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; "
            "border-radius: 16px; border: 2px solid white; background: red"
        )
        
        if result.result_1:
            self.ordinarystress_led_label.setStyleSheet(red_style)
            logging.info("Ordinary stress LED set to RED")
        
        if result.result_2:
            self.depression_led_label.setStyleSheet(red_style)
            logging.info("Depression LED set to RED")
        
        if result.result_3:
            self.anxiety_led_label.setStyleSheet(red_style)
            logging.info("Anxiety LED set to RED")

    def show_nav(self):
        """
        显示导航栏和状态信息
        """
        # 模型状态
        # 判断模型是否空闲，即是否有文件存在
        if not os.path.exists('../state/status.txt'):
            self.status_label.setText("模型空闲")
        
        # 设置所有LED为默认灰色
        self.set_default_led_colors()

        # 如果有最新的评估结果，更新LED颜色
        session = SessionClass()
        result = session.query(Result).order_by(Result.id.desc()).first()
        session.close()

        if result is not None:
            self.update_led_colors(result)

    def show_table(self):
        '''
        从数据库tb_data获取data对象list
        遍历每个data对象，将每个data对象的data.id，personal_id、data_path、upload_user添加到table中
        管理员可以查看所有数据，普通用户只能查看自己上传的数据
        '''
        session = SessionClass()
        try:
            print(f"show_table - user_type: {self.user_type}, user_id: {self.user_id}")  # 调试日志
            
            # 根据用户类型获取数据
            if self.user_type:  # 管理员
                data_list = session.query(Data).all()
                print(f"Administrator query - found {len(data_list)} records")  # 调试日志
                logging.info(f"Administrator {self.user_id}: fetching all data records")
            else:  # 普通用户
                data_list = session.query(Data).filter(Data.user_id == self.user_id).all()
                print(f"Regular user query - found {len(data_list)} records")  # 调试日志
                logging.info(f"Regular user {self.user_id}: fetching own data records")

            # 清空现有表格内容
            self.tableWidget.setRowCount(0)

            # 遍历数据并添加到表
            for data in data_list:
                row = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row)

                # 获取上传用户的用户名
                uploader = session.query(User).filter(User.user_id == data.user_id).first()
                uploader_name = uploader.username if uploader else "未知用户"

                # 设置表格内容
                items = [
                    str(data.id),
                    str(data.personnel_id),
                    str(data.data_path),
                    uploader_name
                ]

                for col, item_text in enumerate(items):
                    item = QTableWidgetItem(item_text)
                    self.tableWidget.setItem(row, col, item)

                # 添加操作按钮
                self.tableWidget.setCellWidget(row, len(self.lst) - 1, self.buttonForRow())

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
                "frequency_wavelet.png", "differential_entropy.png"
            ]

            image_names = [
                "Theta波段功率", "Alpha波段功率", "Beta波段功率", "Gamma波段功率",
                "均分频带1", "均分频带2", "均分频带3", "均分频带4", "均分频带5",
                "域特征 - 过零率", "时域特征 - 方差", "时域特征 - 能量", "时域特征 - 差分",
                "时频域特征 - 小波变换", "微分熵"
            ]

            logging.info(f"Image list initialized with {len(self.image_list)} items.")

            image_path = os.path.join(self.data_path, self.image_list[self.current_index])
            logging.info(f"Attempting to load image from path: {image_path}")

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
                    logging.info(f"Successfully displayed image: {image_names[self.current_index]}")
                else:
                    logging.error(f"Failed to load image: {image_path}")
                    self.curve_label.setText("无法加载图片")
            else:
                logging.error(f"Image file does not exist: {image_path}")
                self.curve_label.setText("图片文件不存在")

        except Exception as e:
            logging.error(f"An error occurred while showing the image: {e}")
            self.curve_label.setText("显示图片时发生错误")

    def next_image(self):
        if self.current_index < len(self.image_list) - 1:
            self.current_index += 1
        else:
            self.current_index = 0
        self.show_image()

    def previous_image(self):
        if self.current_index > 0:
            self.current_index -= 1
        else:
            self.current_index = len(self.image_list) - 1
        self.show_image()

    # btn_return返回首页
    def return_index(self):
        """
        返回到相应的主页面
        根据用户类型返回到管理员或普通用户页面
        """
        path = '../state/user_status.txt'
        user_status = operate_user.read(path)
        
        session = SessionClass()
        try:
            # 先尝试直接用用户名查询
            user = session.query(User).filter(User.username == user_status).first()
            if not user:
                # 如果找不到，尝试将user_status转换为整数作为user_id查询
                try:
                    user_id = int(user_status)
                    user = session.query(User).filter(User.user_id == user_id).first()
                except ValueError:
                    user = None
            
            if user and user.user_type == 'admin':
                index_window = admin_rear.AdminWindowActions()
                logging.info("Returning to admin homepage")
            else:
                index_window = index_rear.Index_WindowActions()
                logging.info("Returning to user homepage")
            
            self.close()
            index_window.show()
            
        except Exception as e:
            logging.error(f"Error in return_index: {str(e)}")
            QMessageBox.critical(self, "错误", f"返回主页时发生错误：{str(e)}")
        finally:
            session.close()

    # 将查看、评估按钮封装到widget中
    def buttonForRow(self):
        widget = QtWidgets.QWidget()
        # 查看
        self.check_pushButton = QtWidgets.QPushButton('查看')
        self.check_pushButton.setStyleSheet("text-align : center;"
                                            "background-color : NavajoWhite;"
                                            "height : 30px;"
                                            "border-style: outset;"
                                            "font-size:13px")
        # 查看数据功能
        self.check_pushButton.clicked.connect(self.checkButton)

        # 评估
        self.evaluate_pushButton = QtWidgets.QPushButton('评估')
        self.evaluate_pushButton.setStyleSheet("text-align : center;"
                                               "background-color : LightCoral;"
                                               "height : 30px;"
                                               "border-style: outset;"
                                               "font-size:13px")
        # 评估状态功能
        self.evaluate_pushButton.clicked.connect(self.EvaluateButton)

        hLayout = QtWidgets.QHBoxLayout()
        hLayout.addWidget(self.check_pushButton)
        hLayout.addWidget(self.evaluate_pushButton)
        hLayout.setContentsMargins(5, 2, 5, 2)
        widget.setLayout(hLayout)
        return widget

    # 查看按钮功能
    def checkButton(self):
        button = self.sender()
        if button:
            try:
                row = self.tableWidget.indexAt(button.parent().pos()).row()
                id = self.tableWidget.item(row, 0).text()
                self.id = int(id)
                logging.info(f"Button clicked in row {row}, ID: {self.id}")

                session = SessionClass()
                data = session.query(Data).filter(Data.id == self.id).first()
                if data:
                    self.data_path = data.data_path
                    logging.info(f"Data path retrieved for ID {self.id}: {self.data_path}")

                    # 获取 tb_result 表中与当前数据 ID 相关的结果
                    result = session.query(Result).filter(Result.id == self.id).first()
                    session.close()
                    if result:
                        # 重置所有LED为灰色
                        self.set_default_led_colors()
                        # 根据结果更新LED颜色
                        self.update_led_colors(result)

                        self.current_index = 0  # 重置当前显示的图片索引
                        logging.info("Initializing current image index to 0")
                        self.show_image()
                    else:
                        logging.warning(f"No evaluation results found for ID {self.id}")
                        QMessageBox.warning(self, "提示", f"没有找到 ID 为 {self.id} 的评估结果")
                else:
                    session.close()
                    logging.warning(f"No data record found for ID {self.id}")
                    QMessageBox.warning(self, "提示", f"没有找到 ID 为 {self.id} 的数据记录")

            except Exception as e:
                logging.error(f"An error occurred in checkButton: {e}")
                QMessageBox.critical(self, "错误", f"查看数据时发生错误: {str(e)}")

    # 调用模型
    def status_model(self, data_path):  # 需要修改 暂未修改 todo
        if os.path.exists('../state/status.txt'):  # 状态评估中，模型正在使用
            file = open('../state/status.txt', mode='r')
            contents = file.readlines()
            print(contents)
            file.close()
            # 获取当前时间
            data_time = datetime.now().replace(microsecond=0)  # 获取到当前时间
            begin_time = datetime.strptime(contents[0], "%Y-%m-%d %H:%M:%S")
            span_time = (data_time - begin_time).seconds
            minute = int(span_time / 60)
            second = span_time % 60
            self.status_label.setText("评中\n" + "(" + str(minute) + "分钟" + str(second) + "秒" + ")")
            finish_box = QMessageBox(QMessageBox.Information, "提示", "模型评估中是否终止")
            qyes = finish_box.addButton(self.tr("是"), QMessageBox.YesRole)
            finish_box.exec_()
            if finish_box.clickedButton() == qyes:

                self.status_label.setText("模型空闲")
                os.remove('../state/status.txt')
                pass

        else:
            model_id, model_path = self.model_list[self.current_model_index]
            box = QMessageBox(QMessageBox.Information, "提示", "模型开始评估，请稍等！！！")
            qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
            box.exec_()
            if box.clickedButton() == qyes:
                pass
            # 生成status.txt文件
            data_time = datetime.now().replace(microsecond=0)  # 获取到当前时间
            # print(data_time)
            desktop_path = '../state/'  # 新创建的txt文件的存放路径
            full_path = desktop_path + 'status.txt'  # 也可以创建一个.doc的word文档
            file = open(full_path, 'w')
            file.write(str(data_time))
            file.close()

            self.status_label.setText("评估中")

            # 调用模型
            self.test_thread = EegModel(data_path, model_path)
            self.test_thread._rule.connect(self.waitTestRes)
            self.test_thread.finished.connect(
                self.on_model_finished)  # connect the finished signal to a slot function
            self.test_thread.start()

    def on_model_finished(self):
        self.lock.acquire()
        try:
            self.current_model_index += 1
            if self.current_model_index < 3:
                model_id, model_path = self.model_list[self.current_model_index]
                self.test_thread = EegModel(self.data_path, model_path)
                self.test_thread._rule.connect(self.waitTestRes)
                self.test_thread.finished.connect(
                    self.on_model_finished)  # connect the finished signal to a slot function
                self.test_thread.start()
        finally:
            self.lock.release()

    def waitTestRes(self, num):
        with open('../state/status.txt', mode='r', encoding='utf-8') as f:
            contents = f.readlines()  # 获取模型开始运行的时间
        self.result_time = datetime.strptime(contents[0], "%Y-%m-%d %H:%M:%S")  # 将string转化为datetime
        
        # 将分数转换为0-95的范围
        probability_score = float(num) * 100  # 将num*100改为num*95，使得最大值为95
        probability_score = max(0, min(95, probability_score))  # 确保分数在0-95之间
        
        self.result_list.append(probability_score)  # 存储转换后的分数
        self.completed_models += 1  # 增加已完成的模型数量

        # 更新对应类型的标签显示分数(不带百分号)
        if self.completed_models == 1:
            self.ordinarystress_label.setText(f"普通应激 ({probability_score:.1f})")
            if num > 0.5:  # 如果num>0.5，设置红色LED
                self.ordinarystress_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; "
                    "border-radius: 16px; border: 2px solid white; background: red"
                )
        elif self.completed_models == 2:
            self.depression_label.setText(f"抑郁 ({probability_score:.1f})")
            if num > 0.5:  # 如果num>0.5，设置红色LED
                self.depression_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; "
                    "border-radius: 16px; border: 2px solid white; background: red"
                )
        elif self.completed_models == 3:
            self.anxiety_label.setText(f"焦虑 ({probability_score:.1f})")
            if num > 0.5:  # 如果num>0.5，设置红色LED
                self.anxiety_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; "
                    "border-radius: 16px; border: 2px solid white; background: red"
                )

        if self.completed_models == 3:  # 如果所有模型都已评估完成
            os.remove('../state/status.txt')  # 删除status.txt文件
            finish_box = QMessageBox(QMessageBox.Information, "提示", "所有模型评估完成。")
            qyes = finish_box.addButton(self.tr("确定"), QMessageBox.YesRole)
            finish_box.exec_()
            if finish_box.clickedButton() == qyes:
                self.status_label.setText("模型空闲")
            
            session = SessionClass()
            try:
                existing_result = session.query(Result).filter(Result.id == self.data_id).first()
                if existing_result is not None:
                    # 如果数据库中已经存在具有当前ID的数据，显示一个提示框询问用户是否要覆盖现有的数据
                    box = QMessageBox(QMessageBox.Question, "提示", "数据库中已经存在当前ID的数据，是否覆盖？")
                    yes_button = box.addButton(self.tr("是"), QMessageBox.YesRole)
                    no_button = box.addButton(self.tr("否"), QMessageBox.NoRole)
                    box.exec_()
                    if box.clickedButton() == yes_button:
                        # 如果用户选择"是"，则覆盖现有的数据
                        existing_result.result_1 = self.result_list[0]
                        existing_result.result_2 = self.result_list[1]
                        existing_result.result_3 = self.result_list[2]
                        existing_result.result_time = self.result_time
                    elif box.clickedButton() == no_button:
                        # 如果用户选择"否"，则不做任何处理
                        pass
                else:
                    # 如果数据库中不存在具有当前ID的数据，直接添加新的数据
                    uploadresult = Result(id=self.data_id, result_1=self.result_list[0], result_2=self.result_list[1],
                                          result_3=self.result_list[2], result_time=self.result_time, user_id=self.user_id)
                    session.add(uploadresult)

                session.commit()
                
                # 重新查询结果以确保它与会话关联
                result_to_update = session.query(Result).filter(Result.id == self.data_id).first()
                
                self.show_nav()
            finally:
                session.close()
            
            self.result_list = []

    # 评估按钮功能


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
                        QMessageBox.warning(self, "警告", "数据不存在，无法进行评估。")
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
        logging.info("Opening model control view.")

        self.model_view = model_control_controller.model_control_Controller()
        self.close()
        self.model_view.show()

        logging.info("Model control view opened successfully.")

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

    # 这里是界面的入口，在这里需要定义QApplication对象，之后界面跳转时不用再重新定义，只需要调用show()函数即可
    app = QApplication(sys.argv)
    # 显示创建的界面
    demo_window = Health_Evaluate_WindowActions()
    demo_window.show()
    sys.exit(app.exec_())