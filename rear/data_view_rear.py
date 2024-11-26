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
                
                self.tableWidget.setItem(row, 0, QTableWidgetItem(str(data.id)))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(str(data.personnel_id)))
                self.tableWidget.setItem(row, 2, QTableWidgetItem(data.personnel_name))
                self.tableWidget.setItem(row, 3, QTableWidgetItem(data.data_path))
                self.tableWidget.setItem(row, 4, QTableWidgetItem('管理员' if data.upload_user == 1 else '普通用户'))
                if data.upload_time:
                    self.tableWidget.setItem(row, 5, QTableWidgetItem(data.upload_time.strftime("%Y-%m-%d %H:%M:%S")))
                else:
                    self.tableWidget.setItem(row, 5, QTableWidgetItem("N/A"))
                
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

    # 定义通道选���应的事件（没用但不能删）
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
        try:
            # 获取当前用户信息
            path = '../state/user_status.txt'
            user_status = operate_user.read(path)
            
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
                # 获取用户名
                username, ok = QInputDialog.getText(self, "输入", "请输入用户名：")
                if not ok or not username:
                    logging.warning("Username input cancelled or empty")
                    # 删除已复制的文件夹
                    if os.path.exists(target_dir):
                        shutil.rmtree(target_dir)
                    return

                # 根据用户名查询用户信息
                user = session.query(User).filter(User.username == username).first()
                if not user:
                    QMessageBox.warning(self, "警告", f"用户名 {username} 不存在")
                    # 删除已复制的文件夹
                    if os.path.exists(target_dir):
                        shutil.rmtree(target_dir)
                    return

                # 从数据库中取最大的id
                max_id = session.query(func.max(Data.id)).scalar()
                if max_id is None:
                    max_id = 0
                max_id = max_id + 1

                # 创建新的数据记录，确保personnel_id是字符串类型
                new_data = Data(
                    id=max_id,
                    personnel_id=str(user.user_id),  # 确保是字符串类型
                    data_path=target_dir,  # 使用新的目标路径
                    upload_time=datetime.now(),
                    user_id=str(user.user_id),  # 确保是字符串类型
                    personnel_name=user.full_name,
                    upload_user=1 if user.user_type == 'admin' else 0
                )
                
                session.add(new_data)
                session.commit()
                
                logging.info(f"Data uploaded successfully. Path: {target_dir}, Username: {username}")
                QMessageBox.information(self, "提示", "数据上传成功！")
                
                # 刷新表格显示
                self.show_table()
                
            except Exception as e:
                # 发生错误时删除已复制的文件夹
                if os.path.exists(target_dir):
                    shutil.rmtree(target_dir)
                raise e
            finally:
                session.close()
                
        except Exception as e:
            logging.error(f"Error in openfile: {str(e)}")
            QMessageBox.critical(self, "错误", f"上传数据时发生错误：{str(e)}")
            
    def show_table(self):
        """刷新表格显示"""
        self.upload_button()  # 调用upload_button方法刷新表格

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
            info.append([kk.id, kk.personnel_id, kk.data_path, kk.upload_user, kk.personnel_name, kk.upload_time])

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
                elif i == 5:
                    content = data[5].strftime("%Y-%m-%d %H:%M:%S") if data[5] else "N/A"
                item.setText(str(content))  # 将content转为string类型才能存入单元格，否则报错。
                self.tableWidget.setItem(row, i, item)
            self.tableWidget.setCellWidget(row, len(self.lst) - 1, self.buttonForRow())  # 在最后一个单元格中加按钮

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
            else:
                index_window = index_rear.Index_WindowActions()
            
            self.close()
            index_window.show()
            
        except Exception as e:
            logging.error(f"Error in return_index: {str(e)}")
            QMessageBox.critical(self, "错误", f"返回主页时发生错误：{str(e)}")
        finally:
            session.close()

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

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 这里是界面的入口，在这里需要定义QApplication对象，之后界面跳转时不用再重新定义，只需要调用show()函数即可
    app = QApplication(sys.argv)
    # 显示创建的界面
    demo_window = Data_View_WindowActions()
    demo_window.show()
    sys.exit(app.exec_())