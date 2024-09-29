from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QFont
from front.component import create_header, create_bottom


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 750)
        MainWindow.setStyleSheet("QMainWindow{background-color:#d4e2f4}")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 垂直方向布局
        self.layout = QtWidgets.QVBoxLayout(self.centralwidget)

        # 返回header组件
        self.header_layout, _, self.btn_return, self.time_show, self.statu_show = create_header('日志管理界面')
        self.layout.addLayout(self.header_layout)

        self.mainVLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.mainVLayout.setObjectName("mainVLayout")
        self.layout.addLayout(self.mainVLayout)

        # 改为显示框 (QTextEdit)
        self.displayBox = QtWidgets.QTextEdit(self.centralwidget)
        self.displayBox.setStyleSheet("background-color:#d4e2f4; color:black; border:1px solid #5c8ac3; margin-right:15px;")
        self.displayBox.setReadOnly(True)
        self.mainVLayout.addWidget(self.displayBox)

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "应激评估系统"))

        font = QFont()
        font.setFamily("Microsoft YaHei")  # 微软雅黑

        # Set initial text for display box
        self.displayBox.setText("This is a display box. You can edit the content.")
