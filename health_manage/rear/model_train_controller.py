import shutil
from datetime import datetime

from PyQt5.QtCore import Qt, QBasicTimer
from PyQt5.QtGui import QPixmap, QImage, QFont
from front.model_train_UI import Ui_model_train
import sys

sys.path.append('../')
from PyQt5.QtWidgets import *
from model.classifer_3 import train, modelTest
from functools import partial
import os
import time
from model.kfold import kfold_val
from PyQt5.QtCore import QThread, pyqtSignal
import state.operate_user as operate_user
from rear import index_rear, admin_rear
from sql_model.tb_data import Data
from sql_model.tb_result import Result
from sql_model.tb_train import Train
from util.db_util import SessionClass
from model.CNN import Rnn
from model.classifer_8 import BasicConvResBlock
from model.classifer_8 import CNN


class model_train_Controller(Ui_model_train):

    def __init__(self):
        super(model_train_Controller, self).__init__()
        self.testAcc = None
        self.train_end_time = None
        self.train_start_time = None
        self.delete_btn = None
        self.cal = None
        self.val_num = None
        self.epochs = None
        self.lr = None
        self.val_thread = None
        self.test_thread = None
        self.train_thread = None
        self.train_btn = None
        self.test_btn = None
        self.model_path = None
        self.data_path = None
        self.test_process = None
        self.user_status_path = '../state/user_status.txt'
        self.timer = QBasicTimer()  # 定时器对象
        self.step = 0  # 进度值
        self.final_result = []
        self.showUi()
        self.btn_train.clicked.connect(self.valModel)
        self.upload_pushButton.clicked.connect(self.openEvent)
        self.return_btn.clicked.connect(self.returnIndex)

    def show_nav(self):
        # header

        session = SessionClass()
        result = session.query(Result).order_by(Result.id.desc()).first()
        session.close()
        # 获取tb_result表中最新的一条记录，得到result对象
        if result is not None:  # result存在
            time_content = result.remaining_time  # 剩余时间
            state_content = result.health_status  # 评估状态
            result_time_content = result.result_time  # 评估时间
            statu_content = result.health_status  # 健康状态

            self.time_show.setText(str(time_content) + ' h')
            if statu_content == 0:  # 健康状态，灯为绿色
                self.statu_show.setStyleSheet(
                    "min-width: 20px; min-height: 20px;max-width:20px; max-height: 20px;border-radius: 11px;  border:1px solid black;background:green")  # 根据状态换相应颜色
            elif statu_content == 1:  # 声学故障，灯为黄色
                self.statu_show.setStyleSheet(
                    "min-width: 20px; min-height: 20px;max-width:20px; max-height: 20px;border-radius: 11px;  border:1px solid black;background:yellow")  # 根据状态换相应颜色
            elif statu_content == 2:  # 机械故障，灯为红色
                self.statu_show.setStyleSheet(
                    "min-width: 20px; min-height: 20px;max-width:20px; max-height: 20px;border-radius: 11px;  border:1px solid black;background:red")  # 根据状态换相应颜色

            # bottom
            data_time_now = datetime.now().replace(microsecond=0, second=0)  # 获取到当前时间
            no_second_result_time = result_time_content.replace(second=0)
            time_span = (data_time_now - no_second_result_time)
            time_span_current = str(time_span.days) + '天' + str(int(time_span.seconds / 3600)) + '时' + str(
                int((time_span.seconds % 3600) / 60)) + '分之前'
            self.evaluate_time.setText('评估时间: ' + str(result_time_content))
            self.pass_time.setText(str(time_span_current))

    def showUi(self):
        # todo 页面初始化时，将tb_data中 flag = 0 （文件夹）存储为文件夹的数据查询出来，显示到table中
        session = SessionClass()
        data = session.query(Data).filter(Data.flag == 0).all()
        session.close()
        data_list = []
        for item in data:
            if item.upload_user_id == 0:
                data_list.append([item.id, item.upload_time, '普通用户', item.data_path])
            if item.upload_user_id == 1:
                data_list.append([item.id, item.upload_time, '管理员', item.data_path])
        self.show_nav()
        self.showTable(data_list)
        self.num_cross_val.addItems(['5', '10', '20'])  # todo 数据库中存储的值 交叉验证次数
        self.lrText.addItems(['0.01', '0.001'])  # todo 数据库中存储的值 学习率
        self.epochsText.addItems(['5', '10', '20'])  # todo 数据库中存储的值 训练次数
        self.model_path = ''  # todo 替换成数据库中use标记为使用的模型路径
        self.test_acc.setText(str(95.23) + '%')  # todo 将最近一次交叉验证结果和交叉验证平均准确率与测试集准确率查询，并在对应位置展示
        self.cross_val_acc.setText(str(95.02) + '%')
        img_dir = '../result/val_img/2023_02_21_12_43'  # todo 查询最近一次交叉验证生成的图片文件夹路径，进行展示
        img_list = os.listdir(img_dir)
        img_path_list = []
        res = []
        self.cross_val_result.clear()
        for i, ele in enumerate(img_list):
            result = '第' + str(i + 1) + '次交叉验证结果'
            res.append(result)
            img = os.path.join(img_dir, ele)
            img_path_list.append(img)
        self.cross_val_result.addItems(res)
        self.showImg([img_path_list[0]])
        if self.cross_val_result.currentIndex() == 0:
            frame = QImage(img_path_list[0])
            pix = QPixmap.fromImage(frame)
            item = QGraphicsPixmapItem(pix)
            scene = QGraphicsScene()
            scene.addItem(item)
            self.result_img.setScene(scene)
            self.result_img.fitInView(QGraphicsPixmapItem(QPixmap(pix)))



        # self.result_img.setPixmap()
        self.cross_val_result.currentIndexChanged.connect(partial(self.showImg, img_path_list, ))

    # todo 返回主页
    def returnIndex(self):
        user = operate_user.read(self.user_status_path)  # 0表示普通用户，1表示管理员
        if user == '0':  # 返回系统首页
            self.index = index_rear.Index_WindowActions()
        elif user == '1':  # 返回管理员首页
            self.index = admin_rear.AdminWindowActions()
        self.hide()
        self.index.show()

    def openEvent(self):
        dir_path = QFileDialog.getExistingDirectory(None, "选取文件夹", "C:/")
        if dir_path != '' or len(dir_path) != 0:
            if any((name.endswith('.mat')) for name in os.listdir(dir_path)):
                self.uploadData_thread = upLoadData(dir_path)
                self.uploadData_thread._rule.connect(self.showUploadRes)
                self.uploadData_thread.start()
            else:
                box = QMessageBox(QMessageBox.Information, "提示", "请上传正确格式数据进行训练和测试！！！")
                yes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
                box.exec_()
                if box.clickedButton() == yes:
                    return

    def showUploadRes(self):
        with open('../result/status/uploadData.txt', mode='r', encoding='utf-8') as f:
            contents = f.readlines()
            rela_path = contents[0]
            print(rela_path)
            f.close()
            os.remove('../result/status/uploadData.txt')
        if rela_path:
            data_time = datetime.now().replace(microsecond=0)  # 获取到当前时间，将当前时间微秒去掉不显示
            # 获取当前用户信息
            str_user = operate_user.read(self.user_status_path)
            user = int(str_user)
            if user == 0:
                user_name = '普通用户'
            else:
                user_name = '管理员'

            session = SessionClass()
            data = Data(data_path=rela_path, upload_user_id=user, flag=0)
            session.add(data)
            session.commit()

            '''
            数据上传后，flag = 0 表示该数据为上传的一批数据(进行模型训练和测试使用)
            [1(数据id), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())(上传时间), '普通用户/管理员'(上传用户), './../Data/programs'(文件相对路径)]
            将数据存入tb_data
            rela_path：相对路径（数据库中存数据相对路径）
            user：上传用户id
            data_time：上传时间
            [1(数据id), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())(上传时间), '普通用户/管理员'(上传用户), './../Data/programs'(文件相对路径)]
            数据id由数据库生成，所以先将上传记录存到数据库，让后再查询得到该条记录(=info)
            '''
            # info 查询flag = 0 的数据 ,是一个列表，将它放到一个大的列表中，格式如下，不然跑不了
            # info = [[4, data_time, '管理员', rela_path]]
            # 重新查询
            data = session.query(Data).order_by(Data.id.desc()).first()
            session.close()
            if data.upload_user_id == 0:
                info = [[data.id, data.upload_time, '普通用户', data.data_path]]
            else:
                info = [[data.id, data.upload_time, '管理员', data.data_path]]

            self.showTable(info)

    # def onClicked(self, user):
    #     radioBtn = self.sender()
    #     if radioBtn.isChecked():
    #         self.data_path = user[3]
    def onClicked(self, id):
        radioBtn = self.sender()
        if radioBtn.isChecked():
            self.id = id
            # print(self.id)
            session = SessionClass()
            data = session.query(Data).filter(Data.id == self.id).first()
            session.close()
            # self.data_path = 根据id去数据库获取这条记录的存储路径，赋值给self.data_path
            self.data_path = data.data_path
            # print(self.data_path)

    def showBottom(self):
        # bottom
        data_time_now = datetime.now().replace(microsecond=0, second=0)  # 获取到当前时间
        result_time_content = datetime(2022, 11, 24, 10, 43, 48)
        no_second_result_time = result_time_content.replace(second=0)
        time_span = (data_time_now - no_second_result_time)
        time_span_current = str(time_span.days) + '天' + str(int(time_span.seconds / 3600)) + '时' + str(
            int((time_span.seconds % 3600) / 60)) + '分之前'
        self.evaluate_time.setText('评估时间: ' + str(result_time_content))
        self.pass_time.setText(str(time_span_current))

    # def showTable(self, data_list):
    #     font = QFont()
    #     font.setFamily('Microsoft YaHei')
    #     if data_list is None:
    #         return
    #     current_row_count = self.table_widget.rowCount()  # 当前表格有多少行
    #     for data in data_list:
    #         self.table_widget.insertRow(current_row_count)
    #         for j in range(0, self.table_widget.columnCount() + 1):
    #             if j == 0:
    #                 choose_data = QRadioButton()
    #                 self.table_widget.setCellWidget(current_row_count, j, choose_data)
    #                 if current_row_count == 0:  # 前面的数据选择单选框
    #                     choose_data.setChecked(True)
    #                     self.data_path = data[3]
    #                 choose_data.toggled.connect(partial(self.onClicked, data))
    #             elif j == 1:  # 数据id
    #                 item = QTableWidgetItem(str(data[0]))
    #                 item.setFont(font)
    #                 self.table_widget.setItem(current_row_count, j, item)
    #             elif j == 2:  # 文件路径
    #                 item = QTableWidgetItem(data[3].split('/')[-1])
    #                 item.setFont(font)
    #                 self.table_widget.setItem(current_row_count, j, item)
    #             elif j == 3:  # 上传时间
    #                 item = QTableWidgetItem(str(data[1]))
    #                 item.setFont(font)
    #                 self.table_widget.setItem(current_row_count, j, item)
    #             elif j == 4:  # 上传用户
    #                 item = QTableWidgetItem(data[2])
    #                 item.setFont(font)
    #                 self.table_widget.setItem(current_row_count, j, item)
    #             else:  # 操作按钮
    #                 self.table_widget.setCellWidget(current_row_count, j, self.buttonForRow())
    #                 self.train_btn.clicked.connect(partial(self.trainModel, data))
    #                 self.test_btn.clicked.connect(partial(self.testModel, data))
    #                 self.delete_btn.clicked.connect(self.deleteButton, )
    #         current_row_count += 1

    # def showTable(self, data_list):
    #     font = QFont()
    #     font.setFamily('Microsoft YaHei')
    #     if data_list is None:
    #         return
    #     current_row_count = self.table_widget.rowCount()  # 当前表格有多少行
    #     for data in data_list:
    #         self.table_widget.insertRow(current_row_count)
    #         for j in range(0, self.table_widget.columnCount() + 1):
    #             if j == 0:
    #                 choose_data = QRadioButton()
    #                 self.table_widget.setCellWidget(current_row_count, j, choose_data)
    #                 if current_row_count == 0:  # 前面的数据选择单选框
    #                     pass
    #                     # choose_data.setChecked(True)
    #                     # self.data_path = data[3]
    #                 # data[0] = id
    #                 choose_data.toggled.connect(partial(self.onClicked, data[0]))
    #             elif j == 1:  # 数据id
    #                 item = QTableWidgetItem(str(data[0]))
    #                 item.setFont(font)
    #                 self.table_widget.setItem(current_row_count, j, item)
    #             elif j == 2:  # 文件路径
    #                 item = QTableWidgetItem(data[3].split('/')[-1])
    #                 item.setFont(font)
    #                 self.table_widget.setItem(current_row_count, j, item)
    #             elif j == 3:  # 上传时间
    #                 item = QTableWidgetItem(str(data[1]))
    #                 item.setFont(font)
    #                 self.table_widget.setItem(current_row_count, j, item)
    #             elif j == 4:  # 上传用户
    #                 item = QTableWidgetItem(data[2])
    #                 item.setFont(font)
    #                 self.table_widget.setItem(current_row_count, j, item)
    #             else:  # 操作按钮
    #                 self.table_widget.setCellWidget(current_row_count, j, self.buttonForRow())
    #                 self.train_btn.clicked.connect(partial(self.trainModel, data))
    #                 self.test_btn.clicked.connect(partial(self.testModel, data))
    #                 self.delete_btn.clicked.connect(self.deleteButton)
    #         current_row_count += 1

    def showTable(self, data_list):
        font = QFont()
        font.setFamily('Microsoft YaHei')
        if data_list is None:
            return
        current_row_count = self.table_widget.rowCount()  # 当前表格有多少行
        for data in data_list:
            self.table_widget.insertRow(current_row_count)
            for j in range(0, self.table_widget.columnCount() + 1):
                if j == 0:
                    choose_data = QRadioButton()
                    self.table_widget.setCellWidget(current_row_count, j, choose_data)
                    if current_row_count == 0:  # 前面的数据选择单选框
                        pass
                        # choose_data.setChecked(True)
                        # self.data_path = data[3]
                    # data[0] = id
                    choose_data.toggled.connect(partial(self.onClicked, data[0]))
                elif j == 1:  # 数据id
                    item = QTableWidgetItem(str(data[0]))
                    item.setFont(font)
                    self.table_widget.setItem(current_row_count, j, item)
                elif j == 2:  # 文件路径
                    item = QTableWidgetItem(data[3].split('/')[-1])
                    item.setFont(font)
                    self.table_widget.setItem(current_row_count, j, item)
                elif j == 3:  # 上传时间
                    item = QTableWidgetItem(str(data[1]))
                    item.setFont(font)
                    self.table_widget.setItem(current_row_count, j, item)
                elif j == 4:  # 上传用户
                    item = QTableWidgetItem(data[2])
                    item.setFont(font)
                    self.table_widget.setItem(current_row_count, j, item)
                elif j == 5:  # 训练次数
                    epochs = QComboBox()
                    epochs.addItems(['5', '100', '200'])
                    self.table_widget.setCellWidget(current_row_count, j, epochs)
                else:  # 操作按钮
                    self.table_widget.setCellWidget(current_row_count, j, self.buttonForRow())
                    self.train_btn.clicked.connect(partial(self.trainModel, data))
                    self.test_btn.clicked.connect(partial(self.testModel, data))
                    self.delete_btn.clicked.connect(self.deleteButton)
            current_row_count += 1

    def deleteButton(self):
        button = self.sender()
        if button:
            # 确定位置的时候这里是关键
            row = self.table_widget.indexAt(button.parent().pos()).row()
            id = self.table_widget.item(row, 1).text()  # 获取当前行数据的ID值
            # 根据id,从tb_data中获取数据路径path
            #                 path =
            session = SessionClass()
            data = session.query(Data).filter(Data.id == id).first()
            path = data.data_path
            if self.data_path == path:  # 删除的数据为当前查看的数据
                box = QMessageBox(QMessageBox.Information, "提示", "数据使用中,请勿删除该数据！！！")
                yes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
                box.exec_()
                if box.clickedButton() == yes:
                    return
            box = QMessageBox(QMessageBox.Information, "提示", "确定删除该数据？？？")
            no = box.addButton(self.tr("取消"), QMessageBox.NoRole)
            yes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
            box.exec_()
            if box.clickedButton() == yes:
                if os.path.exists(path):
                    shutil.rmtree(path)  # 根据数据路径删除'../data/'下对应的文件
                    session.query(Data).filter(Data.id == id).delete()
                    session.commit()
                    session.close()
                    self.table_widget.removeRow(row)  # 根据row删除table中的记录
                else:
                    return
        else:
            return

    def buttonForRow(self):
        widget = QWidget()
        self.train_btn = QPushButton('训练')
        self.train_btn.setStyleSheet(''' text-align : center;
                                              background-color : NavajoWhite;
                                              height : 30px;
                                              width :40px;
                                              border-style: outset;
                                              font : 13px 'Microsoft YaHei' ''')

        self.test_btn = QPushButton('测试')
        self.test_btn.setStyleSheet(''' text-align : center;
                                        background-color : LightCoral;
                                        height : 30px;
                                        width :40px;
                                        border-style: outset;
                                        font : 13px 'Microsoft YaHei'; ''')
        self.delete_btn = QPushButton('删除')
        self.delete_btn.setStyleSheet(''' text-align : center;
                                                      background-color : NavajoWhite;
                                                      height : 30px;
                                                      width :40px;
                                                      border-style: outset;
                                                      font : 13px 'Microsoft YaHei' ''')

        hLayout = QHBoxLayout()
        hLayout.addWidget(self.train_btn)
        hLayout.addWidget(self.test_btn)
        hLayout.addWidget(self.delete_btn)
        hLayout.setContentsMargins(5, 2, 5, 2)
        widget.setLayout(hLayout)
        return widget

    # def trainModel(self, data):
    #     if self.data_path != data[3]:
    #         box = QMessageBox(QMessageBox.Information, "提示", "请选择对应数据进行测试或训练")
    #         qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
    #         box.exec_()
    #         if box.clickedButton() == qyes:
    #             return
    #     else:
    #         if os.path.exists('../result/status/status.txt'):
    #             box = QMessageBox(QMessageBox.Information, "提示", "已有模型正在运行中，请稍候！！！")
    #             qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
    #             box.exec_()
    #             if box.clickedButton() == qyes:
    #                 return
    #         else:
    #             self.progressBar.setVisible(True)
    #             self.run_info.setText('模型运行中:')
    #             box = QMessageBox(QMessageBox.Information, "提示", "模型正在训练中，请稍等！！！")
    #             qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
    #             box.exec_()
    #             if box.clickedButton() == qyes:
    #                 try:
    #                     if os.path.exists(self.data_path):
    #                         self.train_start_time = datetime.now().replace(microsecond=0, second=0)  # 获取到当前时间
    #                         print(self.data_path)
    #                         print(self.train_start_time)
    #                         self.train_thread = TrainModel(self.data_path)
    #                         self.train_thread._rule.connect(self.waitTrainRes)
    #                         self.train_thread.start()
    #                         self.timer.start(1000, self)
    #                     else:
    #                         return
    #                 except:
    #                     if os.path.exists('../result/status/status.txt'):
    #                         os.remove('../result/status/status.txt')
    #                         self.timer.stop()

    def trainModel(self, data):
        button = self.sender()
        if button:

            if self.data_path != data[3]:
                box = QMessageBox(QMessageBox.Information, "提示", "请选择对应数据进行测试或训练")
                qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
                box.exec_()
                if box.clickedButton() == qyes:
                    return
            else:
                row = self.table_widget.indexAt(button.parent().pos()).row()
                self.trainEpochs = int(self.table_widget.cellWidget(row, 5).currentText())  # 获取当前行数据的ID值
                dataId = data[0]
                session = SessionClass()
                data = session.query(Train).filter(dataId == Train.data_id).first()
                session.close()
                # 根据数据id查询train表 判断是否存在记录,存在记录证明已经用该批数据训练过，训练过了提示以使用数据训练，跳过下面的训练代码
                # 没有记录就执行训练代码
                if data is not None:
                    box = QMessageBox(QMessageBox.Information, "提示", "这批数据已进行训练，请勿重复使用！！！")
                    yes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
                    box.exec_()
                    if box.clickedButton() == yes:
                        return
                else:
                    if os.path.exists('../result/status/status.txt'):
                        box = QMessageBox(QMessageBox.Information, "提示", "已有模型正在运行中，请稍候！！！")
                        qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
                        box.exec_()
                        if box.clickedButton() == qyes:
                            return
                    else:
                        self.progressBar.setVisible(True)
                        self.run_info.setText('模型运行中:')
                        box = QMessageBox(QMessageBox.Information, "提示", "模型正在训练中，请稍等！！！")
                        qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
                        box.exec_()
                        if box.clickedButton() == qyes:
                            try:
                                if os.path.exists(self.data_path):
                                    self.train_start_time = datetime.now().replace(microsecond=0, second=0)  # 获取到当前时间
                                    print(self.train_start_time)
                                    self.train_thread = TrainModel(self.data_path, self.trainEpochs)
                                    self.train_thread._rule.connect(self.waitTrainRes)
                                    self.train_thread.start()
                                    self.timer.start(1000, self)
                                else:
                                    return
                            except:
                                if os.path.exists('../result/status/status.txt'):
                                    os.remove('../result/status/status.txt')
                                    self.timer.stop()

    def waitTrainRes(self):
        self.step = 100
        self.train_end_time = datetime.now().replace(microsecond=0, second=0)  # 获取到当前时间
        print(self.train_end_time)
        finish_box = QMessageBox(QMessageBox.Information, "提示", "模型训练完成")
        yes = finish_box.addButton(self.tr("确定"), QMessageBox.YesRole)
        finish_box.exec_()
        if finish_box.clickedButton() == yes:
            self.progressBar.setVisible(False)
            self.run_info.clear()
            self.progressBar.setValue(0)
            self.step = 0
            if os.path.exists('../result/status/status.txt'):
                with open('../result/status/status.txt', mode='r', encoding='utf-8') as f:
                    contents = f.readlines()
                    # start_time = contents[0].strip('\n')
                    # end_time = contents[1].strip('\n')
                    model_save_path = contents[2].strip('\n')
                    model_name = model_save_path.split('/')[-1]
                    f.close()
                    os.remove('../result/status/status.txt')
                    self.final_result.append(self.train_start_time)
                    self.final_result.append(self.train_end_time)
                    self.final_result.append(model_save_path)  # todo 将模型训练时间和结束时间以及生成的模型路径存储到数据库
                    session = SessionClass()
                    kk = session.query(Train).all()
                    # 如果数据库为空，说明没有模型，那么第一个模型的use=1，后续新的模型use默认为0，可在管理页面切换
                    if len(kk) == 0:
                        data = Train(model_name=model_name, test_time=self.train_start_time, model_path=model_save_path,
                                     epoch=self.trainEpochs, data_id=self.id, use=1)
                    else:
                        data = Train(model_name=model_name, test_time=self.train_start_time, model_path=model_save_path,
                                     epoch=self.trainEpochs, data_id=self.id)
                    session.add(data)
                    session.commit()
                    session.close()

    def testModel(self, data):
        if self.data_path != data[3]:
            box = QMessageBox(QMessageBox.Information, "提示", "请选择对应数据进行测试或训练")
            qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
            box.exec_()
            if box.clickedButton() == qyes:
                return
        else:
            if os.path.exists('../result/status/status.txt'):
                box = QMessageBox(QMessageBox.Information, "提示", "已有模型正在运行中，请稍候！！！")
                qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
                box.exec_()
                if box.clickedButton() == qyes:
                    return
            else:
                self.progressBar.setVisible(True)
                self.run_info.setText('模型运行中:')
                box = QMessageBox(QMessageBox.Information, "提示", "模型正在测试中，请稍等！！！")
                qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
                box.exec_()
                session = SessionClass()
                # 如果有相同的，就插入最新的
                data = session.query(Train).filter(Train.use == 1).first()
                self.model_path = data.model_path
                session.commit()
                session.close()
                if box.clickedButton() == qyes:
                    pass
                try:
                    print(self.data_path)
                    print(self.model_path)
                    if os.path.exists(self.data_path) and os.path.exists(self.model_path):
                        self.test_thread = TestModel(self.data_path, self.model_path)
                        self.test_thread._rule.connect(self.waitTestRes)
                        self.test_thread.start()
                        self.timer.start(500, self)
                    else:
                        return
                except:
                    if os.path.exists('../result/status/status.txt'):
                        os.remove('../result/status/status.txt')
                        self.timer.stop()

    def waitTestRes(self):
        self.step = 100
        finish_box = QMessageBox(QMessageBox.Information, "提示", "模型测试完成。")
        qyes = finish_box.addButton(self.tr("确定"), QMessageBox.YesRole)
        finish_box.exec_()
        if finish_box.clickedButton() == qyes:
            self.progressBar.setVisible(False)
            self.run_info.clear()
            self.progressBar.setValue(0)
            self.step = 0
            if os.path.exists('../result/status/status.txt'):
                with open('../result/status/status.txt', mode='r', encoding='utf-8') as f:
                    contents = f.readlines()
                    self.testAcc = contents[2].strip('\n')
                    show_result = float(contents[2].strip('\n')) * 100
                    f.close()
                    os.remove('../result/status/status.txt')
                    show_result = '{:.2f}'.format(show_result)
                    self.test_acc.setText(show_result + '%')
                    session = SessionClass()
                    # 如果有相同的，就插入最新的
                    data = session.query(Train).filter(Train.data_id == self.id).first()
                    data.test_acc = self.testAcc
                    session.commit()
                    session.close()
                    # todo 匹配到测试对应的模型，将测试集准确率存入数据库

    # def valModel(self):
    #     if os.path.exists('../result/status/status.txt'):
    #         box = QMessageBox(QMessageBox.Information, "提示", "已有模型正在运行中，请稍候！！！")
    #         qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
    #         box.exec_()
    #         if box.clickedButton() == qyes:
    #             return
    #     else:
    #         self.progressBar.setVisible(True)
    #         self.run_info.setText('模型运行中:')
    #         box = QMessageBox(QMessageBox.Information, "提示", "模型正在训练中，请稍等！！！")
    #         qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
    #         box.exec_()
    #         if box.clickedButton() == qyes:
    #             pass
    #         self.cross_val_result.clear()
    #         result_list = []
    #         self.lr = float(self.lrText.currentText())
    #         self.epochs = int(self.epochsText.currentText())
    #         num_cross_val = self.num_cross_val.currentText()
    #         self.val_num = int(num_cross_val)
    #         for i in range(1, self.val_num + 1):
    #             result = '第' + str(i) + '次交叉验证结果'
    #             result_list.append(result)
    #         self.cross_val_result.addItems(result_list)
    #         try:
    #             if os.path.exists(self.data_path):
    #                 self.val_thread = ValModel(self.data_path, self.val_num, self.lr, self.epochs)
    #                 self.val_thread._rule.connect(self.waitValRes)
    #                 self.val_thread.start()
    #                 self.timer.start(2000, self)
    #             else:
    #                 return
    #         except:
    #             if os.path.exists('../result/status/status.txt'):
    #                 os.remove('../result/status/status.txt')
    #                 self.timer.stop()
    def valModel(self):
        if os.path.exists('../result/status/status.txt'):
            box = QMessageBox(QMessageBox.Information, "提示", "已有模型正在运行中，请稍候！！！")
            qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
            box.exec_()
            if box.clickedButton() == qyes:
                return
        else:

            dataId = self.id
            # 根据数据id查询train表 判断是否存在记录,
            # 这下面就是训练过了
            session = SessionClass()
            data = session.query(Train).filter(Train.data_id == dataId).first()
            session.close()
            if data is not None:
                self.progressBar.setVisible(True)
                self.run_info.setText('模型运行中:')
                box = QMessageBox(QMessageBox.Information, "提示", "模型正在训练中，请稍等！！！")
                qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
                box.exec_()
                if box.clickedButton() == qyes:
                    pass
                self.cross_val_result.clear()
                result_list = []
                self.lr = float(self.lrText.currentText())
                self.epochs = int(self.epochsText.currentText())
                num_cross_val = self.num_cross_val.currentText()
                self.val_num = int(num_cross_val)
                for i in range(1, self.val_num + 1):
                    result = '第' + str(i) + '次交叉验证结果'
                    result_list.append(result)
                self.cross_val_result.addItems(result_list)
                try:
                    if os.path.exists(self.data_path):
                        self.val_thread = ValModel(self.data_path, self.val_num, self.lr, self.epochs)
                        self.val_thread._rule.connect(self.waitValRes)
                        self.val_thread.start()
                        self.timer.start(2000, self)
                    else:
                        return
                except:
                    if os.path.exists('../result/status/status.txt'):
                        os.remove('../result/status/status.txt')
                        self.timer.stop()
            else:

                box = QMessageBox(QMessageBox.Information, "提示", "请先进行模型训练！！！")
                yes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
                box.exec_()
                if box.clickedButton() == yes:
                    return

    def waitValRes(self):
        self.step = 100
        finish_box = QMessageBox(QMessageBox.Information, "提示", "模型训练完成。")
        yes = finish_box.addButton(self.tr("确定"), QMessageBox.YesRole)
        finish_box.exec_()
        img_path = []
        if finish_box.clickedButton() == yes:
            self.progressBar.setVisible(False)
            self.run_info.clear()
            self.progressBar.setValue(0)
            self.step = 0
            if os.path.exists('../result/status/status.txt'):
                with open('../result/status/status.txt', mode='r', encoding='utf-8') as f:
                    contents = f.readlines()
                    save_folder = contents[0].strip('\n')
                    show_result = float(contents[1].strip('\n')) * 100
                    show_result = '{:.2f}'.format(show_result)
                    f.close()
                    os.remove('../result/status/status.txt')
                    img_dir = os.listdir(save_folder)
                    for ele in img_dir:
                        img = os.path.join(save_folder, ele)
                        img_path.append(img)
                    self.cross_val_acc.setText(show_result + '%')
                    if self.cross_val_result.currentIndex() == 0:
                        result_img = img_path[0]
                        frame = QImage(result_img)
                        pix = QPixmap.fromImage(frame)
                        item = QGraphicsPixmapItem(pix)
                        scene = QGraphicsScene()
                        scene.addItem(item)
                        self.result_img.setScene(scene)
                        self.result_img.fitInView(QGraphicsPixmapItem(QPixmap(pix)))
                        # self.result_img.setPixmap(self.img)
                    self.cross_val_result.currentIndexChanged.connect(partial(self.showImg, img_path, ))
                    print(show_result)
                    session = SessionClass()
                    data = session.query(Train).filter(Train.data_id == self.id).first()
                    data.lr = self.lr
                    data.epoch = self.epochs
                    data.cross_validation = self.val_num
                    data.result_img_path = save_folder
                    data.cv_acc = float(show_result) / 100.00
                    session.commit()
                    session.close()
                    # todo 将self.lr，self.epochs，self.val_num,save_folder(交叉验证生成对应的图片存储的文件夹),show_result(交叉验证平均准确率)与模型训练对应，存入数据库

    def showImg(self, img_path_list):
        currentIndex = self.cross_val_result.currentIndex()
        for ele in img_path_list:
            img = ele.split(os.sep)[-1]
            if str(currentIndex) == img[0]:
                frame = QImage(ele)
                self.img = QPixmap.fromImage(frame)
                item = QGraphicsPixmapItem(self.img)
                scene = QGraphicsScene()
                scene.addItem(item)
                self.result_img.setScene(scene)
                self.result_img.fitInView(QGraphicsPixmapItem(QPixmap(self.img)))
            else:
                continue

    def timerEvent(self, e):
        if self.step < 99:
            self.step += 1
            self.progressBar.setValue(self.step)
        elif self.step == 100:
            self.timer.stop()
            self.progressBar.setValue(self.step)

    def closeEvent(self, event):
        if os.path.exists('../result/status/status.txt'):
            box = QMessageBox(QMessageBox.Information, "提示", "系统模型正在运行中，确定是否退出？？？")
            no = box.addButton(self.tr("取消"), QMessageBox.NoRole)
            yes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
            box.exec_()
            if box.clickedButton() == yes:
                os.remove('../result/status/status.txt')
                event.accept()
            else:
                event.ignore()


