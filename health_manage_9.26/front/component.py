from datetime import datetime

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *


def create_header(title):
    font = QFont()
    font.setFamily('Microsoft YaHei')

    # 创建一个网格布局，用来放置返回按钮和标题
    header_layout = QGridLayout()

    btn_return = QPushButton()  # 返回按钮
    btn_return.setFixedWidth(55)
    btn_return.setFixedHeight(58)
    btn_return.setStyleSheet("QPushButton{border-image: url(./../img/return.png)}")

    name = QLabel()  # 文本框，放title
    name.setText(title)
    name.setAlignment(Qt.AlignCenter)  # 让文本框中的文本居中显示
    name.setFixedHeight(40)
    name.setFixedWidth(200)

    font.setPointSize(22)
    name.setFont(font)

    # 将返回按钮放在第一列的左侧，标题放在中间
    header_layout.addWidget(btn_return, 0, 0, Qt.AlignLeft)  # 左侧返回按钮
    header_layout.addWidget(name, 0, 1, Qt.AlignCenter)  # 居中的标题

    # 使用弹性空隙确保两边元素不会被挤压
    header_layout.setColumnStretch(0, 1)  # 左侧返回按钮所在的列
    header_layout.setColumnStretch(1, 2)  # 中间标题所在的列
    header_layout.setColumnStretch(2, 1)  # 右侧空列，保持平衡

    return header_layout, None, btn_return, None, None




# def return_main(ui_main,ui_current):


def create_bottom():
    bottom_layout = QHBoxLayout()
    # result_time = QTextBrowser()
    evaluate_time = QLabel()
    pass_time = QLabel()
    font = QFont()
    font.setFamily("Microsoft YaHei")
    evaluate_time.setFont(font)
    pass_time.setFont(font)
    # result_time.setFixedHeight(40)
    bottom_layout.addWidget(evaluate_time)
    bottom_layout.addStretch()
    bottom_layout.addWidget(pass_time)
    # bottom样式设计
    evaluate_time.setStyleSheet("QLabel{font-size:30px}"
                                "QLabel{color:black}"
                                "QLabel{padding:0px 0px 2px 4px}")
    pass_time.setStyleSheet("QLabel{font-size:30px}"
                            "QLabel{color:black}"
                            "QLabel{padding:0px 4px 2px 0px}")

    return bottom_layout, evaluate_time, pass_time
