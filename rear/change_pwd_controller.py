# 密码修改控制器

from datetime import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from front.change_pwd_UI import Ui_change_pwd
import sys
sys.path.append('../')
from PyQt5.QtWidgets import QApplication, QMessageBox

from rear import index_rear, admin_rear
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
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('修改密码')
        self.setFixedSize(self.width(), self.height())

        # 设置字体
        font = QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(10)
        self.setFont(font)

        # 连接按钮事件
        self.btn_return.clicked.connect(self.returnIndex)
        self.btn_confirm.clicked.connect(self.changePwd)

        # 从文件中读取用户类型并设置userType
        path = '../state/user_status.txt'
        user = operate_user.read(path)
        userType = "Regular user" if user == 0 else "Administrator"

        # 配置日志
        logging.basicConfig(
            filename='../log/log.txt',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(userType)s - %(message)s'
        )
        logger = logging.getLogger()
        logger.addFilter(UserFilter(userType))

    def changePwd(self):
        """
        修改密码
        """
        # 获取输入
        old_pwd = self.old_pwd_lineEdit.text().strip()
        new_pwd = self.new_pwd_lineEdit.text().strip()
        confirm_pwd = self.confirm_pwd_lineEdit.text().strip()

        # 验证输入
        if not all([old_pwd, new_pwd, confirm_pwd]):
            QMessageBox.warning(self, "错误", "所有字段都必须填写！")
            return

        if new_pwd != confirm_pwd:
            QMessageBox.warning(self, "错误", "新密码和确认密码不匹配！")
            return

        if old_pwd == new_pwd:
            QMessageBox.warning(self, "错误", "新密码不能与旧密码相同！")
            return

        session = SessionClass()
        try:
            # 从文件中读取当前用户名
            with open('../state/current_user.txt', 'r') as f:
                current_username = f.read().strip()

            # 验证旧密码
            user = session.query(User).filter(
                User.username == current_username,
                User.password == old_pwd
            ).first()

            if not user:
                QMessageBox.warning(self, "错误", "旧密码不正确！")
                logging.warning(f"Password change failed for user '{current_username}': incorrect old password")
                return

            # 更新密码
            user.password = new_pwd
            user.updated_at = datetime.now()
            session.commit()

            QMessageBox.information(self, "成功", "密码修改成功！")
            logging.info(f"Password changed successfully for user '{current_username}'")

            # 清空输入框
            self.old_pwd_lineEdit.clear()
            self.new_pwd_lineEdit.clear()
            self.confirm_pwd_lineEdit.clear()

        except Exception as e:
            session.rollback()
            logging.error(f"Error changing password: {str(e)}")
            QMessageBox.critical(self, "错误", f"修改密码失败：{str(e)}")
        finally:
            session.close()

    def returnIndex(self):
        """
        返回首页
        """
        path = '../state/user_status.txt'
        user = operate_user.read(path)

        if user == '0':  # 普通用户
            logging.info("Returning to user homepage")
            self.index = index_rear.Index_WindowActions()
        elif user == '1':  # 管理员
            logging.info("Returning to admin homepage")
            self.index = admin_rear.AdminWindowActions()
        else:
            logging.warning("Unknown user type found in user status file")
            return

        self.close()
        self.index.show()

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    window = change_pwd_Controller()
    window.show()
    sys.exit(app.exec_())
