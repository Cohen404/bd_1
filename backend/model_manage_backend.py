# 文件功能：模型控制界面的后端逻辑
# 该脚本实现了模型控制界面的功能，包括模型上传、删除、导出等操作，以及与数据库的交互

import os
import sys
import time
sys.path.append('../')
from datetime import datetime
from functools import partial
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QRadioButton, QTableWidgetItem, QWidget, QPushButton, QHBoxLayout, \
    QMessageBox, QFileDialog, QInputDialog
import shutil
from front.model_manage_UI import Ui_model_Control
from backend import admin_index_backend, index_backend
from sql_model.tb_result import Result
from sql_model.tb_model import Model
from state import operate_user
from util.db_util import SessionClass
import logging
from util.window_manager import WindowManager
from sql_model.tb_user import User
from config import (
    USER_STATUS_FILE, 
    CURRENT_USER_FILE, 
    LOG_FILE, 
    MODEL_STATUS_FILE,
    DATA_DIR
)

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

class model_control_Controller(Ui_model_Control):
    """
    模型控制界面的主要类，继承自前端UI类
    """
    def __init__(self):
        """
        初始化模型控制界面
        """
        super(model_control_Controller, self).__init__()
        self.id = None
        self.export_btn = None
        self.delete_btn = None
        self.model = None
        self._admin_window = None
        self.showUi()
        self.return_btn.clicked.connect(self.returnIndex)
        
        # 初始化窗口管理器
        window_manager = WindowManager()
        window_manager.register_window('model_control', self)

    def showUi(self):
        """
        显示界面并初始化数据
        """
        # 页面初始化时，将tb_Model中的数据全部都出来，显示到table中
        session = SessionClass()
        data = session.query(Model).all()
        session.close()
        model_list = []
        for item in data:
        #     #model_list.append([item.id, item.test_time, item.test_acc, item.cv_acc, item.model_path, item.use])
            model_list.append([item.model_type, item.model_path,item.create_time])

        # [id,创建时间,测试集准确率,交叉验证准确率,模型路径]
        # model_list = [[1, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), '96.6%', '95.8%',
        #                '../result/model/cnn_2023_01_19_18_05.pt'],
        #               [2, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), '97.6%', '98.8%',
        #                '../result/model/cnn_2023_01_15_20_49.pt']]
        self.showTable(model_list)
        self.show_nav()

        self.upload_btn.clicked.connect(self.uploadModel)

    def show_nav(self):
        """
        显示导航栏（当前未实现具体功能）
        """
        # header
        session = SessionClass()
        result = session.query(Result).order_by(Result.id.desc()).first()
        session.close()
        # 获取tb_result表中最新的一条记录，得到result对象

    def showTable(self, model_list):
        """
        在表格中显示模型列表
        
        参数:
        model_list (list): 包含模型信息的列表
        """
        model_type_mapping = {
             '0': "普通应激评估模型",
             '1': "抑郁评估模型",
             '2': "焦虑评估模型"
        }
        if model_list is None:
            return
        current_row_count = 0  # 当前表格有多少行
        for model in model_list:
            self.table_widget.insertRow(current_row_count)
            for j in range(0, self.table_widget.columnCount() + 1):
                if j == 0:  # 模型类别
                    self.table_widget.setItem(current_row_count, j, QTableWidgetItem(model_type_mapping.get(str(model[0]))))
                elif j == 1:  # 模型路径
                    self.table_widget.setItem(current_row_count, j, QTableWidgetItem(str(model[1])))
                elif j == 2:  # 模型名称
                    model_name = os.path.basename(model[1])
                    self.table_widget.setItem(current_row_count, j, QTableWidgetItem(model_name))
                elif j == 3:  # 上传时间
                    self.table_widget.setItem(current_row_count, j, QTableWidgetItem(str(model[2])))
                else:
                    self.table_widget.setCellWidget(current_row_count, j, self.buttonForRow())
                    self.delete_btn.clicked.connect(self.deleteModel)
                    self.export_btn.clicked.connect(partial(self.exportModel, model))
            current_row_count += 1

    def delete_keras_files(self, directory):
        """
        删除指定目录下的所有.keras文件
        
        参数:
        directory (str): 要删除文件的目录路径
        """
        for filename in os.listdir(directory):
            if filename.endswith('.keras'):
                file_path = os.path.join(directory, filename)
                os.remove(file_path)
                print(f"Deleted file: {file_path}")

    def uploadModel(self):
        """
        上传模型的处理函数
        """
        model_types = ["普通应激评估模型", "抑郁评估模型", "焦虑评估模型"]
        model_type_name, okPressed = QInputDialog.getItem(self, "上传模型", "模型类型:", model_types, 0, False)

        if okPressed and model_type_name:
            model_type = model_types.index(model_type_name)
            logging.info(f"Selected model type: {model_type_name} (Index: {model_type})")

            model_path, _ = QFileDialog.getOpenFileName(self, "选择模型", "", "")
            if model_path:
                # 创建临时文件夹
                tmp_dir = "../tmp"
                os.makedirs(tmp_dir, exist_ok=True)

                # 复制文件到临时文件夹
                tmp_file = os.path.join(tmp_dir, os.path.basename(model_path))
                shutil.copy(model_path, tmp_file)
                logging.info(f"Copied model file to temporary directory: {tmp_file}")

                # 根据模型类型选择目标目录
                model_type_dir_mapping = {
                    0: "./model/yingji",
                    1: "./model/yiyu",
                    2: "./model/jiaolv"
                }
                target_dir = model_type_dir_mapping.get(model_type)

                if target_dir:
                    # 删除目标目录中的所有.keras文件
                    for filename in os.listdir(target_dir):
                        if filename.endswith('.keras'):
                            file_path = os.path.join(target_dir, filename)
                            os.remove(file_path)
                            logging.info(f"Deleted existing model file: {file_path}")

                    # 将临时文件移动到目标目录
                    target_path = os.path.join(target_dir, os.path.basename(tmp_file))
                    shutil.move(tmp_file, target_path)
                    logging.info(f"Moved model file to: {target_path}")

                    # 更新模型属性
                    self.updateModelAttributes(model_type, target_path)

                    # 同步数据库
                    session = SessionClass()
                    existing_model = session.query(Model).filter(Model.model_type == model_type).first()

                    if existing_model is not None:
                        # 更新现有记录
                        existing_model.model_path = target_path
                        existing_model.create_time = datetime.now()
                        logging.info(f"Updated existing model record for type {model_type_name}. New path: {target_path}")
                    else:
                        # 创建新记录
                        model = Model(model_type=model_type, model_path=target_path, create_time=datetime.now())
                        session.add(model)
                        logging.info(f"Added new model record for type {model_type_name}. Path: {target_path}")

                    session.commit()
                    session.close()
                    logging.info(f"Model upload and database update completed successfully.")

                    # 清理临时文件夹
                    shutil.rmtree(tmp_dir)
                    logging.info("Temporary directory cleaned up.")

                    QMessageBox.information(self, "上传成功", f"{model_type_name}上传成功！")
                else:
                    logging.warning(f"No target directory found for model type: {model_type_name}")
                    QMessageBox.warning(self, "上传失败", "未找到目标目录，请检查配置。")
            else:
                logging.warning("Model upload canceled by the user.")
        else:
            logging.warning("No model type selected.")

    def updateModelAttributes(self, model_type, model_path):
        """
        更新模型属性并在表格中显示
        
        参数:
        model_type (int): 模型类型
        model_path (str): 模型文件路径
        """
        model_type_mapping = {
            '0': "普通应激评估模型",
            '1': "抑郁评估模型",
            '2': "焦虑评估模型"
        }
        # 从模型路径中提取模型的名称
        model_name = os.path.basename(model_path)
        # 获取当前的时间作为上传时间
        upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 遍历表格的每一行
        for i in range(self.table_widget.rowCount()):
            # 找到与模型类型匹配的行
            if self.table_widget.item(i, 0).text() == model_type_mapping.get(str(model_type)):
                # 更新表格中的数据
                self.table_widget.item(i, 1).setText(model_path)
                self.table_widget.item(i, 2).setText(model_name)
                self.table_widget.item(i, 3).setText(upload_time)
                break
        else:  # 如果没有找到匹配的模型类型
            # 在表格中添加一行
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)

            # 填入数据
            self.table_widget.setItem(row_position, 0, QTableWidgetItem(model_type_mapping.get(str(model_type))))
            self.table_widget.setItem(row_position, 1, QTableWidgetItem(model_path))
            self.table_widget.setItem(row_position, 2, QTableWidgetItem(model_name))
            self.table_widget.setItem(row_position, 3, QTableWidgetItem(upload_time))
            self.table_widget.setCellWidget(row_position, 4, self.buttonForRow())
            self.delete_btn.clicked.connect(self.deleteModel)
            self.export_btn.clicked.connect(
                partial(self.exportModel, [model_type, model_path, model_name, upload_time]))

    def buttonForRow(self):
        """
        为表格行创建按钮组件
        
        返回:
        QWidget: 包含删除和导出按钮的小部件
        """
        widget = QWidget()
        self.delete_btn = QPushButton('删除')
        self.delete_btn.setStyleSheet(''' text-align : center;
                                          background-color : NavajoWhite;
                                          height : 30px;
                                          width :40px;
                                          border-style: outset;
                                          font : 13px  ''')

        self.export_btn = QPushButton('导出')
        self.export_btn.setStyleSheet(''' text-align : center;
                                    background-color : LightCoral;
                                    height : 30px;
                                    width :40px;
                                    border-style: outset;
                                    font : 13px; ''')

        hLayout = QHBoxLayout()
        hLayout.addWidget(self.delete_btn)
        hLayout.addWidget(self.export_btn)
        hLayout.setContentsMargins(5, 2, 5, 2)
        widget.setLayout(hLayout)
        return widget

    def deleteModel(self):
        """
        删除模型的处理函数
        """
        button = self.sender()
        if button:
            row = self.table_widget.indexAt(button.parent().pos()).row()  # 获取按钮所在行
            model_type_num = self.table_widget.item(row, 0).text()
            model_type_mapping = {
                "普通应激评估模型": '0',
                "抑郁评估模型": '1',
                "焦虑评估模型": '2'
            }
            model_type = model_type_mapping.get(model_type_num)

            logging.info(f"Attempting to delete model of type: {model_type_num} (Mapped to: {model_type})")

            # 确认删除
            box = QMessageBox(QMessageBox.Question, "提示", "请确认是否要删除该模型？")
            qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
            qno = box.addButton(self.tr("取消"), QMessageBox.NoRole)
            box.exec_()

            if box.clickedButton() == qyes:
                self.table_widget.removeRow(row)
                session = SessionClass()
                data = session.query(Model).filter(Model.model_type == model_type).first()

                if data:
                    path = data.model_path  # 根据模型类型获取存储路径
                    logging.info(f"Deleting model file at path: {path}")

                    if os.path.exists(path):
                        os.remove(path)  # 删除对应的文件
                        logging.info(f"Deleted model file: {path}")
                    else:
                        logging.warning(f"Model file not found at path: {path}")

                    # 删除数据库中的记录
                    session.query(Model).filter(Model.model_type == model_type).delete()
                    session.commit()
                    logging.info(f"Deleted model record from database for type: {model_type_num}")
                else:
                    logging.warning(f"No model record found for type: {model_type_num}")

                session.close()
            else:
                logging.info("Model deletion canceled by the user.")

    def exportModel(self, model):
        """
        导出模型的处理函数
        
        参数:
        model (list): 包含模型信息的列表
        """
        if model:
            model_path = model[1]
            model_name = os.path.basename(model_path)  # 获取模型文件名
            logging.info(f"Exporting model with path: {model_path}")

            save_path = QFileDialog.getExistingDirectory(self, "选取模型导出位置", "C:/")

            if save_path:
                new_path = os.path.join(save_path, model_name)
                logging.info(f"Saving model to: {new_path}")

                try:
                    shutil.copy(model_path, new_path)  # 复制文件
                    logging.info(f"Model copied successfully from {model_path} to {new_path}")

                    box = QMessageBox(QMessageBox.Information, "提示", "模型已导出到" + save_path)
                    qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
                    box.exec_()
                except Exception as e:
                    logging.error(f"Error exporting model: {e}")
                    box = QMessageBox(QMessageBox.Critical, "错误", f"模型导出失败: {str(e)}")
                    qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
                    box.exec_()

    # todo 返回主页
    def returnIndex(self):
        """
        返回到相应的主页面
        根据用户类型返回到管理员或普通用户页面
        """
        try:
            # 创建新窗口前先保存引用
            self._admin_window = admin_index_backend.AdminWindowActions()
            
            # 先显示新窗口
            self._admin_window.show()
            # 再隐藏当前窗口
            self.hide()
            # 最后关闭当前窗口
            self.close()
            
            logging.info("Returned to admin page successfully")
        except Exception as e:
            logging.error(f"Error in returnIndex: {str(e)}")
            QMessageBox.critical(self, "错误", f"返回管理页面时发生错误：{str(e)}")


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    window = model_control_Controller()
    window_manager = WindowManager()
    window_manager.register_window('model_control', window)
    window_manager.show_window('model_control')
    sys.exit(app.exec_())