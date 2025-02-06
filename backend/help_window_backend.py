import os
import subprocess
import logging
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import Qt
from front.help_window_UI import Ui_HelpWindow

class HelpWindow(QMainWindow, Ui_HelpWindow):
    def __init__(self):
        super(HelpWindow, self).__init__(None, Qt.Window)
        self.setupUi(self)
        
        # 显示窗口
        self.show()
        
        # Get the absolute path to manual.pdf
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pdf_path = os.path.join(current_dir, 'manual.pdf')
        
        logging.info(f"尝试打开帮助文档: {pdf_path}")
        
        # Check if the PDF file exists
        if not os.path.exists(pdf_path):
            error_msg = f"找不到帮助文档: {pdf_path}"
            logging.error(error_msg)
            QMessageBox.warning(self, "错误", "找不到帮助文档 (manual.pdf)，请确保文件存在于程序根目录。")
            self.close()
            return
            
        try:
            # 在Linux系统中使用xdg-open打开PDF
            subprocess.Popen(['xdg-open', pdf_path])
            logging.info("成功启动PDF查看器")
            # 关闭当前窗口，因为我们使用系统PDF查看器
            self.close()
        except Exception as e:
            error_msg = f"打开帮助文档失败: {str(e)}"
            logging.error(error_msg)
            QMessageBox.critical(self, "错误", f"打开帮助文档失败：{str(e)}\n请确保系统安装了PDF查看器。")
            self.close()