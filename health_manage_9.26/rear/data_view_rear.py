# 文件功能：数据查看和管理界面的后端逻辑
# 该脚本实现了数据查看界面的功能，包括显示数据列表、上传数据、查看数据详情、删除数据等操作

import logging
import os
import sys
import shutil
sys.path.append('../')
import time

import numpy as np
import scipy.io as scio
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFileDialog, QMessageBox, QTableWidgetItem, \
    QGraphicsPixmapItem, QGraphicsScene, QInputDialog
from PyQt5 import QtWidgets
from datetime import datetime
import state.operate_user as operate_user
# 导入本页面的前端部分
import front.data_view as data_view

# 导入跳转页面的后端部分
from rear import index_rear
from rear import admin_rear
from sql_model.tb_data import Data
from sql_model.tb_result import Result
from util.db_util import SessionClass
from sqlalchemy import func
# 导入绘图部分
import data_out
import data_pretreatment

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

class Data_View_WindowActions(data_view.Ui_MainWindow, QMainWindow):
    """
    数据查看窗口的主要类，继承自PyQt5的QMainWindow和前端UI类
    """

    def __init__(self):
        """
        初始化数据查看窗口
        """
        super(data_view.Ui_MainWindow, self).__init__()
        self.setupUi(self)
        self.id = 0
        self.data_path = ''
        # self.show_nav()  # 调用show_nav方法显示header,bottom的内容
        self.show_table()  # 调用show_table方法显示table的内容

        # button to connect
        self.btn_return.clicked.connect(self.return_index)  # 返回首页
        self.upload_pushButton.clicked.connect(self.openfile)  # 上传数据

        # 通道选择下拉框
        self.channel_comboBox.currentIndexChanged.connect(
            lambda: self.WrittingNotOfOther(self.channel_comboBox.currentIndex()))  # 点击下拉列表，触发对应事件

        # 更新下拉菜单选项
        self.channel_comboBox.clear()
        self.channel_comboBox.addItems([
            "Theta/Alpha/Beta/Gamma功率",
            "均分频带",
            "时域特征",
            "时频域特征",
            "微分熵"
        ])

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

        # 添加一个新的标签来显示图像名称
        self.image_name_label = QtWidgets.QLabel(self.centralwidget)
        self.image_name_label.setAlignment(Qt.AlignCenter)
        self.image_name_label.setStyleSheet("font-size: 14px; color: #333;")
        self.verticalLayout.addWidget(self.image_name_label)

    # 定义通道选择对应的事件（没用但不能删）
    def WrittingNotOfOther(self, tag):
        """
        通道选择的回调函数（目前未使用）
        
        参数:
        tag (int): 选择的通道索引
        """
        if tag == 0:
            print('点到了第1项 ...')
        if tag == 1:
            print('点到了第2项 ...')
        if tag == 2:
            print('点到了第3项 ...')
        if tag == 3:
            print('点到了第4项 ...')
        if tag == 4:
            print('点到了第5项 ...')

    def show_table(self):
        '''
        从数据库tb_data获取 flag==1 的所有data对象，即评估数据
        遍历每个data对象，将每个data对象的data.id，data.upload_user_id，data.upload_time添加到table中

        '''

        session = SessionClass()
        kk = session.query(Data).filter().all()
        session.close()
        info = []
        for item in kk:
            info.append([item.id, item.personnel_id, item.data_path, item.upload_user, item.personnel_name])

        for data in info:
            row = self.tableWidget.rowCount()  # 当前form有多少行，最后一行是第row-1行
            self.tableWidget.insertRow(row)  # 创建新的行

            if data[3] == 0:  # info[2]等价于data.upload_user_id
                user_name = '普通用户'
            else:
                user_name = '管理员'
            for i in range(len(self.lst) - 1):
                item = QTableWidgetItem()
                # 获得上传数据信息，将其添加到form中
                content = ''
                if i == 0:
                    content = data[0]  # data[0]对应data.id
                elif i == 1:
                    content = data[1]
                elif i == 2:
                    content = data[4]
                elif i == 3:
                    content = data[2]
                elif i == 4:
                    content = user_name  # user_name上边已经处理过
                item.setText(str(content))  # 将content转为string类型才能存入单元格，否则报错。
                self.tableWidget.setItem(row, i, item)
            self.tableWidget.setCellWidget(row, len(self.lst) - 1, self.buttonForRow())  # 在最后一个单元格中加入按钮

    def openfile(self):
        """
        打开文件对话框并处理选择的文件夹
        """
        folder_path = ''
        hadprocessed = False
        # 获取文件夹路径
        folder_path = QFileDialog.getExistingDirectory(self, '选择文件夹')

        if folder_path == '':
            logging.info("No folder selected.")
            return
        else:
            # 获取文件夹名称
            folder_name = os.path.basename(folder_path)
            logging.info(f"Selected folder: {folder_name}")

            # 检查文件夹名称是否重复
            session = SessionClass()
            data_folder = session.query(Data).filter(Data.data_path.like(f'../data/{folder_name}%')).first()
            session.close()

            if data_folder is not None:
                box = QMessageBox(QMessageBox.Information, "提示", "当前文件夹名称已存在!!!")
                qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
                box.exec_()
                if box.clickedButton() == qyes:
                    logging.warning(f"Folder name '{folder_name}' already exists.")
                    return
            else:
                # 初始化标志变量
                has_csv = False
                has_edf_or_fif = False
                has_nii = False

                # 遍历文件夹中的所有文件
                for file_name in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file_name)
                    if file_name.endswith('.csv'):
                        has_csv = True
                    elif file_name.endswith('.edf'):
                        has_edf_or_fif = True
                    elif file_name.endswith('.nii'):
                        has_nii = True
                    elif file_name.endswith('.fif'):
                        has_edf_or_fif = True
                        hadprocessed = True

                # 检查是否包含所需的文件类型
                if not (has_csv and has_edf_or_fif and has_nii):
                    box = QMessageBox(QMessageBox.Warning, "缺少文件",
                                      "所选文件夹必须包含一个CSV文件，一个EDF或FIF文件和一个NII文件！")
                    qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
                    box.exec_()
                    if box.clickedButton() == qyes:
                        logging.warning("Selected folder is missing required files.")
                        return
                else:
                    # 复制文件夹到程序的data目录
                    destination_folder = os.path.join('../data', folder_name)
                    try:
                        shutil.copytree(folder_path, destination_folder)
                        logging.info(f"Folder copied to '{destination_folder}'.")
                    except Exception as e:
                        logging.error(
                            f"Failed to copy folder '{folder_path}' to '{destination_folder}'. Error: {str(e)}")
                        QMessageBox.critical(self, "错误", f"复制文件夹时发生错误: {str(e)}")
                        return

                    # 读取用户状态文件，获取上传用户ID
                    path = '../state/user_status.txt'
                    str_user = operate_user.read(path)
                    user = int(str_user)
                    # 使用切片获取前六位数字
                    number_str = folder_name[:6]
                    # 将字符串转换为整数
                    folder_name_personnel_id = int(number_str)
                    folder_name_personnel_name = folder_name[7:]
                    data_path = '../data/' + folder_name
                    # 从数据库中取最大的id，新插入的数据是这个id+1
                    session = SessionClass()
                    max_id = session.query(func.max(Data.id)).scalar()
                    if max_id is None:
                        max_id = 0
                    max_id = max_id + 1

                    session = SessionClass()
                    data = Data(id=max_id, personnel_id=folder_name_personnel_id, data_path=data_path, upload_user=user,
                                personnel_name=folder_name_personnel_name)
                    session.add(data)
                    session.commit()
                    session.close()

                    logging.info(f"Added new data record with ID {max_id}.")
                    if hadprocessed:
                        pass
                    else:
                        # 可视化
                        file_path = data_path + '/EEG.edf'
                        box = QMessageBox(QMessageBox.Information, "信息", "正在进行可视化，请稍候。")
                        qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
                        box.exec_()
                        if box.clickedButton() == qyes:
                            try:
                                data_out.analyze_eeg_data(file_path)
                                logging.info(f"Visualization completed for file: {file_path}")
                                QMessageBox.information(self, "信息", "可视化成功完成")
                            except Exception as e:
                                logging.error(f"Error during visualization: {str(e)}")
                                QMessageBox.warning(self, "警告", f"可视化过程中出现错误: {str(e)}")

                        # 预处理
                        box = QMessageBox(QMessageBox.Information, "信息", "正在进行数据预处理，请稍候。")
                        qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
                        box.exec_()
                        if box.clickedButton() == qyes:
                            try:
                                data_pretreatment.treat(data_path)
                                logging.info(f"Preprocessing completed for data: {data_path}")
                                QMessageBox.information(self, "信息", "预处理成功完成")
                            except Exception as e:
                                logging.error(f"Error during preprocessing: {str(e)}")
                                QMessageBox.warning(self, "警告", f"预处理过程中出现错误: {str(e)}")

                    self.upload_button()  # (不可删)upload_button方法，将刚上传到tb_data表中的记录（即tb_data表最后一条记录）显示到table中
                    logging.info("Upload button called to refresh table.")

    # 将openfile选择的数据存入数据库之后，将刚存入的数据显示到表单中
    def upload_button(self):

        '''
        将数据库tb_data表中最新的一条记录获取下来，得到一个data对象，要判断flag是否等于1，等于1进行下列操作
        data.id, data.data_path, data.upload_user_id, data.upload_time, data.flag

        '''
        session = SessionClass()
        kk = session.query(Data).order_by(Data.id.desc()).first()  # 倒序查找最大的id
        session.close()
        info = []
        if kk is not None:
            info.append([kk.id, kk.personnel_id, kk.data_path, kk.upload_user, kk.personnel_name])

        for data in info:
            row = self.tableWidget.rowCount()  # 当前form有多少行，最后一行是第row-1行
            self.tableWidget.insertRow(row)  # 创建新的行

            if data[3] == 0:  # info[2]等价于data.upload_user_id
                user_name = '普通用户'
            else:
                user_name = '管理员'
            for i in range(len(self.lst) - 1):
                item = QTableWidgetItem()
                # 获得上传数据信息，将其添加到form中
                content = ''
                if i == 0:
                    content = data[0]  # data[0]对应data.id
                elif i == 1:
                    content = data[1]
                elif i == 2:
                    content = data[4]
                elif i == 3:
                    content = data[2]
                elif i == 4:
                    content = user_name  # user_name上边已经处理过
                item.setText(str(content))  # 将content转为string类型才能存入单元格，否则报错。
                self.tableWidget.setItem(row, i, item)
            self.tableWidget.setCellWidget(row, len(self.lst) - 1, self.buttonForRow())  # 在最后一个单元格中加入按钮

    # 将查看、评估按钮封装到widget中
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

    def show_image(self):
        feature_type = self.channel_comboBox.currentText()
        
        if feature_type == "Theta/Alpha/Beta/Gamma功率":
            wave_choice, ok = QInputDialog.getItem(self, "选择波段", "请选择要查看的波段：", 
                                                   ["Theta", "Alpha", "Beta", "Gamma"], 0, False)
            if ok and wave_choice:
                image_path = os.path.join(self.data_path, f'{wave_choice}.png')
                image_name = f"{wave_choice}波段功率"
            else:
                return
        elif feature_type == "均分频带":
            band_choice, ok = QInputDialog.getItem(self, "选择频带", "请选择要查看的频带：", 
                                                   ["Band 1", "Band 2", "Band 3", "Band 4", "Band 5"], 0, False)
            if ok and band_choice:
                band_number = int(band_choice.split()[-1])
                image_path = os.path.join(self.data_path, f'frequency_band_{band_number}.png')
                image_name = f"均分频带 {band_number}"
            else:
                return
        elif feature_type == "时域特征":
            time_feature_choice, ok = QInputDialog.getItem(self, "选择时域特征", "请选择要查看的时域特征：", 
                                                           ["过零率", "方差", "能量", "差分"], 0, False)
            if ok and time_feature_choice:
                image_path = os.path.join(self.data_path, f'time_{time_feature_choice}.png')
                image_name = f"时域特征 - {time_feature_choice}"
            else:
                return
        elif feature_type == "时频域特征":
            image_path = os.path.join(self.data_path, 'frequency_wavelet.png')
            image_name = "时频域特征 - 小波变换"
        elif feature_type == "微分熵":
            image_path = os.path.join(self.data_path, 'differential_entropy.png')
            image_name = "微分熵"
        else:
            logging.warning(f"Unknown feature type selected: {feature_type}")
            return

        if os.path.exists(image_path):
            self.pixmap = QPixmap(image_path)
            if not self.pixmap.isNull():
                self.scene = QGraphicsScene()
                self.pixmap_item = QGraphicsPixmapItem(self.pixmap)
                self.scene.addItem(self.pixmap_item)
                self.graphicsView.setScene(self.scene)
                self.fit_image_in_view()
                self.image_name_label.setText(image_name)  # 更新图像名称标签
                logging.info(f"Successfully displayed image: {image_path}")
            else:
                logging.error(f"Failed to load image: {image_path}")
                QMessageBox.warning(self, "加载图片失败", "无法加载所选特征的图片。")
        else:
            logging.error(f"Image file does not exist: {image_path}")
            QMessageBox.warning(self, "图片不存在", "所选特征的图片文件不存在。可能是因为数据还未进行可视化处理。")

    def fit_image_in_view(self):
        if hasattr(self, 'scene') and self.scene:
            self.graphicsView.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fit_image_in_view()

    # 查看按钮功能
    def checkbutton(self):
        """
        查看按钮的回调函数
        """
        button = self.sender()
        if button:
            row = self.tableWidget.indexAt(button.parent().pos()).row()
            id = self.tableWidget.item(row, 0).text()
            self.id = int(id)
            logging.info(f"Button clicked in row {row}, corresponding ID: {self.id}")

            try:
                session = SessionClass()
                data = session.query(Data).filter(Data.id == self.id).first()
                session.close()
                if data:
                    self.data_path = data.data_path
                    logging.info(f"Data path retrieved from database: {self.data_path}")
                    
                    # 调用show_image方法来显示图片
                    self.show_image()
                else:
                    logging.warning(f"No data found for ID: {self.id}")
                    QMessageBox.warning(self, "数据不存在", f"ID为{self.id}的数据不存在。")
            except Exception as e:
                logging.error(f"An error occurred in checkbutton: {e}")
                QMessageBox.critical(self, "错误", f"查看数据时发生错误: {str(e)}")

    # 删除功能
    def deletebutton(self):
        """
        删除按钮的回调函数
        """
        button = self.sender()
        if button:
            # 确定位置的时候这里是关键
            row = self.tableWidget.indexAt(button.parent().pos()).row()
            id = self.tableWidget.item(row, 0).text()  # 获取当前行数据的ID值
            logging.info(f"Attempting to delete record with ID {id} from the table.")

            if id == self.id:  # 删除的数据为当前查看的数据
                self.id = 0
                self.data_path = ''
                logging.info(f"Current view ID {id} matched, reset ID and data path.")

            # 开始数据库会话
            session = SessionClass()
            try:
                # 根据id从tb_data中获取数据路径path
                data = session.query(Data).filter(Data.id == id).first()
                if data:
                    path = data.data_path
                    logging.info(f"Data path for ID {id}: {path}")

                    # 检查数据路径是否存在
                    if os.path.exists(path):
                        # 删除'../data/'下对应的文件夹
                        shutil.rmtree(path)
                        logging.info(f"Deleted folder at path: {path}")
                    else:
                        logging.warning(f"Data path does not exist: {path}")

                    # 从tb_data中删除对应记录
                    session.query(Data).filter(Data.id == id).delete()
                    session.commit()
                    logging.info(f"Deleted record with ID {id} from tb_data.")

                    # 删除result表中对应的数据
                    session.query(Result).filter(Result.id == id).delete()
                    session.commit()
                    logging.info(f"Deleted record with ID {id} from result table.")
                else:
                    logging.warning(f"No data found with ID {id}.")
            except Exception as e:
                logging.error(f"Error occurred while deleting record with ID {id}: {str(e)}")
                QMessageBox.critical(self, "错误", f"删除记录时发生错误: {str(e)}")
            finally:
                session.close()
                # 从表格中删除记录
                self.tableWidget.removeRow(row)
                logging.info(f"Removed row {row} from table.")

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
    demo_window = Data_View_WindowActions()
    demo_window.show()
    sys.exit(app.exec_())