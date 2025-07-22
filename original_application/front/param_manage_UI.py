import sys
from PyQt5.QtWidgets import *
from front.component import create_header, create_bottom
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Ui_param_Control(QWidget):
    """
    参数控制界面UI类
    
    负责创建和设置参数控制界面的所有UI元素，包括：
    - 参数设置
    - 系统备份和恢复
    - 上传服务控制
    """

    def __init__(self):
        """
        初始化参数控制界面
        """
        super().__init__()
        self.statu_show = None
        self.time_show = None
        self.return_btn = None
        self.init_ui()

    def init_ui(self):
        """
        初始化UI
        
        功能:
        - 设置窗口基本属性（标题、大小、样式）
        - 创建并设置布局
        - 添加页面头部和参数设置表单
        - 添加系统备份和恢复功能
        - 添加上传服务控制功能
        """
        # 窗体标题和尺寸
        self.setWindowTitle('长远航作业应激神经系统功能预警评估系统')
        self.setFixedSize(1000, 750)
        self.setStyleSheet('''QWidget{background-color:rgb(212, 226, 244);}''')

        # 窗体位置
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)

        # 垂直方向布局
        layout = QVBoxLayout()

        # 1.创建顶部菜单布局
        layout.addLayout(self.init_header())
        layout.addStretch()

        # 2.创建中间功能
        layout.addLayout(self.init_table())
        layout.addStretch()

        # 3.创建上传服务控制布局
        layout.addLayout(self.init_upload_service_control())
        layout.addStretch()

        # 4.创建备份恢复功能
        layout.addLayout(self.init_backup_restore())
        layout.addStretch()

        # 给窗体设置元素的排列方式
        self.setLayout(layout)

    def init_header(self):
        """
        初始化页面头部
        
        返回:
        layout: 头部布局
        """
        layout, _, self.return_btn, self.time_show, self.statu_show = create_header('参数管理')
        return layout

    def init_table(self):
        """
        初始化参数设置表单
        
        返回:
        param_layout: 参数设置表单布局
        """
        self.param_layout = QHBoxLayout()
        self.param_form = QFormLayout()
        self.param_form.setLabelAlignment(Qt.AlignRight)

        self.sample_freq_label = QLabel("采样频率:")
        self.sample_freq_label.setStyleSheet("font-size: 30px;")
        self.sample_freq = QLineEdit()
        self.sample_freq.setStyleSheet("font-size: 30px; height: 60px; width: 180px;")

        self.electrode_numbers_label = QLabel("电极数量:")
        self.electrode_numbers_label.setStyleSheet("font-size: 30px;")
        self.electrode_numbers = QLineEdit()
        self.electrode_numbers.setStyleSheet("font-size: 30px; height: 60px; width: 180px;")

        self.question_num_label = QLabel("量表问题数量:")
        self.question_num_label.setStyleSheet("font-size: 30px;")
        self.question_num = QLineEdit()
        self.question_num.setStyleSheet("font-size: 30px; height: 60px; width: 180px;")

        self.model_num_label = QLabel("模型数量:")
        self.model_num_label.setStyleSheet("font-size: 30px;")
        self.model_num = QLineEdit()
        self.model_num.setStyleSheet("font-size: 30px; height: 60px; width: 180px;")

        self.param_form.addRow(self.sample_freq_label, self.sample_freq)
        self.param_form.addRow(self.electrode_numbers_label, self.electrode_numbers)
        self.param_form.addRow(self.question_num_label, self.question_num)
        self.param_form.addRow(self.model_num_label, self.model_num)
        
        self.param_layout.addStretch()
        self.param_layout.addLayout(self.param_form)
        self.param_layout.addStretch()

        self.save_button = QPushButton('保存')
        self.save_button.setStyleSheet("font-size: 20px; height: 60px; width: 180px;color: white;background-color:rgb(0, 120, 215);border-radius: 10px;")
        self.param_layout.addWidget(self.save_button)
        
        return self.param_layout

    def init_upload_service_control(self):
        """
        初始化上传服务控制布局
        
        返回:
        upload_service_layout: 上传服务控制布局
        """
        upload_service_layout = QVBoxLayout()
        
        # 创建标题
        title_label = QLabel("上传服务控制")
        title_label.setStyleSheet("font-size: 30px; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        upload_service_layout.addWidget(title_label)
        
        # 创建控制按钮布局
        control_layout = QHBoxLayout()
        
        # 创建开启/关闭按钮
        self.service_toggle_btn = QPushButton('开启服务')
        self.service_toggle_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                height: 60px;
                width: 180px;
                color: white;
                background-color: rgb(0, 120, 215);
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgb(0, 100, 195);
            }
        """)
        control_layout.addWidget(self.service_toggle_btn)
        
        # 创建IP白名单输入框和按钮布局
        ip_layout = QHBoxLayout()
        
        # IP输入框
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("输入IP地址（例如：192.168.1.100）")
        self.ip_input.setStyleSheet("""
            QLineEdit {
                font-size: 20px;
                height: 60px;
                padding: 0 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)
        ip_layout.addWidget(self.ip_input)
        
        # 添加IP按钮
        self.add_ip_btn = QPushButton('添加IP')
        self.add_ip_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                height: 60px;
                width: 120px;
                color: white;
                background-color: rgb(0, 120, 215);
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgb(0, 100, 195);
            }
        """)
        ip_layout.addWidget(self.add_ip_btn)

        # 删除IP按钮
        self.delete_ip_btn = QPushButton('删除IP')
        self.delete_ip_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                height: 60px;
                width: 120px;
                color: white;
                background-color: rgb(215, 0, 0);
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgb(195, 0, 0);
            }
        """)
        ip_layout.addWidget(self.delete_ip_btn)
        
        # 创建IP白名单显示区域
        self.ip_list = QListWidget()
        self.ip_list.setStyleSheet("""
            QListWidget {
                font-size: 18px;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #e0e0e0;
            }
        """)
        self.ip_list.setMaximumHeight(150)
        
        # 添加所有组件到主布局
        upload_service_layout.addLayout(control_layout)
        upload_service_layout.addLayout(ip_layout)
        upload_service_layout.addWidget(self.ip_list)
        
        return upload_service_layout

    def init_backup_restore(self):
        """
        初始化备份和恢复功能布局
        
        返回:
        backup_restore_layout: 备份恢复功能布局
        """
        backup_restore_layout = QHBoxLayout()
        
        # 创建备份按钮
        self.backup_button = QPushButton('系统备份')
        self.backup_button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                height: 60px;
                width: 180px;
                color: white;
                background-color: rgb(0, 120, 215);
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgb(0, 100, 195);
            }
        """)
        
        # 创建恢复按钮
        self.restore_button = QPushButton('系统恢复')
        self.restore_button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                height: 60px;
                width: 180px;
                color: white;
                background-color: rgb(215, 120, 0);
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgb(195, 100, 0);
            }
        """)
        
        backup_restore_layout.addStretch()
        backup_restore_layout.addWidget(self.backup_button)
        backup_restore_layout.addSpacing(20)  # 添加按钮之间的间距
        backup_restore_layout.addWidget(self.restore_button)
        backup_restore_layout.addStretch()
        
        return backup_restore_layout


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Ui_param_Control()
    w.show()
    app.exec()
