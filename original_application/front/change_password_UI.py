import sys
from PyQt5.QtWidgets import *
from front.component import create_header, create_bottom
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Ui_change_pwd(QWidget):
    """
    密码修改界面的UI类
    """
    def __init__(self):
        """
        初始化Ui_change_pwd类
        """
        super().__init__()
        self.pass_time = None
        self.evaluate_time = None
        self.result_time = None
        self.statu_show = None
        self.time_show = None
        self.tips = None
        self.change_btn = None
        self.re_new_pwd = None
        self.new_pwd = None
        self.old_pwd = None
        self.return_btn = None
        self.init_ui()

    def init_ui(self):
        """
        初始化UI界面
        """
        # 窗体标题和尺寸
        self.setWindowTitle('长远航作业应激神经系统功能预警评估系统')
        self.resize(1000, 750)
        self.setStyleSheet('''QWidget{background-color:rgb(212, 226, 244);}''')

        # 窗体位置
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)

        # 垂直方向布局
        layout = QVBoxLayout()

        # 1.创建顶部菜单布局
        layout.addLayout(self.init_header())

        layout.addStretch(1)
        # 2.创建中间表格布局
        layout.addLayout(self.init_form())
        layout.addStretch(1)
        layout.addLayout(self.init_btn())
        layout.addStretch(2)

        # 3.创建输入提示框布局
        layout.addLayout(self.init_tips())

        # 4.创建底部时间布局
        layout.addLayout(self.init_footer())

        # 给窗体设置元素的排列方式
        self.setLayout(layout)

    def init_header(self):
        """
        初始化头部
        """
        layout, _, self.return_btn, self.time_show, self.statu_show = create_header('长远航作业应激神经系统功能预警评估系统')
        return layout

    def init_form(self):
        """
        初始化表单
        """
        pwd_layout = QVBoxLayout()
        font = QFont()
        font.setFamily('Microsoft YaHei')
        font.setPointSize(12)
        pwd_box = QHBoxLayout()
        pwd_form = QGridLayout()
        pwd_form.setSpacing(30)
        oldPwdLabel = QLabel('旧密码:')
        oldPwdLabel.setFont(font)
        self.old_pwd = QLineEdit()
        self.old_pwd.setEchoMode(QLineEdit.Password)
        newPwdLabel = QLabel('新密码:')
        newPwdLabel.setFont(font)
        self.new_pwd = QLineEdit()
        self.new_pwd.setEchoMode(QLineEdit.Password)
        reNewPwdLabel = QLabel("重新输入新密码:")
        reNewPwdLabel.setFont(font)
        self.re_new_pwd = QLineEdit()
        self.re_new_pwd.setEchoMode(QLineEdit.Password)
        pwd_form.addWidget(oldPwdLabel, 1, 0)
        pwd_form.addWidget(self.old_pwd, 1, 1)
        pwd_form.addWidget(newPwdLabel, 2, 0)
        pwd_form.addWidget(self.new_pwd, 2, 1)
        pwd_form.addWidget(reNewPwdLabel, 3, 0)
        pwd_form.addWidget(self.re_new_pwd, 3, 1)
        pwd_box.addStretch()
        pwd_box.addLayout(pwd_form)
        pwd_box.addStretch()
        pwd_layout.addStretch()
        pwd_layout.addLayout(pwd_box)
        pwd_layout.addStretch()

        return pwd_layout

    def init_btn(self):
        """
        初始化按钮
        """
        btn_layout = QHBoxLayout()
        self.change_btn = QPushButton('确认修改')
        self.change_btn.setStyleSheet("background-color:#00BFFF;font:15pt 'Microsoft YaHei'")
        btn_layout.addWidget(self.change_btn)
        return btn_layout

    def init_tips(self):
        """
        初始化提示信息
        """
        tip = QVBoxLayout()
        self.tips = QLabel()
        tip.addWidget(self.tips)
        return tip

    def init_footer(self):
        """
        初始化底部
        """
        bottom_layout, self.evaluate_time, self.pass_time = create_bottom()
        return bottom_layout

    def resizeEvent(self, evt):
        """
        处理窗口大小变化事件
        
        参数:
        evt (QResizeEvent): 窗口大小变化事件
        """
        w = evt.size().width()
        h = evt.size().height()
        self.old_pwd.setFixedWidth(int(w * 0.3))
        self.old_pwd.setFixedHeight(int(h * 0.07))
        self.new_pwd.setFixedHeight(int(h * 0.07))
        self.re_new_pwd.setFixedHeight(int(h * 0.07))
        self.change_btn.setFixedWidth(int(w * 0.2))
        self.change_btn.setFixedHeight(int(h * 0.11))

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     w = Ui_change_pwd()
#     param = Ui_param_Control()
#     w.show()
#     app.exec()