# model_control_UI.py
# 模型控制界面的实现
# 包括模型列表和上传功能

import sys
from PyQt5.QtWidgets import *
from front.component import create_header, create_bottom

class Ui_model_Control(QWidget):
    """
    模型控制界面UI类
    
    负责创建和设置模型控制界面的所有UI元素
    """

    def __init__(self):
        """
        初始化模型控制界面
        """
        super().__init__()
        self.pass_time = None
        self.evaluate_time = None
        self.result_time = None
        self.statu_show = None
        self.time_show = None
        self.return_btn = None
        self.table_widget = None
        self.init_ui()

    def init_ui(self):
        """
        初始化UI
        
        功能:
        - 设置窗口基本属性（标题、大小、样式）
        - 创建并设置布局
        - 添加页面头部、主体和底部
        """
        # 窗体标题和尺寸
        self.setStyleSheet('''QWidget{background-color:rgb(212, 226, 244);}''')
        self.setWindowTitle('应激评估系统')
        self.resize(1000, 750)

        # 窗体位置
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)

        # 垂直方向布局
        layout = QVBoxLayout()

        # 1.创建顶部菜单布局
        layout.addLayout(self.init_header())

        # 2.创建中间功能
        layout.addLayout(self.init_table())

        # 3.创建底部时间布局
        layout.addLayout(self.init_footer())

        # 给窗体设置元素的排列方式
        self.setLayout(layout)

    def init_header(self):
        """
        初始化页面头部
        
        返回:
        layout: 头部布局
        """
        layout, _, self.return_btn, self.time_show, self.statu_show = create_header('模型管理')
        return layout

    def init_table(self):
        """
        初始化模型表格
        
        返回:
        table_layout: 表格布局
        """
        table_layout = QHBoxLayout()
        self.table_widget = QTableWidget(0, 5)
        self.table_widget.setStyleSheet(
            "QHeaderView::section{background-color:rgb(212, 226, 244);font:12pt 'Microsoft YaHei';color: black;};")
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # table_header = [
        #     {'text': '模型选择'},
        #     {'text': 'ID', },
        #     {'text': '文件名',},
        #     {'text': '创建时间', },
        #     {'text': '测试集准确率', },
        #     {'text': '交叉验证准确率', },
        #     {'text': '操作', },
        # ]
        table_header=[
          {'text':'模型类别'},
          {'text':'模型路径'},
            {'text':'模型名称'},
          {'text':'创建时间'},
          {'text':'操作'},]
        for idx, info in enumerate(table_header):
            item = QTableWidgetItem()
            item.setText(info['text'])
            self.table_widget.setHorizontalHeaderItem(idx, item)

        table_layout.addWidget(self.table_widget)
        self.upload_btn = QPushButton('上传')
        # 将上传按钮添加到新的布局中
        table_layout.addWidget(self.upload_btn)
        return table_layout

    def init_footer(self):
        """
        初始化页面底部
        
        返回:
        footer_layout: 底部布局
        """
        footer_layout, self.evaluate_time, self.pass_time = create_bottom()
        return footer_layout


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Ui_model_Control()
    w.show()
    app.exec()
