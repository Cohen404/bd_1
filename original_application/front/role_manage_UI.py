# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox
)

from front.component import create_header, create_bottom

class Ui_MainWindow(object):
    """
    角色管理界面UI类
    
    负责创建和设置角色管理界面的所有UI元素，包括：
    - 角色列表展示
    - 权限分配管理
    """

    def setupUi(self, MainWindow):
        """
        设置角色管理界面UI
        
        参数:
        MainWindow (QMainWindow): 主窗口对象
        """
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 750)
        MainWindow.setStyleSheet("QMainWindow{background-color:#d4e2f4}")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 垂直方向布局
        self.layout = QtWidgets.QVBoxLayout(self.centralwidget)

        # 返回header组件
        self.header_layout, _, self.btn_return, self.time_show, self.statu_show = create_header('角色管理界面')
        self.layout.addLayout(self.header_layout)

        # 主布局
        self.mainVLayout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.mainVLayout)

        # 角色列表表格
        self.lst = ['角色ID', '角色名称', '描述', '操作']
        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setStyleSheet("margin-right:15px")
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(len(self.lst))
        self.tableWidget.setHorizontalHeaderLabels(self.lst)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.tableWidget.resizeColumnsToContents()
        self.mainVLayout.addWidget(self.tableWidget)

        # 权限管理区域
        self.permissionGroupBox = QtWidgets.QGroupBox("权限管理")
        self.permissionGroupBox.setStyleSheet("QGroupBox{font-size: 16px;}")
        self.permissionLayout = QtWidgets.QVBoxLayout()
        self.permissionGroupBox.setLayout(self.permissionLayout)
        
        # 选择角色下拉框
        self.roleSelectLayout = QtWidgets.QHBoxLayout()
        self.roleLabel = QtWidgets.QLabel("选择角色：")
        self.roleLabel.setStyleSheet("font-size: 14px;")
        self.roleComboBox = QtWidgets.QComboBox()
        self.roleComboBox.setStyleSheet("font-size: 14px;")
        self.roleSelectLayout.addWidget(self.roleLabel)
        self.roleSelectLayout.addWidget(self.roleComboBox)
        self.roleSelectLayout.addStretch()
        self.permissionLayout.addLayout(self.roleSelectLayout)

        # 权限复选框区域
        self.checkboxLayout = QtWidgets.QGridLayout()
        self.permissionLayout.addLayout(self.checkboxLayout)
        
        # 保存按钮
        self.saveButton = QtWidgets.QPushButton("保存权限设置")
        self.saveButton.setStyleSheet("""
            QPushButton {
                background-color: #759dcd;
                font-size: 14px;
                border-radius: 5px;
                padding: 5px 15px;
                color: white;
            }
            QPushButton:hover {
                background-color: #5c8ac3;
            }
        """)
        self.permissionLayout.addWidget(self.saveButton)
        
        self.mainVLayout.addWidget(self.permissionGroupBox)

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        """
        重新翻译UI
        
        参数:
        MainWindow (QMainWindow): 主窗口对象
        """
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "长远航作业应激神经系统功能预警评估系统"))
        
        # 设置表格样式
        self.tableWidget.horizontalHeader().setStyleSheet(
            "QHeaderView::section{background-color:#5c8ac3;font-size:11pt;color: black;};")
        self.tableWidget.setStyleSheet("background-color:#d4e2f4; color:black; border:1px solid #5c8ac3") 