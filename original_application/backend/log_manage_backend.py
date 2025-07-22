# 文件功能：日志管理界面的后端逻辑
# 该脚本实现了日志管理界面的功能，包括显示日志内容、返回首页等操作

import sys
sys.path.append('../')
import os
from datetime import datetime, timedelta
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QTableWidgetItem, 
    QWidget, QPushButton, QHBoxLayout, QTextEdit, QLabel, QComboBox
)
import state.operate_user as operate_user
# 导入本页面的前端部分
import front.log_manage_UI as log_manage_UI
# 导入跳转页面的后端部分
from backend import admin_index_backend, index_backend
from sql_model.tb_user import User
from util.db_util import SessionClass
import logging
from util.window_manager import WindowManager
import time

from config import (
    USER_STATUS_FILE, 
    CURRENT_USER_FILE, 
    LOG_FILE, 
    MODEL_STATUS_FILE,
    DATA_DIR
)


class UserFilter(logging.Filter):
    """
    自定义日志过滤器，用于添加用户类型信息到日志记录中
    """
    def __init__(self, userType):
        super().__init__()
        self.userType = userType

    def filter(self, record):
        record.userType = self.userType
        return True

class Log_Manage_WindowActions(log_manage_UI.Ui_MainWindow, QMainWindow):
    """
    日志管理窗口的主要类，继承自PyQt5的QMainWindow和前端UI类
    """

    def __init__(self):
        """
        初始化日志管理窗口
        """
        super(log_manage_UI.Ui_MainWindow, self).__init__()
        self.setupUi(self)
        
        # 设置日志显示框的属性
        self.displayBox.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.displayBox.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.displayBox.setLineWrapMode(QTextEdit.NoWrap)
        
        # 创建控制面板
        control_widget = QWidget()
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建日期选择部分
        date_widget = QWidget()
        date_layout = QHBoxLayout()
        date_layout.setContentsMargins(0, 0, 0, 0)
        
        self.date_label = QLabel("日期筛选:")
        self.date_label.setStyleSheet("font-size: 12px; color: #333;")
        
        self.date_combo = QComboBox()
        self.date_combo.addItems(["全部", "今天", "最近3天", "最近7天", "最近30天"])
        self.date_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 3px 10px;
                min-width: 100px;
                font-size: 12px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(resources/down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        self.date_combo.currentIndexChanged.connect(self.filter_logs)
        
        date_layout.addWidget(self.date_label)
        date_layout.addWidget(self.date_combo)
        date_layout.addStretch()  # 添加弹性空间
        date_widget.setLayout(date_layout)
        
        # 创建字体控制部分
        font_control_widget = QWidget()
        font_control_layout = QHBoxLayout()
        font_control_layout.setContentsMargins(0, 0, 0, 0)
        
        self.font_size = 10  # 初始字体大小
        
        # 字体大小显示标签
        self.font_size_label = QLabel(f'字体大小: {self.font_size}')
        self.font_size_label.setStyleSheet("font-size: 12px; color: #333; margin-right: 5px;")
        
        # 减小字体按钮
        self.decrease_font_btn = QPushButton('-')
        self.decrease_font_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 3px;
                padding: 3px 8px;
                font-size: 14px;
                font-weight: bold;
                min-width: 25px;
                max-width: 25px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.decrease_font_btn.clicked.connect(self.decrease_font_size)
        
        # 增大字体按钮
        self.increase_font_btn = QPushButton('+')
        self.increase_font_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 3px;
                padding: 3px 8px;
                font-size: 14px;
                font-weight: bold;
                min-width: 25px;
                max-width: 25px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.increase_font_btn.clicked.connect(self.increase_font_size)
        
        font_control_layout.addWidget(self.font_size_label)
        font_control_layout.addWidget(self.decrease_font_btn)
        font_control_layout.addWidget(self.increase_font_btn)
        font_control_widget.setLayout(font_control_layout)
        
        # 将所有控件添加到主控制布局
        control_layout.addWidget(date_widget)
        control_layout.addWidget(font_control_widget)
        control_widget.setLayout(control_layout)
        
        # 将控制面板添加到主布局
        self.mainVLayout.insertWidget(0, control_widget)
        
        # 设置初始字体
        font = QFont("Consolas", self.font_size)
        self.displayBox.setFont(font)
        
        self.show_log_content()  # 显示日志内容

        # 连接按钮事件
        self.btn_return.clicked.connect(self.return_index)

        # 设置用户类型
        path = USER_STATUS_FILE
        user = operate_user.read(path)
        userType = "Regular user" if user == 0 else "Administrator"

        # 配置日志
        logging.basicConfig(
            filename=LOG_FILE,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(userType)s - %(message)s'
        )
        logger = logging.getLogger()
        logger.addFilter(UserFilter(userType))

        # 初始化窗口管理器
        window_manager = WindowManager()
        window_manager.register_window('log_manage', self)

    def filter_logs(self):
        """根据选择的日期范围筛选日志"""
        try:
            file_path = LOG_FILE
            if not os.path.exists(file_path):
                self.displayBox.setText("Log file not found.")
                return

            # 获取当前时间
            current_time = datetime.now()
            filter_option = self.date_combo.currentText()
            
            # 根据选择确定起始时间
            if filter_option == "今天":
                start_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
            elif filter_option == "最近3天":
                start_time = (current_time - timedelta(days=3)).replace(hour=0, minute=0, second=0, microsecond=0)
            elif filter_option == "最近7天":
                start_time = (current_time - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
            elif filter_option == "最近30天":
                start_time = (current_time - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
            else:  # "全部"
                start_time = None

            # 读取并过滤日志
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as log_file:
                lines = log_file.readlines()
                filtered_lines = []
                
                for line in lines:
                    try:
                        # 解析日志时间
                        log_time_str = line.split(' - ')[0].strip()
                        log_time = datetime.strptime(log_time_str, '%Y-%m-%d %H:%M:%S,%f')
                        
                        # 根据时间过滤
                        if start_time is None or log_time.date() >= start_time.date():
                            filtered_lines.append(line)
                    except (ValueError, IndexError):
                        continue  # 跳过无法解析时间的行

                total_lines = len(filtered_lines)
                # 只显示最后1000行
                if total_lines > 1000:
                    filtered_lines = filtered_lines[-1000:]
                    self.displayBox.clear()
                    self.displayBox.setTextColor(QColor("blue"))
                    self.displayBox.append(f"注意：共有 {total_lines} 条日志记录，仅显示最新的1000条。\n")
                
                # 清空现有内容（如果之前没有清空的话）
                if total_lines <= 1000:
                    self.displayBox.clear()
                
                # 显示过滤后的内容
                for line in filtered_lines:
                    if "ERROR" in line:
                        self.displayBox.setTextColor(QColor("red"))
                    elif "WARNING" in line:
                        self.displayBox.setTextColor(QColor("orange"))
                    elif "INFO" in line:
                        self.displayBox.setTextColor(QColor("black"))
                    
                    self.displayBox.append(line.strip())
                
                # 滚动到底部
                self.displayBox.verticalScrollBar().setValue(
                    self.displayBox.verticalScrollBar().maximum()
                )
                
        except Exception as e:
            logging.error(f"Error filtering logs: {str(e)}")
            QMessageBox.critical(self, "错误", f"筛选日志时发生错误：{str(e)}")

    def show_log_content(self):
        """显示日志内容"""
        self.filter_logs()  # 使用筛选方法来显示日志

    def increase_font_size(self):
        """增大字体"""
        if self.font_size < 20:  # 设置最大字体大小限制
            self.font_size += 1
            self.update_font()

    def decrease_font_size(self):
        """减小字体"""
        if self.font_size > 8:  # 设置最小字体大小限制
            self.font_size -= 1
            self.update_font()

    def update_font(self):
        """更新字体大小"""
        font = QFont("Consolas", self.font_size)
        self.displayBox.setFont(font)
        self.font_size_label.setText(f'字体大小: {self.font_size}')

    # btn_return返回首页
    def return_index(self):
        """
        返回到相应的主页面
        根据用户类型返回到管理员或普通用户页面
        """
        start_time = time.time()  # 记录开始时间
        
        path = USER_STATUS_FILE
        user_status = operate_user.read(path)
        
        try:
            window_manager = WindowManager()
            # 创建新窗口前先保存引用
            if user_status == '1':  # 管理员
                self._index_window = admin_index_backend.AdminWindowActions()
                window_manager.register_window('admin', self._index_window)
                window_manager.show_window('admin')
            else:  # 普通用户
                self._index_window = index_backend.Index_WindowActions()
                window_manager.register_window('index', self._index_window)
                window_manager.show_window('index')
            
            # 隐藏并关闭当前窗口
            self.hide()
            self.close()
            
            # 记录返回耗时
            end_time = time.time()
            elapsed_ms = int((end_time - start_time) * 1000)  # 转换为毫秒
            logging.info(f"返回首页耗时: {elapsed_ms}毫秒")
            
            logging.info("Returned to index page successfully")
        except Exception as e:
            logging.error(f"Error in return_index: {str(e)}")
            QMessageBox.critical(self, "错误", f"返回主页时发生错误：{str(e)}")



if __name__ == '__main__':
    # 启用高DPI缩放
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 这里是界面的入口，在这里需要定义QApplication对象，之后界面跳转时不用再重新定义，只需要调用show()函数即可
    app = QApplication(sys.argv)
    # 显示创建的界面
    demo_window = Log_Manage_WindowActions()
    window_manager = WindowManager()
    window_manager.register_window('log_manage', demo_window)
    window_manager.show_window('log_manage')
    
    # 进入应用的主事件循环
    sys.exit(app.exec_())
