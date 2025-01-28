import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from backend.init_login_backend import Index_WindowActions

def main():
    # 启用高DPI缩放
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 创建并显示主窗口
    main_window = Index_WindowActions()
    main_window.show()
    
    # 进入应用的主事件循环
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 