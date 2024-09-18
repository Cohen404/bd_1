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
from front.model_control_UI import Ui_model_Control
from rear import index_rear, admin_rear
from sql_model.tb_result import Result
from sql_model.tb_model import Model
from state import operate_user
from util.db_util import SessionClass
from model.CNN import Rnn
from model.classifer_8 import BasicConvResBlock
from model.classifer_8 import CNN
import logging

class UserFilter(logging.Filter):
    def __init__(self, userType):
        super().__init__()
        self.userType = userType

    def filter(self, record):
        record.userType = self.userType
        return True

class model_control_Controller(Ui_model_Control):
    def __init__(self):
        super(model_control_Controller, self).__init__()
        self.id = None
        self.export_btn = None
        self.delete_btn = None
        self.model = None
        self.showUi()
        self.return_btn.clicked.connect(self.returnIndex)
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

    def showUi(self):
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
        # header

        session = SessionClass()
        result = session.query(Result).order_by(Result.id.desc()).first()
        session.close()
        # 获取tb_result表中最新的一条记录，得到result对象

    def showTable(self, model_list):
        model_type_mapping = {
             '0':"普通应激评估模型",
                '1':"抑郁评估模型",
                '2':"焦虑评估模型"
        }
        if model_list is None:
            return
        current_row_count = 0  # 当前表格有多少行
        for model in model_list:
            self.table_widget.insertRow(current_row_count)
            for j in range(0, self.table_widget.columnCount() + 1):
                if j == 0:#模型类别
                    self.table_widget.setItem(current_row_count, j, QTableWidgetItem(model_type_mapping.get(str(model[0]))))
                elif j == 1:#模型路径
                    self.table_widget.setItem(current_row_count, j, QTableWidgetItem(str(model[1])))
                elif j == 2:#模型名称
                    model_name = os.path.basename(model[1])
                    self.table_widget.setItem(current_row_count, j, QTableWidgetItem(model_name))
                elif j == 3:#上传时间
                    self.table_widget.setItem(current_row_count, j, QTableWidgetItem(str(model[2])))
                else:
                    self.table_widget.setCellWidget(current_row_count, j, self.buttonForRow())
                    self.delete_btn.clicked.connect(self.deleteModel)
                    self.export_btn.clicked.connect(partial(self.exportModel, model))
            current_row_count += 1

    def uploadModel(self):
        model_types = ["普通应激评估模型", "抑郁评估模型", "焦虑评估模型"]
        model_type_name, okPressed = QInputDialog.getItem(self, "上传模型", "模型类型:", model_types, 0, False)

        if okPressed and model_type_name:
            model_type = model_types.index(model_type_name)
            logging.info(f"Selected model type: {model_type_name} (Index: {model_type})")

            model_path, _ = QFileDialog.getOpenFileName(self, "选择模型", "", "")
            if model_path:
                relative_model_path = os.path.relpath(model_path)  # 获取相对路径
                logging.info(f"Selected model file path: {relative_model_path}")

                # Update model attributes
                self.updateModelAttributes(model_type, relative_model_path)

                # Synchronize with database
                session = SessionClass()
                existing_model = session.query(Model).filter(Model.model_type == model_type).first()

                if existing_model is not None:
                    # Update existing record
                    existing_model.model_path = relative_model_path
                    existing_model.create_time = datetime.now()
                    logging.info(
                        f"Updated existing model record for type {model_type_name}. New path: {relative_model_path}")
                else:
                    # Create new record
                    model = Model(model_type=model_type, model_path=relative_model_path, create_time=datetime.now())
                    session.add(model)
                    logging.info(f"Added new model record for type {model_type_name}. Path: {relative_model_path}")

                session.commit()
                session.close()
                logging.info(f"Model upload and database update completed successfully.")
            else:
                logging.warning("Model upload canceled by the user.")
        else:
            logging.warning("No model type selected.")


    def updateModelAttributes(self, model_type, model_path):
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

    # def getCurrentModel(self):
    #     return self.model

    # todo 返回主页
    def returnIndex(self):
        path = '../state/user_status.txt'
        user = operate_user.read(path)  # 0表示普通用户，1表示管理员

        if user == '0':  # 返回系统首页
            self.index = index_rear.Index_WindowActions()
        elif user == '1':  # 返回管理员首页
            self.index = admin_rear.AdminWindowActions()
        self.close()
        self.index.show()


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    w = model_control_Controller()
    w.show()
    w.setStyleSheet('''QWidget{background-color:rgb(212, 226, 244);}''')
    app.exec()
