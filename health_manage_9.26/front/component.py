from datetime import datetime

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *


def create_header(title):
    font = QFont()
    font.setFamily('Microsoft YaHei')
    header_layout = QHBoxLayout()  # 水平布局 放title,返回按钮，剩余寿命，当前状态
    not_return_header_layout = QHBoxLayout()  # 水平布局 放title,返回按钮，剩余寿命，当前状态
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
    left_layout = QHBoxLayout()
    left_layout.addWidget(btn_return)
    left_layout.addStretch(2)
    left_layout.addWidget(name)
    right_layout = QHBoxLayout()
    right_layout1 = QHBoxLayout()
    remain_time = QLabel('')
    # remain_time.setStyleSheet("font-size:15px")
    time_show = QTextBrowser()
    font.setPointSize(14)
    remain_time.setFont(font)
    time_show.setFont(font)
    time_show.setFixedHeight(40)
    time_show.setFixedWidth(200)
    time_show.setAlignment(Qt.AlignCenter)  # 让文本框中的文本居中显示
    time_show.setStyleSheet('background-color: white;')
    # time_show.setAlignment(Qt.AlignCenter)
    current_state = QLabel('')
    current_state.setFont(font)
    # current_state.setStyleSheet("font-size:15px")
    statu_show = QLabel()
    right_layout.addStretch()
    right_layout.addWidget(remain_time)
    right_layout.addWidget(time_show)
    right_layout.addWidget(current_state)
    right_layout.addWidget(statu_show)

    header_layout.addLayout(left_layout)
    header_layout.addLayout(right_layout)

    no_label = QLabel()  # 返回按钮
    no_label.setFixedWidth(55)
    no_label.setFixedHeight(58)
    left_layout1 = QHBoxLayout()
    left_layout1.addWidget(no_label)
    left_layout1.addStretch(2)
    left_layout1.addWidget(name)

    right_layout1.addStretch()
    right_layout1.addWidget(remain_time)
    right_layout1.addWidget(time_show)
    right_layout1.addWidget(current_state)
    right_layout1.addWidget(statu_show)
    not_return_header_layout.addLayout(left_layout1)
    not_return_header_layout.addLayout(right_layout1)
    # # not_return_header_layout.addStretch(4)
    # not_return_header_layout.addStretch(1)
    # not_return_header_layout.addWidget(name)

    return header_layout, not_return_header_layout, btn_return, time_show, statu_show

    # return header_layout, btn_return, time_show, statu_show


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
