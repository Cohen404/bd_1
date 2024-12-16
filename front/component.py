from datetime import datetime

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *


# 创建头部组件
def create_header(title, show_help=False):
    """
    创建应用程序的头部组件
    
    参数:
    title (str): 要显示在头部的标题
    show_help (bool): 是否显示帮助按钮，默认为False
    
    返回:
    tuple: 包含头部布局和各个组件的元组
    """
    font = QFont()
    font.setFamily('Microsoft YaHei')

    # 创建一个网格布局，用来放置返回按钮和标题
    header_layout = QGridLayout()

    btn_return = QPushButton("返回")  # 修改返回按钮，添加文字
    btn_return.setFixedWidth(100)  # 调整宽度以适应文字
    btn_return.setFixedHeight(58)
    # 修改返回按钮样式
    btn_return.setStyleSheet("""
        QPushButton {
            color: white;
            background-color: #4379b9;
            border: 2px;
            border-radius: 10px;
            padding: 2px 4px;
            font-size: 20px;
        }
        QPushButton:hover {
            background-color: #94b2da;
        }
    """)
    btn_return.setFont(font)  # 使用相同的字体

    name = QLabel()  # 文本框，放title
    name.setText(title)
    name.setAlignment(Qt.AlignCenter)  # 让文本框中的文本居中显示
    name.setFixedHeight(40)
    name.setFixedWidth(200)

    btn_help = None
    if show_help:
        # 添加帮助按钮
        btn_help = QPushButton("帮助")
        btn_help.setFixedWidth(100)
        btn_help.setFixedHeight(58)
        btn_help.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #4379b9;
                border: 2px;
                border-radius: 10px;
                padding: 2px 4px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #94b2da;
            }
        """)
        btn_help.setFont(font)

    font.setPointSize(22)
    name.setFont(font)

    # 将返回按钮放在第一列的左侧，标题放在中间，帮助按钮放在右侧
    header_layout.addWidget(btn_return, 0, 0, Qt.AlignLeft)  # 左侧返回按钮
    header_layout.addWidget(name, 0, 1, Qt.AlignCenter)  # 居中的标题
    if btn_help:
        header_layout.addWidget(btn_help, 0, 2, Qt.AlignRight)  # 右侧帮助按钮

    # 使用弹性空隙确保两边元素不会被挤压
    header_layout.setColumnStretch(0, 1)  # 左侧返回按钮所在的列
    header_layout.setColumnStretch(1, 2)  # 中间标题所在的列
    header_layout.setColumnStretch(2, 1)  # 右侧帮助按钮所在的列

    return header_layout, None, btn_return, None, btn_help


# 创建底部组件
def create_bottom():
    """
    创建应用程序的底部组件
    
    返回:
    tuple: 包含底部布局和时间显示标签的元组
    """
    bottom_layout = QHBoxLayout()
    evaluate_time = QLabel()
    pass_time = QLabel()
    font = QFont()
    font.setFamily("Microsoft YaHei")
    evaluate_time.setFont(font)
    pass_time.setFont(font)
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