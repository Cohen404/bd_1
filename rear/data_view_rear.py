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
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFileDialog, QMessageBox, QTableWidgetItem, \
    QGraphicsPixmapItem, QGraphicsScene, QInputDialog, QProgressDialog
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
        
        # 设置表格列宽
        self.tableWidget.setColumnWidth(3, 400)  # 设置路径列的宽度为400像素
        # 设置表格的选择行为
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        # 设置表格的选择模式
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        # 设置表格的水平表头可见
        self.tableWidget.horizontalHeader().setVisible(True)
        # 设置表格的垂直表头可见
        self.tableWidget.verticalHeader().setVisible(True)
        # 设置表格的水平表头文字对齐方式
        self.tableWidget.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        # 设置表格的垂直表头文字对齐方式
        self.tableWidget.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        # 设置表格的水平表头的样式
        self.tableWidget.horizontalHeader().setStyleSheet("QHeaderView::section{background:skyblue;}")
        # 设置表格的垂直表头的样式
        self.tableWidget.verticalHeader().setStyleSheet("QHeaderView::section{background:skyblue;}")
        # 设置表格内容文字对齐方式
        self.tableWidget.setStyleSheet("QTableWidget::item{padding-left:10px;}")

        # 获取当前用户信息
        try:
            # 从current_user.txt获取用户ID
            with open('../state/current_user.txt', 'r') as f:
                self.user_id = f.read().strip()
            print(f"当前用户ID: {self.user_id}")

            # 从user_status.txt获取用户类型
            path = '../state/user_status.txt'
            user_type = operate_user.read(path)
            self.user_type = (user_type == '1')  # 1表示管理员
            print(f"用户类型: {'管理员' if self.user_type else '普通用户'}")

            # 验证用户信息
            session = SessionClass()
            user = session.query(User).filter(User.user_id == self.user_id).first()
            session.close()

            if user:
                print(f"数据库中的用户信息: ID={user.user_id}, 用户名={user.username}, 类型={user.user_type}")
            else:
                print("警告：在数据库中未找到用户信息")
                QMessageBox.warning(self, "警告", "无法获取用户信息")
                return

        except Exception as e:
            print(f"获取用户信息时出错: {str(e)}")
            QMessageBox.critical(self, "错误", f"获取用户信息失败：{str(e)}")
            return

        # 显示表格
        self.show_table()

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

        window_manager = WindowManager()
        window_manager.register_window('data_view', self)

    def get_user_type(self, user_id):
        """
        获取用户类型
        """
        session = SessionClass()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                return 1 if user.user_type == 'admin' else 0
            return 0
        except Exception as e:
            logging.error(f"Error getting user type: {str(e)}")
            return 0
        finally:
            session.close()

    def show_table(self):
        """
        显示数据表格
        """
        session = SessionClass()
        try:
            print(f"\n开始查询数据表...")
            print(f"当前用户ID: {self.user_id}, 是否管理员: {self.user_type}")

            if self.user_type:  # 管理员
                print("管理员查询所有数据")
                data_list = session.query(Data).all()
            else:  # 普通用户
                print(f"普通用户查询自己的数据: user_id = {self.user_id}")
                data_list = session.query(Data).filter(Data.user_id == self.user_id).all()

            print(f"查询到 {len(data_list)} 条数据")

            # 清空表格
            self.tableWidget.setRowCount(0)

            for data in data_list:
                print(f"处理数据: ID={data.id}, 用户ID={data.user_id}, 路径={data.data_path}")
                row = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row)
                
                # 获取路径的最后一个目录名
                display_path = os.path.basename(data.data_path)
                
                # 创建并设置各列的项目
                id_item = QTableWidgetItem(str(data.id))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, 0, id_item)
                
                personnel_id_item = QTableWidgetItem(str(data.personnel_id))
                personnel_id_item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, 1, personnel_id_item)
                
                name_item = QTableWidgetItem(data.personnel_name)
                name_item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, 2, name_item)
                
                # 创建路径项并设置工具提示（鼠标悬停显示完整路径）
                path_item = QTableWidgetItem(display_path)
                path_item.setToolTip(data.data_path)  # 设置完整路径为工具提示
                path_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # 左对齐
                self.tableWidget.setItem(row, 3, path_item)
                
                user_type_item = QTableWidgetItem('管理员' if data.upload_user == 1 else '普通用户')
                user_type_item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, 4, user_type_item)
                
                if data.upload_time:
                    time_item = QTableWidgetItem(data.upload_time.strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    time_item = QTableWidgetItem("N/A")
                time_item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, 5, time_item)
                
                self.tableWidget.setCellWidget(row, 6, self.buttonForRow())

            if len(data_list) == 0:
                print("没有找到任何数据")
                QMessageBox.information(self, "提示", "暂无数据")

            logging.info(f"Data table refreshed successfully with {len(data_list)} records")
        except Exception as e:
            print(f"显示数据表格时出错: {str(e)}")
            logging.error(f"Error displaying data table: {str(e)}")
            QMessageBox.critical(self, "错误", f"显示数据表格失败：{str(e)}")
        finally:
            session.close()

    # 定义通道选应的事件（没用但不能删）
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

    def openfile(self):
        """
        打开文件对话框，选择要上传的数据文件
        """
        # 先打开文件选择对话框
        source_dir = QFileDialog.getExistingDirectory(self, "选择文件夹", os.getcwd())
        if not source_dir:
            logging.info("File selection cancelled")
            return
            
        # 检查是否选择了文件
        if not os.path.exists(source_dir):
            QMessageBox.warning(self, "警告", "选择的文件夹不存在")
            return

        # 获取源文件夹名称
        source_dir_name = os.path.basename(source_dir)
        
        # 构建目标目录路径
        target_base_dir = '../data'
        target_dir = os.path.join(target_base_dir, source_dir_name)
        
        # 如果目标目录已存在，则添加后缀
        suffix = 1
        while os.path.exists(target_dir):
            new_name = f"{source_dir_name}_{suffix}"
            target_dir = os.path.join(target_base_dir, new_name)
            suffix += 1
        
        # 确保目标基础目录存在
        os.makedirs(target_base_dir, exist_ok=True)
        
        # 复制文件夹
        try:
            shutil.copytree(source_dir, target_dir)
            logging.info(f"Directory copied from {source_dir} to {target_dir}")
        except Exception as e:
            logging.error(f"Failed to copy directory: {str(e)}")
            QMessageBox.critical(self, "错误", f"复制文件夹时发生错误：{str(e)}")
            return
            
        session = SessionClass()
        try:
            # 获取当前用户信息
            user = session.query(User).filter(User.user_id == self.user_id).first()
            if not user:
                QMessageBox.warning(self, "警告", "无法获取当前用户信息")
                if os.path.exists(target_dir):
                    shutil.rmtree(target_dir)
                return

            # 从数据库中取最大的id
            max_id = session.query(func.max(Data.id)).scalar()
            if max_id is None:
                max_id = 0
            max_id = max_id + 1

            # 创建新的数据记录
            new_data = Data(
                id=max_id,
                personnel_id=str(user.user_id),
                data_path=target_dir,
                upload_time=datetime.now(),
                user_id=str(user.user_id),
                personnel_name=user.full_name,
                upload_user=1 if user.user_type == 'admin' else 0
            )
            
            session.add(new_data)
            session.commit()
            
            logging.info(f"Data uploaded successfully. Path: {target_dir}, Username: {user.username}")
            QMessageBox.information(self, "提示", "数据上传成功！")
            
            # 刷新表格显示
            self.show_table()
            
        except Exception as e:
            # 发生错误时删除已复制的文件夹
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            session.rollback()
            logging.error(f"Error during data upload: {str(e)}")
            QMessageBox.critical(self, "错误", f"数据上传失败：{str(e)}")
        finally:
            session.close()
            
            
    def show_table(self):
        """刷新表格显示"""
        self.upload_button()  # 调用upload_button方法刷新表格

    # 将openfile选择的数据存入数据库之后，将刚存入的数据显示到表单中
    def upload_button(self):
        """
        将数据库tb_data表中最新的一条记录获取下来并显示到表格中
        """
        session = SessionClass()
        kk = session.query(Data).order_by(Data.id.desc()).first()  # 倒序查找最大的id
        session.close()
        
        if kk is not None:
            row = self.tableWidget.rowCount()  # 当前form有多少行
            self.tableWidget.insertRow(row)  # 创建新的行
            
            # 获取路径的最后一个目录名
            display_path = os.path.basename(kk.data_path)
            
            # 创建并设置各列的项目
            id_item = QTableWidgetItem(str(kk.id))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(row, 0, id_item)
            
            personnel_id_item = QTableWidgetItem(str(kk.personnel_id))
            personnel_id_item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(row, 1, personnel_id_item)
            
            name_item = QTableWidgetItem(kk.personnel_name)
            name_item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(row, 2, name_item)
            
            # 创建路径项并设置工具提示
            path_item = QTableWidgetItem(display_path)
            path_item.setToolTip(kk.data_path)  # 设置完整路径为工具提示
            path_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # ���对齐
            self.tableWidget.setItem(row, 3, path_item)
            
            user_type_item = QTableWidgetItem('管理员' if kk.upload_user == 1 else '普通用户')
            user_type_item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(row, 4, user_type_item)
            
            if kk.upload_time:
                time_item = QTableWidgetItem(kk.upload_time.strftime("%Y-%m-%d %H:%M:%S"))
            else:
                time_item = QTableWidgetItem("N/A")
            time_item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(row, 5, time_item)
            
            self.tableWidget.setCellWidget(row, 6, self.buttonForRow())

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
        # 预处理
        self.preprocess_pushButton = QtWidgets.QPushButton('预处理')
        self.preprocess_pushButton.setStyleSheet(''' text-align : center;
                                                  background-color : LightGreen;
                                                  height : 30px;
                                                  border-style: outset;
                                                  font : 13px  ''')

        # 绑定按钮事件
        self.check_pushButton.clicked.connect(self.checkbutton)
        self.delete_pushButton.clicked.connect(self.deletebutton)
        self.preprocess_pushButton.clicked.connect(self.preprocessbutton)

        hLayout = QtWidgets.QHBoxLayout()
        hLayout.addWidget(self.check_pushButton)
        hLayout.addWidget(self.preprocess_pushButton)
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

                    # 删除result表中对应数据
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

    def get_current_user(self):
        """
        获取当前用户信息
        """
        try:
            with open('../state/current_user.txt', 'r') as f:
                username = f.read().strip()
            
            session = SessionClass()
            user = session.query(User).filter(User.username == username).first()
            session.close()
            
            if user:
                return user.user_id, user.user_type == 'admin'
            return None, False
        except Exception as e:
            logging.error(f"Error getting current user: {str(e)}")
            return None, False

    # 添加预处理按钮的回调函数
    def preprocessbutton(self):
        """
        预处理按钮的回调函数，执行数据预处理和特征提取
        """
        button = self.sender()
        if button:
            row = self.tableWidget.indexAt(button.parent().pos()).row()
            data_id = int(self.tableWidget.item(row, 0).text())  # 获取数据ID
            
            try:
                # 从数据库获取完整路径
                session = SessionClass()
                data = session.query(Data).filter(Data.id == data_id).first()
                if not data:
                    QMessageBox.warning(self, "警告", "找不到对应的数据记录")
                    return
                    
                data_path = data.data_path  # 使用数据库中存储的完整路径
                session.close()

                # 创建进度条对话框
                progress_dialog = QProgressDialog("正在处理数据...", "取消", 0, 100, self)
                progress_dialog.setWindowTitle("处理中")
                progress_dialog.setWindowModality(Qt.WindowModal)
                progress_dialog.setMinimumDuration(0)
                progress_dialog.setAutoClose(True)
                progress_dialog.setAutoReset(True)

                # 创建处理线程
                self.processing_thread = ProcessingThread(data_path)

                # 连接信号
                self.processing_thread.progress.connect(progress_dialog.setValue)
                self.processing_thread.finished.connect(self.processing_completed)
                self.processing_thread.error.connect(self.processing_error)
                progress_dialog.canceled.connect(self.processing_thread.terminate)

                # 启动线程
                self.processing_thread.start()

                logging.info(f"Started processing data from: {data_path}")

            except Exception as e:
                logging.error(f"Error setting up processing: {str(e)}")
                QMessageBox.critical(self, "错误", f"设置处理任务时出错：{str(e)}")

    # 添加处理完成的回调函数
    def processing_completed(self):
        """处理完成后的回调"""
        logging.info("Data processing completed successfully")
        QMessageBox.information(self, "成功", "数据预处理和特征提取已完成")

    # 添加处理错误的回调函数
    def processing_error(self, error_msg):
        """处理错误的回调"""
        logging.error(f"Error during processing: {error_msg}")
        QMessageBox.critical(self, "错误", f"处理过程中出现错误：{error_msg}")

# 添加一个处理线程类
class ProcessingThread(QThread):
    """数据处理线程"""
    finished = pyqtSignal()  # 处理完成信号
    error = pyqtSignal(str)  # 错误信号
    progress = pyqtSignal(int)  # 进度信号

    def __init__(self, data_path):
        super().__init__()
        self.data_path = data_path

    def run(self):
        try:
            # 数据预处理 - 30%进度
            self.progress.emit(10)
            data_pretreatment.treat(self.data_path)
            self.progress.emit(30)

            # 查找EDF文件 - 40%进度
            edf_files = [f for f in os.listdir(self.data_path) if f.endswith('.edf')]
            if not edf_files:
                raise Exception("未找到EDF文件")
            self.progress.emit(40)

            # 特征提取和可视化 - 60-100%进度
            file_path = os.path.join(self.data_path, edf_files[0])
            self.progress.emit(60)
            data_out.analyze_eeg_data(file_path)
            self.progress.emit(100)

            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 这里是界面的入口，在这里需要定义QApplication对象，之后界面跳转时不用再重新定义，只需要调用show()函数即可
    app = QApplication(sys.argv)
    # 显示创建的界面
    demo_window = Data_View_WindowActions()
    demo_window.show()
    sys.exit(app.exec_())