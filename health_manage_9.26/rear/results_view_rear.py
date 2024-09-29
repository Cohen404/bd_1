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
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsPixmapItem, QGraphicsScene, QMessageBox, \
    QTableWidgetItem
import state.operate_user as operate_user
# 导入本页面的前端部分
import front.results_view as results_view

# 导入跳转页面的后端部分
from rear import index_rear
from rear import admin_rear
from sql_model.tb_data import Data
from sql_model.tb_result import Result
from util.db_util import SessionClass

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
        self.show_table()  # 调用show_table方法显示table的内容

        self.btn_return.clicked.connect(self.return_index)  # 返回首页
        self.pushButton_2.clicked.connect(self.next_image)  # 连接next_button的点击事件到next_button函数
        self.pushButton.clicked.connect(self.previous_image)  # 连接previous_button的点击事件到previous_button函数

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
        从数据库获取评估结果并显示在表格中
        """
        session = SessionClass()

        # 1. 从 Result 表中获取所有 id
        result_ids = session.query(Result.id).all()

        # 2. 如果没有找到任何结果，则退出该函数
        if not result_ids:
            session.close()
            QMessageBox.information(self, "提示", "没有找到任何评估结果。")
            return

        # 提取出所有的id
        result_ids = [r.id for r in result_ids]

        # 3. 在 Data 表中查找与这些 id 对应的记录
        kk = session.query(Data).filter(Data.id.in_(result_ids)).all()
        session.close()

        # 4. 准备信息
        info = []
        for item in kk:
            info.append([item.id, item.personnel_name, item.upload_user])

        # 5. 在表格中显示这些信息
        self.tableWidget.setRowCount(0)  # 清空表格内容
        for data in info:
            row = self.tableWidget.rowCount()  # 当前表格有多少行，最后一行是第 row-1 行
            self.tableWidget.insertRow(row)  # 创建新的一行

            # 设置用户名称
            user_name = '普通用户' if data[2] == 0 else '管理员'

            # 填充表格内容
            for i in range(len(self.lst) - 1):
                item = QTableWidgetItem()
                content = ''
                if i == 0:
                    content = data[0]  # data[0] 对应 data.id
                elif i == 1:
                    content = data[1]  # data[1] 对应 data.personnel_name
                elif i == 2:
                    content = user_name  # 用户类型

                item.setText(str(content))  # 将 content 转为字符串类型才能存入单元格
                self.tableWidget.setItem(row, i, item)

            # 在最后一个单元格中加入按钮
            self.tableWidget.setCellWidget(row, len(self.lst) - 1, self.buttonForRow())

    def show_image(self):
        """
        显示当前选中的图像
        """
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
                box = QMessageBox(QMessageBox.Warning, "加载图片失败",
                                  "可能由于上传的数据已预处理完毕或者可视化失败。")
                qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
                box.exec_()
                return

            pix = QPixmap.fromImage(frame)
            item = QGraphicsPixmapItem(pix)
            scene = QGraphicsScene()
            scene.addItem(item)
            self.status_graphicsView.setScene(scene)
            self.status_graphicsView.fitInView(QGraphicsPixmapItem(QPixmap(pix)))

            logging.info(f"Image successfully displayed: {self.image_list[self.current_index]}")

            _translate = QtCore.QCoreApplication.translate
            self.status_label.setText(
                _translate("MainWindow", "EEG特征图: {}".format(self.image_list[self.current_index])))
            logging.info(f"Label updated to display: EEG特征图: {self.image_list[self.current_index]}")

        except Exception as e:
            logging.error(f"An error occurred while showing the image: {e}")

    def next_image(self):
        """
        显示下一张图片
        """
        # 更新索引到下一张图片
        if self.current_index < len(self.image_list) - 1:
            self.current_index += 1
        else:
            self.current_index = 0  # 回到第一张图片
        self.show_image()

    def previous_image(self):
        """
        显示上一张图片
        """
        # 更新索引到上一张图片
        if self.current_index > 0:
            self.current_index -= 1
        else:
            self.current_index = len(self.image_list) - 1  # 回到最后一张图片
        self.show_image()

    def buttonForRow(self):
        """
        为每一行创建操作按钮
        
        返回:
        QtWidgets.QWidget: 包含查看和删除按钮的小部件
        """
        widget = QtWidgets.QWidget()
        # 查看
        self.check_pushButton = QtWidgets.QPushButton('查看')
        self.check_pushButton.setStyleSheet(''' text-align : center;
                                          background-color : NavajoWhite;
                                          height : 30px;
                                          border-style: outset;
                                          font : 13px  ''')
        # 删除
        self.delete_pushButton = QtWidgets.QPushButton('删除')
        self.delete_pushButton.setStyleSheet(''' text-align : center;
                                                  background-color : LightCoral;
                                                  height : 30px;
                                                  border-style: outset;
                                                  font : 13px  ''')

        # 查看数据功能
        self.check_pushButton.clicked.connect(self.checkbutton)
        # 删除功能
        self.delete_pushButton.clicked.connect(self.deletebutton)

        hLayout = QtWidgets.QHBoxLayout()
        hLayout.addWidget(self.check_pushButton)
        hLayout.addWidget(self.delete_pushButton)
        hLayout.setContentsMargins(5, 2, 5, 2)
        widget.setLayout(hLayout)
        return widget

    def checkbutton(self):
        """
        查看按钮的回调函数
        """
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
                            self.health_led_label.setStyleSheet(
                                "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; border-radius: 16px; border: 2px solid white; background: red"
                            )
                            logging.info("Health LED label set to RED")
                        else:
                            self.health_led_label.setStyleSheet(
                                "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; border-radius: 16px; border: 2px solid white; background: green"
                            )
                            logging.info("Health LED label set to GREEN")

                        # 根据result_2设置acoustic_led_label
                        if result.result_2:
                            self.acoustic_led_label.setStyleSheet(
                                "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; border-radius: 16px; border: 2px solid white; background: red"
                            )
                            logging.info("Acoustic LED label set to RED")
                        else:
                            self.acoustic_led_label.setStyleSheet(
                                "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; border-radius: 16px; border: 2px solid white; background: green"
                            )
                            logging.info("Acoustic LED label set to GREEN")

                        # 根据result_3设置mechanical_led_label
                        if result.result_3:
                            self.mechanical_led_label.setStyleSheet(
                                "min-width: 30px; min-height: 30px; max-width: 30px; max-height: 30px; border-radius: 16px; border: 2px solid white; background: red"
                            )
                            logging.info("Mechanical LED label set to RED")
                        else:
                            self.mechanical_led_label.setStyleSheet(
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

    # 删除功能
    def deletebutton(self):
        button = self.sender()
        if button:
            # 确定位置的时候这里是关键
            row = self.tableWidget.indexAt(button.parent().pos()).row()
            id = self.tableWidget.item(row, 0).text()  # 获取当前行数据的ID值
            id = int(id)  # 确保id是整数类型

            try:
                # 开始数据库会话
                session = SessionClass()

                # 删除result表中对应的数据
                session.query(Result).filter(Result.id == id).delete()
                session.commit()
                session.close()

                # 从表格中移除记录
                self.tableWidget.removeRow(row)

                # 记录日志信息
                logging.info(f"Deleted record with ID {id} from Result table.")
                QMessageBox.information(self, "成功", "记录删除成功。")

            except Exception as e:
                # 记录错误日志
                logging.error(f"Failed to delete record with ID {id} from Result table. Error: {str(e)}")
                QMessageBox.critical(self, "错误", f"删除记录时发生错误：{str(e)}")



    # btn_return返回首页
    def return_index(self):
        path = '../state/user_status.txt'
        user = operate_user.read(path)  # 0表示普通用户，1表示管理员

        if user == '0':  # 返回系统首页
            self.index = index_rear.Index_WindowActions()
            logging.info("Returned to user homepage.")
        elif user == '1':  # 返回管理员首页
            self.index = admin_rear.AdminWindowActions()
            logging.info("Returned to admin homepage.")

        self.close()
        self.index.show()

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 这里是界面的入口，在这里需要定义QApplication对象，之后界面跳转时不用再重新定义，只需要调用show()函数即可
    app = QApplication(sys.argv)
    # 显示创建的界面
    demo_window = Results_View_WindowActions()
    demo_window.show()
    sys.exit(app.exec_())