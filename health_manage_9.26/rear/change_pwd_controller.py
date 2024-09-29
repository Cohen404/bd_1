# 密码修改控制器

from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from front.change_pwd_UI import Ui_change_pwd
import sys
sys.path.append('../')
from PyQt5.QtWidgets import QApplication, QMessageBox

from rear import index_rear, admin_rear
from sql_model.tb_result import Result
from sql_model.tb_user import User
from state import operate_user
from util.db_util import SessionClass
import logging

class UserFilter(logging.Filter):
    """
    用户类型日志过滤器
    """
    def __init__(self, userType):
        super().__init__()
        self.userType = userType

    def filter(self, record):
        record.userType = self.userType
        return True


class change_pwd_Controller(Ui_change_pwd):
    """
    密码修改控制器类
    
    负责处理密码修改的逻辑
    """
    def __init__(self):
        super(change_pwd_Controller, self).__init__()
        self.show_nav()
        self.change_btn.clicked.connect(self.checkChange)
        self.return_btn.clicked.connect(self.returnIndex)

        # 从文件中读取用户类型并设置userType
        path = '../state/user_status.txt'
        user = operate_user.read(path)  # 0表示普通用户，1表示管理员
        userType = "Regular user" if user == 0 else "Administrator"

        # 配置 logging 模块
        logging.basicConfig(
            filename='../log/log.txt',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(userType)s - %(message)s'
        )

        # 添加过滤器
        logger = logging.getLogger()
        logger.addFilter(UserFilter(userType))

    def show_nav(self):
        """
        显示导航栏
        """
        # header

        session = SessionClass()
        result = session.query(Result).order_by(Result.id.desc()).first()
        session.close()


    # 密码修改
    def checkChange(self):
        """
        检查并执行密码修改
        """
        # 读取当前用户
        with open('../state/current_user.txt', 'r') as f:
            current_user = f.read().strip()

        # 创建数据库会话
        session = SessionClass()
        old_pwd = self.old_pwd.text()
        data = session.query(User).filter(User.name == current_user, User.pwd == old_pwd).first()

        # 检查旧密码是否正确
        if not old_pwd or data is None:
            logging.warning("Password change failed: Incorrect old password.")
            box = QMessageBox(QMessageBox.Information, "提示", "密码错误，请重新输入")
            qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
            box.exec_()
            if box.clickedButton() == qyes:
                self.old_pwd.clear()
            return

        # 检查新密码是否为空
        if not self.new_pwd.text():
            logging.warning("Password change failed: New password not entered.")
            box = QMessageBox(QMessageBox.Information, "提示", "请输入新密码")
            qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
            box.exec_()
            if box.clickedButton() == qyes:
                self.old_pwd.clear()
            return

        # 检查新密码是否与旧密码相同
        if self.new_pwd.text() == old_pwd:
            logging.warning("Password change failed: New password matches old password.")
            box = QMessageBox(QMessageBox.Information, "提示", "新密码与旧密码重复")
            qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
            box.exec_()
            if box.clickedButton() == qyes:
                self.new_pwd.clear()
            return

        # 检查重复输入的密码是否与新密码一致
        if self.re_new_pwd.text() != self.new_pwd.text():
            logging.warning("Password change failed: Re-entered password does not match new password.")
            box = QMessageBox(QMessageBox.Information, "提示", "重复输入的密码与新密码不一致")
            qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
            box.exec_()
            if box.clickedButton() == qyes:
                self.re_new_pwd.clear()
            return

        # 密码修改成功
        logging.info("Password changed successfully for user: %s", current_user)
        box = QMessageBox(QMessageBox.Information, "提示", "密码修改成功")
        qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
        box.exec_()
        if box.clickedButton() == qyes:
            # 更新数据库中的密码
            session.query(User).filter(User.name == current_user).update(
                {'pwd': self.new_pwd.text().encode()})
            session.commit()
            session.close()

    # 返回首页
    def returnIndex(self):
        """
        返回首页
        """
        path = '../state/user_status.txt'
        user = operate_user.read(path)  # 0表示普通用户，1表示管理员

        # 根据用户类型决定返回的首页
        if user == '0':  # 普通用户
            logging.info("User type: Regular user. Returning to user homepage.")
            self.index = index_rear.Index_WindowActions()
        elif user == '1':  # 管理员
            logging.info("User type: Administrator. Returning to admin homepage.")
            self.index = admin_rear.AdminWindowActions()
        else:
            logging.warning("Unknown user type found in user status file.")
            return  # 退出函数，防止程序继续执行

        # 关闭当前窗口并显示新的首页
        self.close()
        self.index.show()


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    w = change_pwd_Controller()
    # w.showMaximized()
    w.show()
    w.setStyleSheet('''QWidget{background-color:rgb(212, 226, 244);}''')
    app.exec()
