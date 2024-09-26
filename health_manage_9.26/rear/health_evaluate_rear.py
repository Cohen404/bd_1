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

class UserFilter(logging.Filter):
    def __init__(self, userType):
        super().__init__()
        self.userType = userType

    def filter(self, record):
        record.userType = self.userType
        return True


class Health_Evaluate_WindowActions(health_evaluate.Ui_MainWindow, QMainWindow):

    def __init__(self):
        super(health_evaluate.Ui_MainWindow, self).__init__()
        self.test_thread = None
        self.data_path = None
        self.model_list = []
        self.lock = threading.Lock()
        self.result_time = None
        self.setupUi(self)  # 初始化health_evaluate方法
        self.show_nav()  # 调用show_nav方法显示header,bottom的内容
        self.show_table()  # 调用show_table方法显示table的内容
        # button to connect
        self.btn_return.clicked.connect(self.return_index)  # 返回首页
        self.data_id = 0
        self.completed_models = 0

        self.current_image_index = 0  # 当前显示的图片索引
        self.current_model_index=0
        self.pushButton_2.clicked.connect(self.next_image)  # 连接next_button的点击事件到next_button函数
        self.pushButton.clicked.connect(self.previous_image)  # 连接previous_button的点击事件到previous_button函数

        self.result_list=[]
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

    def show_nav(self):
        # 模型状态
        # 判断模型是否空闲，即是否有文件存在
        if not os.path.exists('../state/status.txt'):
            self.status_label.setText("模型空闲")
        # header
        session = SessionClass()
        result = session.query(Result).order_by(Result.id.desc()).first()
        session.close()
        # 获取tb_result表中最新的一条记录，得到result对象
        if result is not None:  # result
            #statu_content = result.health_status  # 健康状态
            ordinarystress_content = result.result_1
            depression_content = result.result_2
            anxiety_content = result.result_3
            if ordinarystress_content == 1:
                self.ordinarystress_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px;max-width:30px; max-height: 30px;border-radius: 16px; border:2px solid white;background:red")
            else:
                self.ordinarystress_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px;max-width:30px; max-height: 30px;border-radius: 16px; border:2px solid white;background:green")

            if depression_content == 1:
                self.depression_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px;max-width:30px; max-height: 30px;border-radius: 16px; border:2px solid white;background:red")
            else:
                self.depression_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px;max-width:30px; max-height: 30px;border-radius: 16px; border:2px solid white;background:green")

            if anxiety_content == 1:
                self.anxiety_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px;max-width:30px; max-height: 30px;border-radius: 16px; border:2px solid white;background:red")
            else:
                self.anxiety_led_label.setStyleSheet(
                    "min-width: 30px; min-height: 30px;max-width:30px; max-height: 30px;border-radius: 16px; border:2px solid white;background:green")

    def show_table(self):
        '''
        从数据库tb_data获取data对象list
        遍历每个data对象，将每个data对象的data.id，personal_id、data_path、upload_user添加到table中
        '''
        session = SessionClass()
        kk = session.query(Data).all()
        session.close()
        info = []
        for item in kk:
            info.append([item.id, item.personnel_id, item.data_path,item.upload_user])
        for data in info:
            row = self.tableWidget.rowCount()  # 当前form有多少行，最后一行是第row-1行
            self.tableWidget.insertRow(row)  # 创建新的行

            #if data[2] == 0:  # info[2]等价于data.upload_user_id
            if data[3] == 0:
                user_name = '普通用户'
            else:
                user_name = '管理员'
            for i in range(len(self.lst) - 1):
                item = QTableWidgetItem()
                # 获得上传数据信息，将其添加到form中
                content = ''
                if i == 0:
                    content = data[0]  # 对应data.id
                elif i==1:
                   content = data[1]
                elif i==2:
                    content = data[2]
                elif i == 3:
                    content = user_name
                item.setText(str(content))  # 将content转为string类型才能存入单元格，否则报错。
                self.tableWidget.setItem(row, i, item)
            self.tableWidget.setCellWidget(row, len(self.lst) - 1, self.buttonForRow())  # 在最后一个单元格中加入按钮

    def show_image(self):
        try:
            self.image_list = [
                "differential_entropy.png",
                "frequency_domain_features.png",
                "theta_alpha_beta_gamma_powers.png",
                "time_domain_features.png",
                "time_frequency_features.png"
            ]  # 图片列表

            logging.info("Image list initialized with {} items.".format(len(self.image_list)))

            # 获取当前索引对应的图片路径
            image_path = f"{self.data_path}/{self.image_list[self.current_index]}"
            logging.info(f"Attempting to load image from path: {image_path}")

            frame = QImage(image_path)
            if frame.isNull():
                logging.error(f"Failed to load image: {image_path}")
                return

            pix = QPixmap.fromImage(frame)
            item = QGraphicsPixmapItem(pix)
            scene = QGraphicsScene()
            scene.addItem(item)

            self.curve_graphicsView.setScene(scene)
            self.curve_graphicsView.fitInView(QGraphicsPixmapItem(QPixmap(pix)))

            logging.info(f"Image successfully displayed: {self.image_list[self.current_index]}")

            _translate = QtCore.QCoreApplication.translate
            self.curve_label.setText(
                _translate("MainWindow", "EEG特征图: {}".format(self.image_list[self.current_index])))
            logging.info(f"Label updated to display: EEG特征图: {self.image_list[self.current_index]}")

        except Exception as e:
            logging.error(f"An error occurred while showing the image: {e}")

    # btn_return返回首页
    def return_index(self):
        path = '../state/user_status.txt'
        user = operate_user.read(path)  # 0表示普通用户，1表示管理员

        if user == '0':  # 普通用户
            logging.info("User type: Regular user. Preparing to return to user homepage.")
            self.index = index_rear.Index_WindowActions()
        elif user == '1':  # 管理员
            logging.info("User type: Administrator. Preparing to return to admin homepage.")
            self.index = admin_rear.AdminWindowActions()
        else:
            logging.warning("Unknown user type found in user status file: %s", user)
            return  # 退出函数，防止程序继续执行

        # 隐藏当前窗口并显示新的首页
        self.hide()
        self.index.show()

    def next_image(self):
        # 更新索引到下一张图片
        if self.current_index < len(self.image_list) - 1:
            self.current_index += 1
        else:
            self.current_index = 0  # 回到第一张图片
        self.show_image()

    def previous_image(self):
        # 更新索引到上一张图片
        if self.current_index > 0:
            self.current_index -= 1
        else:
            self.current_index = len(self.image_list) - 1  # 回到最后一张图片
        self.show_image()


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
                # 确定位置并获取当前行数据的ID值
                row = self.tableWidget.indexAt(button.parent().pos()).row()
                id = self.tableWidget.item(row, 0).text()
                self.id = int(id)  # 全局使用
                logging.info(f"Button clicked in row {row}, ID: {self.id}")

                # 通过self.id获取到tb_data表中对应数据的路径
                session = SessionClass()
                data = session.query(Data).filter(Data.id == self.id).first()
                if data:
                    self.data_path = data.data_path
                    logging.info(f"Data path retrieved for ID {self.id}: {self.data_path}")

                    # 获取 tb_result 表中与当前数据 ID 相关的结果
                    result = session.query(Result).filter(Result.id == self.id).first()
                    session.close()
                    if result:
                        logging.info(
                            f"Results retrieved for ID {self.id}: result_1={result.result_1}, result_2={result.result_2}, result_3={result.result_3}")

                        # 根据result_1设置health_led_label
                        if result.result_1:
                            self.ordinarystress_led_label.setStyleSheet(
                                "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; border-radius: 16px; border: 2px solid white; background: red"
                            )
                            logging.info("Health LED label set to RED")
                        else:
                            self.ordinarystress_led_label.setStyleSheet(
                                "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; border-radius: 16px; border: 2px solid white; background: green"
                            )
                            logging.info("Health LED label set to GREEN")

                        # 根据result_2设置acoustic_led_label
                        if result.result_2:
                            self.depression_led_label.setStyleSheet(
                                "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; border-radius: 16px; border: 2px solid white; background: red"
                            )
                            logging.info("Acoustic LED label set to RED")
                        else:
                            self.depression_led_label.setStyleSheet(
                                "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; border-radius: 16px; border: 2px solid white; background: green"
                            )
                            logging.info("Acoustic LED label set to GREEN")

                        # 根据result_3设置mechanical_led_label
                        if result.result_3:
                            self.anxiety_led_label.setStyleSheet(
                                "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; border-radius: 16px; border: 2px solid white; background: red"
                            )
                            logging.info("Mechanical LED label set to RED")
                        else:
                            self.anxiety_led_label.setStyleSheet(
                                "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; border-radius: 16px; border: 2px solid white; background: green"
                            )
                            logging.info("Mechanical LED label set to GREEN")

                    else:
                        logging.warning(f"No evaluation results found for ID {self.id}")
                        QMessageBox.warning(self, "提示", f"没有找到 ID 为 {self.id} 的评估结果")
                else:
                    session.close()
                    logging.warning(f"No data record found for ID {self.id}")
                    QMessageBox.warning(self, "提示", f"没有找到 ID 为 {self.id} 的数据记录")

                self.current_index = 0  # 当前显示的图片索引
                logging.info("Initializing current image index to 0")
                self.show_image()

            except Exception as e:
                logging.error(f"An error occurred in checkbutton: {e}")

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
            self.status_label.setText("评估中\n" + "(" + str(minute) + "分钟" + str(second) + "秒" + ")")
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

    def waitTestRes(self, result):
        with open('../state/status.txt', mode='r', encoding='utf-8') as f:
            contents = f.readlines()  # 获取模型开始运行的时间
            f.close()
        self.result_time = datetime.strptime(contents[0], "%Y-%m-%d %H:%M:%S")  # 将string转化为datetime
        self.result_list.append(result)  # 将评估结果添加到结果列表中
        self.completed_models += 1  # 增加已完成的模型数量

        if self.completed_models == 3:  # 如果所有模型都已评估完成
            os.remove('../state/status.txt')  # 删除status.txt文件
            finish_box = QMessageBox(QMessageBox.Information, "提示", "所有模型评估完成。")
            qyes = finish_box.addButton(self.tr("确定"), QMessageBox.YesRole)
            finish_box.exec_()
            if finish_box.clickedButton() == qyes:
                self.status_label.setText("模型空闲")
            session = SessionClass()
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
                                      result_3=self.result_list[2], result_time=self.result_time)
                session.add(uploadresult)

            session.commit()
            session.close()
            self.result_list=[]
            self.show_nav()

        # 评估按钮功能


    def EvaluateButton(self):
        button = self.sender()
        self.current_model_index = 0
        self.completed_models = 0
        if button:
            row = self.tableWidget.indexAt(button.parent().pos()).row()  # 当前按钮所在行
            id = self.tableWidget.item(row, 0).text()
            self.data_id = id
            '''
            根据id获取数据路径
            data_path = 
            获取tb_train中当前使用的模型路径以及模型id
            self.model_id =    # 模型id设为全局变量，后续保存结果到数据库时使用（**重要**）
            model_path = 
            '''
            session = SessionClass()
            data1 = session.query(Data).filter(Data.id == id).first()
            self.data_path = data1.data_path
            model_0 = session.query(Model).filter(Model.model_type == 0).first()
            model_1 = session.query(Model).filter(Model.model_type == 1).first()
            model_2 = session.query(Model).filter(Model.model_type == 2).first()
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
                for model_type, model_path in self.model_list:
                    if not os.path.exists(model_path):
                        box = QMessageBox(QMessageBox.Information, "提示",
                                          "模型文件不存在，请重新上传模型：\n" + model_path)
                        qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
                        box.exec_()
                        if box.clickedButton() == qyes:
                            self.open_model_control_view()
                        return  # 如果文件不存在，直接返回，不执行后续的self.status_model(self.data_path)

                self.status_model(self.data_path)

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
