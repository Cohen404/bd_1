# log_manage.py
# 日志管理界面的实现
# 显示系统日志信息

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QFont
from front.component import create_header, create_bottom


class Ui_MainWindow(object):
    """
    日志管理界面UI类
    
    负责创建和设置日志管理界面的所有UI元素
    """

    def setupUi(self, MainWindow):
        """
        设置日志管理界面UI
        
        参数:
        MainWindow (QMainWindow): 主窗口对象
        
        功能:
        - 设置窗口基本属性（标题、大小、样式）
        - 创建并设置中央窗口部件
        - 设置布局（垂直布局）
        - 添加页面头部
        - 创建并添加日志显示框
        - 设置样式和字体
        """
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
        self.displayBox.setStyleSheet("""
            QTextEdit {
                background-color: #d4e2f4;
                color: black;
                border: 1px solid #5c8ac3;
            }
            QScrollBar:vertical {
                border: none;
                background: #d4e2f4;
                width: 14px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #5c8ac3;
                min-height: 30px;
                border-radius: 7px;
            }
            QScrollBar::add-line:vertical {
                height: 0px;
            }
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        self.displayBox.setReadOnly(True)
        self.mainVLayout.addWidget(self.displayBox)

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        """
        重新翻译UI
        
        参数:
        MainWindow (QMainWindow): 主窗口对象
        
        功能:
        - 设置窗口标题
        - 设置字体
        - 设置日志显示框初始文本
        """
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "长远航作业应激神经系统功能预警评估系统"))

        font = QFont()
        font.setFamily("Microsoft YaHei")  # 微软雅黑

        # Set initial text for display box
        self.displayBox.setText("This is a display box. You can edit the content.")
