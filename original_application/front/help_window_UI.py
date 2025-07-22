from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt

class Ui_HelpWindow(object):
    def setupUi(self, HelpWindow):
        HelpWindow.setObjectName("HelpWindow")
        HelpWindow.resize(400, 200)
        HelpWindow.setStyleSheet("QMainWindow{background-color:#d4e2f4}")
        
        self.centralwidget = QtWidgets.QWidget(HelpWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Create layout
        self.layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Add a loading label
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setText("正在打开帮助文档...")
        self.layout.addWidget(self.label)
        
        HelpWindow.setCentralWidget(self.centralwidget)
        
        self.retranslateUi(HelpWindow)
        QtCore.QMetaObject.connectSlotsByName(HelpWindow)

    def retranslateUi(self, HelpWindow):
        _translate = QtCore.QCoreApplication.translate
        HelpWindow.setWindowTitle(_translate("HelpWindow", "帮助文档"))