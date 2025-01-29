# 文件功能：用户管理界面的后端逻辑
# 该脚本实现了用户管理界面的功能，包括显示用户列表、添加用户、删除用户、修改密码等操作

import os
import sys
import logging
sys.path.append('../')
import time
from datetime import datetime
import hashlib

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QTableWidgetItem,
    QWidget, QHBoxLayout, QPushButton, QDialog, QFormLayout,
    QLineEdit, QComboBox, QDialogButtonBox
)
import state.operate_user as operate_user

# 导入本页面的前端部分
import front.user_manage_UI as user_manage_UI

# 导入跳转页面的后端部分
from backend import index_backend
from backend import admin_index_backend
from backend import role_manage_backend
from sql_model.tb_user import User
from util.db_util import SessionClass
from util.window_manager import WindowManager

from config import (
    USER_STATUS_FILE, 
    CURRENT_USER_FILE, 
    LOG_FILE, 
    MODEL_STATUS_FILE,
    DATA_DIR
)

def hash_password(password):
    """使用SHA256加密密码"""
    return hashlib.sha256(password.encode()).hexdigest()

class UserFilter(logging.Filter):
    """
    自定义日志过滤器，用于添加用户类型信息到日志记录中
    """
    def __init__(self, userType):
        super().__init__()
        self.userType = userType

    def filter(self, record):
        record.userType = self.userType
        return True

