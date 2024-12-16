from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import QUrl, Qt

class Ui_HelpWindow(object):
    def setupUi(self, HelpWindow):
        HelpWindow.setObjectName("HelpWindow")
        HelpWindow.resize(800, 600)
        HelpWindow.setStyleSheet("QMainWindow{background-color:#d4e2f4}")
        
        self.centralwidget = QtWidgets.QWidget(HelpWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Create web view for PDF
        self.webView = QWebEngineView(self.centralwidget)
        
        # Enable PDF viewer using QWebEngineSettings directly
        self.webView.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.webView.settings().setAttribute(QWebEngineSettings.PdfViewerEnabled, True)
        
        # Create layout after creating the central widget
        self.layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.webView)
        
        HelpWindow.setCentralWidget(self.centralwidget)
        
        self.retranslateUi(HelpWindow)
        QtCore.QMetaObject.connectSlotsByName(HelpWindow)

    def retranslateUi(self, HelpWindow):
        _translate = QtCore.QCoreApplication.translate
        HelpWindow.setWindowTitle(_translate("HelpWindow", "帮助文档"))