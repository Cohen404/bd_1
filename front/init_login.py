# init_login.py
# 初始登录界面的实现
# 提供用户登录入口

import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtCore import Qt

class Ui_MainWindow(object):
    """
    初始登录界面UI类
    """

    def setupUi(self, MainWindow):
        """
        设置初始登录界面UI
        """
        MainWindow.setObjectName("MainWindow")
        MainWindow.setStyleSheet("QMainWindow{background-color:#d4e2f4}")
        MainWindow.resize(1000, 750)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 垂直方向布局
        self.layout = QtWidgets.QVBoxLayout(self.centralwidget)
        
        # 标题
        self.title_label = QLabel("应激评估系统", self.centralwidget)
        self.title_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(24)
        self.title_label.setFont(font)
        self.layout.addWidget(self.title_label)

        # main主体
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")

        # 垂直弹簧
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 0, 1, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem5, 2, 1, 1, 1)

        # 水平弹簧
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 0, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 1, 2, 1, 1)

        # 用户登录按钮
        self.user_login_Button = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.user_login_Button.sizePolicy().hasHeightForWidth())
        self.user_login_Button.setSizePolicy(sizePolicy)
        self.user_login_Button.setObjectName("user_login_Button")
        self.gridLayout.addWidget(self.user_login_Button, 1, 1, 1, 1)

        self.layout.addLayout(self.gridLayout)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        """
        重新翻译UI
        """
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "应激评估系统"))
        self.user_login_Button.setText(_translate("MainWindow", "用户\n登录"))

        # 设置字体和样式
        style_sheet = """
            QLabel {
                color: black;
                font-size: 24px;
                margin: 20px;
            }
            QPushButton {
                color: white;
                background-color: #4379b9;
                border: 2px;
                border-radius: 10px;
                padding: 20px;
                font-size: 30px;
                font-family: "Microsoft YaHei";
            }
            QPushButton:hover {
                background-color: #94b2da;
            }
        """
        
        MainWindow.setStyleSheet(style_sheet)