class User_Manage_WindowActions(user_manage_UI.Ui_MainWindow, QMainWindow):
    """
    用户管理窗口的主要类，继承自PyQt5的QMainWindow和前端UI类
    """

    def __init__(self):
        """
        初始化用户管理窗口
        """
        super(user_manage_UI.Ui_MainWindow, self).__init__()
        self.setupUi(self)
        window_manager = WindowManager()
        window_manager.register_window('user_manage', self)
        self.show_table()  # 显示用户表格

        # 连接按钮事件
        self.btn_return.clicked.connect(self.return_index)  # 返回首页
        self.addButton.clicked.connect(self.add_user)  # 添加用户
        self.roleManageBtn.clicked.connect(self.open_role_manage)  # 打开角色管理

        # 设置日志
        path = USER_STATUS_FILE
        user = operate_user.read(path)
        userType = "Regular user" if user == 0 else "Administrator"
        
        logging.basicConfig(
            filename=LOG_FILE,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(userType)s - %(message)s'
        )
        
        logger = logging.getLogger()
        logger.addFilter(UserFilter(userType))

    def show_table(self):
        """显示用户表格"""
        session = SessionClass()
        try:
            users = session.query(User).all()
            self.tableWidget.setRowCount(len(users))
            
            for i, user in enumerate(users):
                # 添加用户信息到表格
                self.tableWidget.setItem(i, 0, QTableWidgetItem(str(user.user_id)))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(user.username))
                self.tableWidget.setItem(i, 2, QTableWidgetItem('管理员' if user.user_type == 'admin' else '普通用户'))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(user.email or ''))
                self.tableWidget.setItem(i, 4, QTableWidgetItem(user.phone or ''))
                
                # 添加操作按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(2, 0, 2, 0)  # 减小上下边距
                btn_layout.setSpacing(4)  # 设置按钮之间的间距
                
                edit_btn = QPushButton("编辑")
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #759dcd;
                        border-radius: 4px;
                        padding: 2px;
                        font-family: 'Microsoft YaHei';
                        font-size: 12px;
                        min-width: 50px;
                        min-height: 20px;
                        max-height: 20px;
                    }
                    QPushButton:hover {
                        background-color: #5c8ac3;
                    }
                """)
                edit_btn.clicked.connect(lambda _, uid=user.user_id: self.edit_user(uid))
                
                delete_btn = QPushButton("删除")
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #d9534f;
                        color: white;
                        border-radius: 4px;
                        padding: 2px;
                        font-family: 'Microsoft YaHei';
                        font-size: 12px;
                        min-width: 50px;
                        min-height: 20px;
                        max-height: 20px;
                    }
                    QPushButton:hover {
                        background-color: #c9302c;
                    }
                """)
                delete_btn.clicked.connect(lambda _, uid=user.user_id: self.delete_user(uid))
                
                btn_layout.addWidget(edit_btn)
                btn_layout.addWidget(delete_btn)
                btn_widget.setLayout(btn_layout)
                
                self.tableWidget.setCellWidget(i, 5, btn_widget)
                
        except Exception as e:
            logging.error(f"Error displaying user table: {str(e)}")
            QMessageBox.critical(self, "错误", f"显示用户表格失败：{str(e)}")
        finally:
            session.close()

    def edit_user(self, user_id):
        """编辑用户信息"""
        session = SessionClass()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                logging.warning(f"Attempted to edit non-existent user with ID: {user_id}")
                QMessageBox.warning(self, "警告", "用户不存在！")
                return
                
            dialog = QDialog(self)
            dialog.setWindowTitle("编辑用户信息")
            layout = QFormLayout()
            
            # 创建输入框
            username_edit = QLineEdit(user.username)
            email_edit = QLineEdit(user.email or '')
            phone_edit = QLineEdit(user.phone or '')
            role_combo = QComboBox()
            role_combo.addItems(["普通用户", "管理员"])
            role_combo.setCurrentText("管理员" if user.user_type == "admin" else "普通用户")
            
            # 添加到布局
            layout.addRow("用户名:", username_edit)
            layout.addRow("邮箱:", email_edit)
            layout.addRow("电话:", phone_edit)
            layout.addRow("角色:", role_combo)
            
            # 按钮
            buttons = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addRow(buttons)
            
            dialog.setLayout(layout)
            
            if dialog.exec_() == QDialog.Accepted:
                # 记录原始值用于日志
                old_values = {
                    'username': user.username,
                    'email': user.email,
                    'phone': user.phone,
                    'user_type': user.user_type
                }
                
                # 更新用户信息
                user.username = username_edit.text()
                user.email = email_edit.text() or None
                user.phone = phone_edit.text() or None
                user.user_type = "admin" if role_combo.currentText() == "管理员" else "user"
                
                # 记录变更到日志
                changes = []
                if old_values['username'] != user.username:
                    changes.append(f"username: {old_values['username']} -> {user.username}")
                if old_values['email'] != user.email:
                    changes.append(f"email: {old_values['email']} -> {user.email}")
                if old_values['phone'] != user.phone:
                    changes.append(f"phone: {old_values['phone']} -> {user.phone}")
                if old_values['user_type'] != user.user_type:
                    changes.append(f"role: {old_values['user_type']} -> {user.user_type}")
                
                session.commit()
                self.show_table()
                
                if changes:
                    logging.info(f"User {user_id} updated: {', '.join(changes)}")
                QMessageBox.information(self, "成功", "用户信息更新成功！")
            else:
                logging.info(f"User edit cancelled for user ID: {user_id}")
                
        except Exception as e:
            session.rollback()
            logging.error(f"Error updating user {user_id}: {str(e)}")
            QMessageBox.critical(self, "错误", f"更新用户信息失败：{str(e)}")
        finally:
            session.close()

    def add_user(self):
        """添加新用户"""
        username = self.nameIN.text().strip()
        password = self.pswdIN.text().strip()
        email = self.emailIN.text().strip()
        phone = self.phoneIN.text().strip()
        user_type = 'admin' if self.character_comboBox.currentText() == "管理员" else 'user'

        if not username or not password:
            logging.warning("Attempted to add user with empty username or password")
            QMessageBox.warning(self, "输入错误", "用户名和密码不能为空！")
            return

        # 对密码进行SHA256加密
        hashed_password = hash_password(password)

        session = SessionClass()
        try:
            # 检查用户名是否存在
            if session.query(User).filter(User.username == username).first():
                logging.warning(f"Attempted to add user with existing username: {username}")
                QMessageBox.warning(self, "错误", "用户名已存在！")
                return

            new_user = User(
                user_id=f"user{int(time.time())}",
                username=username,
                password=hashed_password,  # 存储加密后的密码
                email=email or None,
                phone=phone or None,
                user_type=user_type,
                created_at=datetime.now()
            )

            session.add(new_user)
            session.commit()
            
            # 清空输入框
            self.nameIN.clear()
            self.pswdIN.clear()
            self.emailIN.clear()
            self.phoneIN.clear()
            
            self.show_table()
            logging.info(f"New user added: {username} (type: {user_type})")
            QMessageBox.information(self, "成功", "用户添加成功！")
            
        except Exception as e:
            session.rollback()
            logging.error(f"Error adding new user '{username}': {str(e)}")
            QMessageBox.critical(self, "错误", f"添加用户失败：{str(e)}")
        finally:
            session.close()

    def delete_user(self, user_id):
        """删除用户"""
        session = SessionClass()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                logging.warning(f"Attempted to delete non-existent user with ID: {user_id}")
                QMessageBox.warning(self, "警告", "用户不存在！")
                return

            # 显示确认对话框
            reply = QMessageBox.question(
                self, 
                '确认删除', 
                f'确定要删除用户 "{user.username}" 吗？\n此操作不可恢复！',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                session.delete(user)
                session.commit()
                logging.info(f"User deleted successfully: {user.username} (ID: {user_id})")
                QMessageBox.information(self, "成功", "用户删除成功！")
                self.show_table()
            else:
                logging.info(f"User deletion cancelled for: {user.username} (ID: {user_id})")

        except Exception as e:
            session.rollback()
            logging.error(f"Error deleting user {user_id}: {str(e)}")
            QMessageBox.critical(self, "错误", f"删除用户失败：{str(e)}")
        finally:
            session.close()

    def update_password(self, user_id, new_password):
        """
        更新用户密码
        """
        session = SessionClass()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                user.password = new_password
                user.updated_at = datetime.now()
                session.commit()
                logging.info(f"Password updated for user '{user.username}'")
                return True
            return False
        except Exception as e:
            session.rollback()
            logging.error(f"Error updating password: {str(e)}")
            return False
        finally:
            session.close()

    # btn_return返回首页
    def return_index(self):
        """
        返回到相应的主页面
        根据用户类型返回到管理员或普通用户页面
        """
        path = USER_STATUS_FILE
        user_status = operate_user.read(path)
        
        try:
            window_manager = WindowManager()
            # 创建新窗口前先保存引用
            if user_status == '1':  # 管理员
                self._index_window = admin_index_backend.AdminWindowActions()
                window_manager.register_window('admin', self._index_window)
                window_manager.show_window('admin')
            else:  # 普通用户
                self._index_window = index_backend.Index_WindowActions()
                window_manager.register_window('index', self._index_window)
                window_manager.show_window('index')
            
            # 隐藏并关闭当前窗口
            self.hide()
            self.close()
            
            logging.info("Returned to index page successfully")
        except Exception as e:
            logging.error(f"Error in return_index: {str(e)}")
            QMessageBox.critical(self, "错误", f"返回主页时发生错误：{str(e)}")

    def open_role_manage(self):
        """打开角色管理界面"""
        try:
            window_manager = WindowManager()
            self._role_manage_window = role_manage_backend.RoleManageWindowActions()
            window_manager.register_window('role_manage', self._role_manage_window)
            window_manager.show_window('role_manage')
            
            # 隐藏并关闭当前窗口
            self.hide()
            self.close()
            
            logging.info("Role management window opened")
        except Exception as e:
            logging.error(f"Error opening role management window: {str(e)}")
            QMessageBox.critical(self, "错误", f"打开角色管理界面失败：{str(e)}")


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    demo_window = User_Manage_WindowActions()
    window_manager = WindowManager()
    window_manager.register_window('user_manage', demo_window)
    window_manager.show_window('user_manage')
    sys.exit(app.exec_())