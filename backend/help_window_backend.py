import os
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from front.help_window_UI import Ui_HelpWindow

class HelpWindow(QMainWindow, Ui_HelpWindow):
    def __init__(self):
        super(HelpWindow, self).__init__(None, Qt.Window)
        self.setupUi(self)
        
        # Get the absolute path to manual.pdf
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pdf_path = os.path.join(current_dir, 'manual.pdf')
        
        # Check if the PDF file exists
        if not os.path.exists(pdf_path):
            QMessageBox.warning(self, "错误", "找不到帮助文档 (manual.pdf)，请确保文件存在于程序根目录。")
            return
            
        # Convert the file path to URL format and load the PDF
        url = QUrl.fromLocalFile(pdf_path)
        self.webView.load(url)
        
        # Make sure the window stays on top but doesn't block other windows
        self.setWindowModality(Qt.NonModal)
        
        # Set a reasonable size for the help window
        self.resize(800, 600)
        
        # Show the window
        self.show()