def copyDir(dir_path):
    if dir_path:
        save_path = '../trainData/'
        final_save_path = save_path + time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        with open('../result/status/uploadData.txt', mode='w', encoding='utf-8') as f:
            f.write(final_save_path)
            f.close()
        source_path = os.path.abspath(dir_path)
        if not os.path.exists(final_save_path):
            os.makedirs(final_save_path)
        if os.path.exists(source_path):
            # root 所指的是当前正在遍历的这个文件夹的本身的地址
            # dirs 是一个 list，内容是该文件夹中所有的目录的名字(不包括子目录)
            # files 同样是 list, 内容是该文件夹中所有的文件(不包括子目录)
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    src_file = os.path.join(root, file)
                    shutil.copy(src_file, final_save_path)


class upLoadData(QThread):
    _rule = pyqtSignal(str)

    def __init__(self, dir_path):
        self.dir_path = dir_path
        super(upLoadData, self).__init__()

    def run(self):
        copyDir(self.dir_path)
        self._rule.emit('success')


class TestModel(QThread):
    _rule = pyqtSignal(str)

    def __init__(self, data_path, model_path):
        self.data_path = data_path
        self.model_path = model_path
        super(TestModel, self).__init__()

    def run(self):
        modelTest(self.data_path, self.model_path)
        self._rule.emit('success')


class TrainModel(QThread):
    _rule = pyqtSignal(str)

    def __init__(self, data_path, epochs):
        self.data_path = data_path
        self.epochs = epochs
        super(TrainModel, self).__init__()

    def run(self):
        train(self.data_path, self.epochs)
        self._rule.emit('success')


class ValModel(QThread):
    _rule = pyqtSignal(str)

    def __init__(self, data_path, val_num, lr, epochs):
        self.data_path = data_path
        self.val_num = val_num
        self.lr = lr
        self.epochs = epochs
        super(ValModel, self).__init__()

    def run(self):
        kfold_val(self.data_path, self.val_num, self.lr, self.epochs)
        self._rule.emit('success')


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    w = model_train_Controller()
    # w.showMaximized()
    w.show()
    app.exec()
