# 密码修改控制器

from datetime import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from front.change_pwd_UI import Ui_change_pwd
import sys
sys.path.append('../')
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit, QPushButton, QLabel

from rear import index_rear, admin_rear
from sql_model.tb_user import User
from state import operate_user
from util.db_util import SessionClass
import logging
from util.window_manager import WindowManager

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

class change_pwd_Controller(QWidget):
    def __init__(self):
        super(change_pwd_Controller, self).__init__()
        self.init_ui()
        # 初始化窗口管理器
        window_manager = WindowManager()
        window_manager.register_window('change_pwd', self)

    def init_ui(self):
        """
        初始化UI界面
        """
        # 设置窗口标题和大小
        self.setWindowTitle('修改密码')
        self.resize(1000, 750)
        self.setStyleSheet('''QWidget{background-color:rgb(212, 226, 244);}''')

        # 创建主布局
        main_layout = QVBoxLayout()

        # 创建顶部布局
        header_layout = QHBoxLayout()
        title_label = QLabel('修改密码')
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        title_label.setAlignment(Qt.AlignCenter)
        self.return_btn = QPushButton('返回')
        self.return_btn.setStyleSheet("""
            QPushButton {
                background-color: #4379b9;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2c5282;
            }
        """)
        header_layout.addWidget(self.return_btn)
        header_layout.addStretch()
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # 创建表单布局
        form_layout = QGridLayout()
        form_layout.setSpacing(20)

        # 创建标签和输入��
        labels = ['原密码:', '新密码:', '确认新密码:']
        self.old_pwd = QLineEdit()
        self.new_pwd = QLineEdit()
        self.confirm_pwd = QLineEdit()
        input_fields = [self.old_pwd, self.new_pwd, self.confirm_pwd]

        # 设置密码框样式
        pwd_style = """
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #4379b9;
            }
        """

        # 添加标签和输入框到表单
        for i, (label, input_field) in enumerate(zip(labels, input_fields)):
            label_widget = QLabel(label)
            label_widget.setStyleSheet("font-size: 16px; color: #333;")
            input_field.setEchoMode(QLineEdit.Password)
            input_field.setStyleSheet(pwd_style)
            input_field.setMinimumWidth(300)
            form_layout.addWidget(label_widget, i, 0, Qt.AlignRight)
            form_layout.addWidget(input_field, i, 1)

        # 创建一个容器来居中表单
        form_container = QHBoxLayout()
        form_container.addStretch()
        form_container.addLayout(form_layout)
        form_container.addStretch()

        # 添加表单到主布局
        main_layout.addStretch()
        main_layout.addLayout(form_container)
        main_layout.addStretch()

        # 创建确认按钮
        self.confirm_btn = QPushButton('确认修改')
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #4379b9;
                color: white;
                border: none;
                padding: 10px 30px;
                border-radius: 5px;
                font-size: 16px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #2c5282;
            }
        """)
        
        # 创建按钮容器来居中按钮
        btn_container = QHBoxLayout()
        btn_container.addStretch()
        btn_container.addWidget(self.confirm_btn)
        btn_container.addStretch()

        # 添加按钮到主布局
        main_layout.addLayout(btn_container)
        main_layout.addStretch()

        # 设置主布局
        self.setLayout(main_layout)

        # 连接按钮事件
        self.return_btn.clicked.connect(self.returnIndex)
        self.confirm_btn.clicked.connect(self.changePwd)

    def changePwd(self):
        """
        修改密码
        """
        # 获取输入
        old_pwd = self.old_pwd.text().strip()
        new_pwd = self.new_pwd.text().strip()
        confirm_pwd = self.confirm_pwd.text().strip()

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
            # 从文件中读取当前用户ID
            with open('../state/current_user.txt', 'r') as f:
                current_user_id = f.read().strip()

            print(f"当前用户ID: {current_user_id}")

            # 验证旧密码
            user = session.query(User).filter(
                User.user_id == current_user_id,
                User.password == old_pwd
            ).first()

            if not user:
                QMessageBox.warning(self, "错误", "旧密码不正确！")
                logging.warning(f"Password change failed for user '{current_user_id}': incorrect old password")
                return

            print(f"验证用户���息: ID={user.user_id}, 用户名={user.username}")

            # 更新密码
            user.password = new_pwd
            user.updated_at = datetime.now()
            session.commit()

            QMessageBox.information(self, "成功", "密码修改成功！")
            logging.info(f"Password changed successfully for user '{user.username}'")

            # 清空输入框
            self.old_pwd.clear()
            self.new_pwd.clear()
            self.confirm_pwd.clear()

        except Exception as e:
            session.rollback()
            print(f"修改密码时出错: {str(e)}")
            logging.error(f"Error changing password: {str(e)}")
            QMessageBox.critical(self, "错误", f"修改密码失败：{str(e)}")
        finally:
            session.close()

    # btn_return返回首页
    def returnIndex(self):
        """
        返回到相应的主页面
        根据用户类型返回到管理员或普通用户页面
        """
        path = '../state/user_status.txt'
        user_status = operate_user.read(path)
        
        try:
            # 创建新窗口前先保存引用
            if user_status == '1':  # 管理员
                self._index_window = admin_rear.AdminWindowActions()
            else:  # 普通用户
                self._index_window = index_rear.Index_WindowActions()
            
            # 先显示新窗口
            self._index_window.show()
            # 再隐藏当前窗口
            self.hide()
            # 最后关闭当前窗口
            self.close()
            
            logging.info("Returned to index page successfully")
        except Exception as e:
            logging.error(f"Error in return_index: {str(e)}")
            QMessageBox.critical(self, "错误", f"返回主页时发生错误：{str(e)}")


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    window = change_pwd_Controller()
    window_manager = WindowManager()
    window_manager.register_window('change_pwd', window)
    window_manager.show_window('change_pwd')
    sys.exit(app.exec_())
