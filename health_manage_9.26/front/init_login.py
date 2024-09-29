# init_login.py
# 初始登录界面的实现
# 提供用户登录入口

import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QLabel

from front.component import create_header, create_bottom
from PyQt5.QtCore import Qt

class Ui_MainWindow(object):
    """
    初始登录界面UI类
    
    负责创建和设置初始登录界面的所有UI元素
    """

    def setupUi(self, MainWindow):
        """
        设置初始登录界面UI
        
        参数:
        MainWindow (QMainWindow): 主窗口对象
        
        功能:
        - 设置窗口基本属性（标题、大小、样式）
        - 创建并设置中央窗口部件
        - 设置布局（垂直布局）
        - 添加页面头部
        - 创建并添加用户登录按钮
        - 设置样式和字体
        """
        MainWindow.setObjectName("MainWindow")
        MainWindow.setStyleSheet("QMainWindow{background-color:#d4e2f4}")
        MainWindow.resize(1000, 750)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 垂直方向布局
        self.layout = QtWidgets.QVBoxLayout(self.centralwidget)
        _, self.header_layout, _ ,_,_= create_header('首页')
        self.layout.addLayout(self.header_layout)
        # main主体
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
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

        MainWindow.setCentralWidget(self.centralwidget)
        self.layout.addLayout(self.gridLayout)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        """
        重新翻译UI
        
        参数:
        MainWindow (QMainWindow): 主窗口对象
        
        功能:
        - 设置窗口标题
        - 设置用户登录按钮文本
        - 设置字体
        - 设置按钮样式
        """
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "应激系统"))
        self.user_login_Button.setText(_translate("MainWindow", "用户\n登录"))

        font = QFont()
        font.setFamily("Microsoft YaHei")  # 微软雅黑
        self.user_login_Button.setFont(font)

        # 样式设置
        self.user_login_Button.setStyleSheet("QPushButton{color:white}"
                                             "QPushButton:hover{background-color:#94b2da}"
                                             "QPushButton{background-color:#4379b9}"
                                             "QPushButton{border:2px}"
                                             "QPushButton{border-radius:10px}"
                                             "QPushButton{padding:2px 4px}"
                                             "QPushButton{font-size:30px}")

