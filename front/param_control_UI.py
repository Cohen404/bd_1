import sys
from PyQt5.QtWidgets import *
from front.component import create_header, create_bottom
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Ui_param_Control(QWidget):
    """
    参数控制界面UI类
    
    负责创建和设置参数控制界面的所有UI元素
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
        """
        # 窗体标题和尺寸

        self.setWindowTitle('应激系统')
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
        # param_layout = QHBoxLayout()
        # param_form = QFormLayout()
        # param_form.setLabelAlignment(Qt.AlignRight)
        # sample_freq = QComboBox()
        # sample_freq.setFixedHeight(40)
        # sample_freq.setFixedWidth(120)
        # sample_freq.addItems(['5', '10', '20'])  # todo 换成数据库读取数据
        # electrode_numbers = QComboBox()
        # electrode_numbers.setFixedHeight(40)
        # electrode_numbers.setFixedWidth(120)
        # electrode_numbers.addItems(['5', '10', '20'])
        # choose_time_interval = QCheckBox()
        #
        # data_format = QComboBox()
        # data_format.setFixedWidth(120)
        # data_format.setFixedHeight(40)
        # data_format.addItems(['EEG'])
        # choose_timed_evaluation = QCheckBox()
        # check = QVBoxLayout()
        # check.addStretch(3)
        # check.addWidget(choose_time_interval)
        # check.addStretch(1)
        # check.addWidget(choose_timed_evaluation)
        # check.addStretch(1)
        #
        # param_form.addRow("采样频率:", sample_freq)
        # param_form.addRow("电极数量:", electrode_numbers)
        # param_form.addRow("采集格式:", data_format)
        # param_layout.addStretch()
        # param_layout.addLayout(param_form)
        # param_layout.addLayout(check)
        # param_layout.addStretch()
        # self.save_button = QPushButton('底部按钮')
        # param_layout.addWidget(self.save_button)
        self.param_layout = QHBoxLayout()
        self.param_form = QFormLayout()
        self.param_form.setLabelAlignment(Qt.AlignRight)

        self.eeg_location_label=QLabel("采集位置:")
        self.eeg_location_label.setStyleSheet("font-size: 30px;")
        self.eeg_location = QLineEdit()
        self.eeg_location.setStyleSheet("font-size: 30px; height: 60px; width: 180px;")

        self.sample_freq_label = QLabel("采样频率:")
        self.sample_freq_label.setStyleSheet("font-size: 30px;")
        self.sample_freq = QLineEdit()
        self.sample_freq.setStyleSheet("font-size: 30px; height: 60px; width: 180px;")


        self.electrode_numbers_label = QLabel("电极数量:")
        self.electrode_numbers_label.setStyleSheet("font-size: 30px;")
        self.electrode_numbers =QLineEdit()
        self.electrode_numbers.setStyleSheet("font-size: 30px; height: 60px; width: 180px;")


        self.data_format_label = QLabel("采集格式:")
        self.data_format_label.setStyleSheet("font-size: 30px;")
        self.data_format = QComboBox()
        self.data_format.setStyleSheet("font-size: 30px; height: 60px; width: 180px;")
        self.data_format.addItems(['EEG'])

        self.param_form.addRow(self.eeg_location_label, self.eeg_location)
        self.param_form.addRow(self.sample_freq_label, self.sample_freq)
        self.param_form.addRow(self.electrode_numbers_label, self.electrode_numbers)
        self.param_form.addRow(self.data_format_label, self.data_format)
        self.param_layout.addStretch()
        self.param_layout.addLayout(self.param_form)

        self.param_layout.addStretch()

        self.save_button = QPushButton('保存')
        self.save_button.setStyleSheet("font-size: 20px; height: 60px; width: 180px;color: white;background-color:rgb(0, 120, 215);border-radius: 10px;")
        self.param_layout.addWidget(self.save_button)
        return self.param_layout




if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Ui_param_Control()
    w.show()
    app.exec()
