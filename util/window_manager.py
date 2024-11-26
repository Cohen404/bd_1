from PyQt5.QtWidgets import QWidget, QMainWindow
from PyQt5.QtCore import Qt

class WindowManager:
    """
    窗口管理类，用于管理所有页面的实例
    使用单例模式确保只有一个管理器实例
    """
    _instance = None
    _windows = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WindowManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # 只在第一次创建时初始化
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.current_window = None

    def register_window(self, name: str, window: QMainWindow):
        """
        注册一个窗口实例并设置窗口属性
        """
        # 设置窗口标志：禁用最大化按钮
        window.setFixedSize(1000, 750)  # 固定窗口大小
        window.setWindowFlags(window.windowFlags() & ~Qt.WindowMaximizeButtonHint)  # 移除最大化按钮
        self._windows[name] = window
        
        # 如果是第一个窗口，设置为当前窗口
        if self.current_window is None:
            self.current_window = window

    def get_window(self, name: str) -> QMainWindow:
        """
        获取一个窗口实例，如果不存在则返回None
        """
        return self._windows.get(name)

    def show_window(self, name: str):
        """
        显示指定的窗口，并隐藏当前窗口
        """
        window = self._windows.get(name)
        if window:
            # 隐藏当前窗口
            if self.current_window and self.current_window != window:
                self.current_window.hide()
            
            # 显示新窗口
            window.show()
            self.current_window = window
        else:
            print(f"Window '{name}' not found") 