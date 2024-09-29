import sys

from PyQt5.QtWidgets import *
from front.component import create_header, create_bottom


class Ui_model_Control(QWidget):
    def __init__(self):
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
        layout, _, self.return_btn, self.time_show, self.statu_show = create_header('模型管理')
        return layout

    def init_table(self):
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
        footer_layout, self.evaluate_time, self.pass_time = create_bottom()
        return footer_layout


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Ui_model_Control()
    w.show()
    app.exec()
