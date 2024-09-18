import sys

from IPython.external.qt_for_kernel import QtCore
from PyQt5.QtWidgets import *
from pyqt5_plugins.examplebutton import QtWidgets

from front.component import create_header, create_bottom
from PyQt5.QtGui import *


class Ui_model_train(QWidget):
    def __init__(self):
        super().__init__()
        self.train_graid = None
        self.upload_pushButton = None
        self.pass_time = None
        self.evaluate_time = None
        self.run_info = None
        self.left_layout = None
        self.tip = None
        self.result_time = None
        self.statu_show = None
        self.time_show = None
        self.return_btn = None
        self.tips = None
        self.test_acc = None
        self.cross_val_acc = None
        self.result_img = None
        self.img = None
        self.cross_val_result = None
        self.btn_train = None
        self.epochsText = None
        self.lrText = None
        self.num_cross_val = None
        self.train_form = None
        self.table_widget = None
        self.progressBar = None
        self.init_ui()

    def init_ui(self):
        # 窗体标题和尺寸

        self.setWindowTitle('直线共轭内啮合齿轮泵健康管理系统')
        self.resize(1000, 750)
        self.setStyleSheet('''QWidget{background-color:rgb(212, 226, 244);}''')
        font = QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(20)
        self.setFont(font)

        # 窗体位置
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)

        # 垂直方向布局
        layout = QVBoxLayout()

        # 1.创建顶部菜单布局
        layout.addLayout(self.init_header())

        # 2.创建中间表格布局
        layout.addLayout(self.init_table())

        # 3训练模型布局
        layout.addLayout(self.init_train())

        layout.addLayout(self.init_tips())

        # 4.创建底部时间布局
        layout.addLayout(self.init_footer())

        # 给窗体设置元素的排列方式
        self.setLayout(layout)

    def init_header(self):
        layout, _, self.return_btn, self.time_show, self.statu_show = create_header('模型训练')
        return layout

    def init_table(self):
        table_layout = QHBoxLayout()
        self.table_widget = QTableWidget(0, 6)
        self.table_widget.setStyleSheet(
            "QHeaderView::section{background-color:rgb(212, 226, 244);font:12pt 'Microsoft YaHei';color: black;};")
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.lst = ['数据选择', 'ID', '文件名', '上传时间', '上传用户', '训练次数','操作']
        self.table_widget.setColumnCount(len(self.lst))
        self.table_widget.setHorizontalHeaderLabels(self.lst)
        self.table_widget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)  # 使列表自适应宽度
        self.table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # 设置tablewidget不可编辑
        # self.table_widget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)  # 设置tablewidget不可选中
        self.table_widget.resizeColumnsToContents()  # 设置列宽高按照内容自适应

        self.upload_pushButton = QPushButton()
        self.upload_pushButton.setFixedWidth(80)
        _translate = QtCore.QCoreApplication.translate
        self.upload_pushButton.setText(_translate("MainWindow", "数\n据\n上\n传"))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.upload_pushButton.sizePolicy().hasHeightForWidth())
        self.upload_pushButton.setSizePolicy(sizePolicy)
        self.upload_pushButton.setStyleSheet("margin-top:30px;margin-bottom:30px;margin-left:10px;\n"
                                             "background-color: #759dcd;font-size: 25px;border-radius:20px;font:15pt 'Microsoft YaHei';")
        self.upload_pushButton.setIconSize(QtCore.QSize(20, 20))
        self.upload_pushButton.setCheckable(False)
        self.upload_pushButton.setObjectName("load_pushButton")
        table_layout.addWidget(self.table_widget)
        table_layout.addWidget(self.upload_pushButton)
        return table_layout

    def init_train(self):
        train_layout = QHBoxLayout()
        self.left_layout = QVBoxLayout()
        self.train_graid = QGridLayout()
        self.train_graid.setSpacing(30)
        font = QFont()
        font.setFamily('Microsoft YaHei')
        font.setPointSize(12)
        cross_val_acc_label = QLabel('交叉验证次数:')
        cross_val_acc_label.setFont(font)
        lrLabel = QLabel('学习率:')
        lrLabel.setFont(font)
        epochLabel = QLabel('训练次数:')
        epochLabel.setFont(font)
        self.num_cross_val = QComboBox()
        self.num_cross_val.setFont(font)
        self.num_cross_val.setFixedWidth(200)
        self.num_cross_val.setFixedHeight(60)
        self.lrText = QComboBox()
        self.lrText.setFont(font)
        self.lrText.setFixedWidth(200)
        self.lrText.setFixedHeight(60)

        self.epochsText = QComboBox()
        self.epochsText.setFont(font)
        self.epochsText.setFixedWidth(200)
        self.epochsText.setFixedHeight(60)
        self.run_info = QLabel()
        self.run_info.setFont(font)
        self.progressBar = QProgressBar()
        self.progressBar.setFont(font)
        self.progressBar.setVisible(False)
        self.progressBar.setStyleSheet(
            "border: 2px solid #2196F3;border-radius: 5px;background-color: #E0E0E0;text-align: center;")
        self.progressBar.resize(150, 20)
        self.train_graid.addWidget(cross_val_acc_label, 1, 0)
        self.train_graid.addWidget(self.num_cross_val, 1, 1)
        self.train_graid.addWidget(lrLabel, 2, 0)
        self.train_graid.addWidget(self.lrText, 2, 1)
        self.train_graid.addWidget(epochLabel, 3, 0)
        self.train_graid.addWidget(self.epochsText, 3, 1)
        self.btn_train = QPushButton('训练模型')
        # self.btn_train.setFixedWidth(370)
        self.btn_train.setFixedHeight(80)
        self.btn_train.setStyleSheet("background-color:#00BFFF;font:15pt 'Microsoft YaHei'")
        self.left_layout.addLayout(self.train_graid)
        self.left_layout.addWidget(self.btn_train)
        self.left_layout.addWidget(self.run_info)
        self.left_layout.addWidget(self.progressBar)

        # 创建右侧结果显示
        result_layer = QHBoxLayout()
        show_result_img = QVBoxLayout()
        textFont = QFont()
        textFont.setFamily('Microsoft YaHei')
        textFont.setPointSize(12)
        self.cross_val_result = QComboBox()
        self.cross_val_result.setFont(font)
        self.cross_val_result.setFixedWidth(240)
        self.cross_val_result.setFixedHeight(40)
        self.cross_val_result.addItem('查看交叉验证结果')
        self.result_img = QGraphicsView()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.result_img.sizePolicy().hasHeightForWidth())
        self.result_img.setSizePolicy(sizePolicy)

        show_result_img.addWidget(self.cross_val_result)
        show_result_img.addWidget(self.result_img)

        result_form = QVBoxLayout()
        result_form.setSpacing(10)
        acc_text = QLabel('测试集准确率')
        val_acc_text = QLabel('交叉验证平均准确率')

        acc_text.setFont(font)
        val_acc_text.setFont(font)
        self.test_acc = QTextBrowser()
        font.setPointSize(20)
        self.test_acc.setFont(font)
        self.test_acc.setFixedWidth(200)
        self.test_acc.setFixedHeight(70)
        self.cross_val_acc = QTextBrowser()
        self.cross_val_acc.setFont(font)
        self.cross_val_acc.setFixedWidth(200)
        self.cross_val_acc.setFixedHeight(70)
        result_form.addWidget(acc_text)
        result_form.addWidget(self.test_acc)
        result_form.addWidget(val_acc_text)
        result_form.addWidget(self.cross_val_acc)

        result_layer.addLayout(show_result_img)
        result_layer.addLayout(result_form)
        result_layer.setSpacing(15)
        train_layout.addLayout(self.left_layout)
        # train_layout.addStretch()
        train_layout.addLayout(result_layer)
        return train_layout

    def init_tips(self):
        self.tip = QVBoxLayout()
        return self.tip

    def init_footer(self):
        bottom_layout, self.evaluate_time, self.pass_time = create_bottom()
        return bottom_layout

    def resizeEvent(self, evt):
        w = evt.size().width()
        h = evt.size().height()
        print(w, h)
        # self.num_cross_val.setFixedWidth(int(w * 0.15))
        # self.num_cross_val.setFixedHeight(int(h * 0.07))
        # self.lrText.setFixedHeight(int(h * 0.07))
        # self.epochsText.setFixedHeight(int(h * 0.07))
        # self.cross_val_result.setFixedWidth(int(w * 0.2))
        # self.cross_val_result.setFixedHeight(int(h * 0.07))
        # self.test_acc.setFixedWidth(int(w * 0.15))
        # self.test_acc.setFixedHeight(int(h * 0.07))
        # self.cross_val_acc.setFixedWidth(int(w * 0.15))
        # self.cross_val_acc.setFixedHeight(int(h * 0.07))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Ui_model_train()
    w.show()
    w.setStyleSheet('''QWidget{background-color:#66CCFF;}''')
    app.exec()
