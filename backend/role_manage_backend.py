# 文件功能：角色管理界面的后端逻辑
# 该脚本实现了角色管理界面的功能，包括显示角色列表、编辑角色权限等操作

import os
import sys
import logging
import traceback
sys.path.append('../')
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QTableWidgetItem,
    QWidget, QHBoxLayout, QPushButton, QCheckBox
)
import state.operate_user as operate_user

# 导入本页面的前端部分
import front.role_manage_UI as role_manage_UI

# 导入跳转页面的后端部分
from backend import user_manage_backend
from sql_model.tb_role import Role
from sql_model.tb_permission import Permission
from sql_model.tb_role_permission import RolePermission
from util.db_util import SessionClass
from util.window_manager import WindowManager

from config import (
    USER_STATUS_FILE, 
    LOG_FILE
)

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

class RoleManageWindowActions(role_manage_UI.Ui_MainWindow, QMainWindow):
    """
    角色管理窗口的主要类，继承自PyQt5的QMainWindow和前端UI类
    """
    
    def __init__(self):
        """初始化角色管理窗口"""
        super(role_manage_UI.Ui_MainWindow, self).__init__()
        self.setupUi(self)
        window_manager = WindowManager()
        window_manager.register_window('role_manage', self)
        
        # 初始化数据库会话
        self.session = SessionClass()
        
        # 初始化UI组件
        self.init_ui()
        
        # 绑定事件处理函数
        self.bind_events()
        
        # 加载初始数据
        self.load_roles()
        self.load_permissions()
        
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
        
    def init_ui(self):
        """初始化UI组件"""
        # 设置表格列宽
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeToContents)
        header.setSectionResizeMode(1, header.ResizeToContents)
        header.setSectionResizeMode(2, header.Stretch)
        header.setSectionResizeMode(3, header.ResizeToContents)
        
    def bind_events(self):
        """绑定事件处理函数"""
        self.roleComboBox.currentIndexChanged.connect(self.on_role_selected)
        self.saveButton.clicked.connect(self.save_permissions)
        self.btn_return.clicked.connect(self.return_to_user_manage)
        
    def load_roles(self):
        """加载角色列表数据"""
        try:
            # 清空表格
            self.tableWidget.setRowCount(0)
            
            # 查询所有角色
            roles = self.session.query(Role).all()
            
            # 填充表格
            for row, role in enumerate(roles):
                self.tableWidget.insertRow(row)
                
                # 设置角色信息
                self.tableWidget.setItem(row, 0, QTableWidgetItem(role.role_id))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(role.role_name))
                self.tableWidget.setItem(row, 2, QTableWidgetItem(role.description))
                
                # 添加编辑按钮
                edit_btn = QPushButton("编辑权限")
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #759dcd;
                        color: white;
                        border-radius: 3px;
                        padding: 3px 8px;
                    }
                    QPushButton:hover {
                        background-color: #5c8ac3;
                    }
                """)
                edit_btn.clicked.connect(lambda checked, r=role: self.edit_role_permissions(r))
                self.tableWidget.setCellWidget(row, 3, edit_btn)
                
            # 更新角色下拉框
            self.roleComboBox.clear()
            for role in roles:
                self.roleComboBox.addItem(role.role_name, role.role_id)
                
        except Exception as e:
            error_stack = traceback.format_exc()
            logging.error(f"Error loading roles: {str(e)}\n{error_stack}")
            QMessageBox.critical(self, "错误", f"加载角色列表失败：\n{str(e)}\n\n详细错误：\n{error_stack}")
            
    def load_permissions(self):
        """加载所有权限"""
        try:
            # 清空权限复选框区域
            for i in reversed(range(self.checkboxLayout.count())): 
                self.checkboxLayout.itemAt(i).widget().setParent(None)
                
            # 查询所有权限
            permissions = self.session.query(Permission).all()
            
            # 创建权限复选框
            for i, permission in enumerate(permissions):
                checkbox = QCheckBox(permission.permission_name)
                checkbox.setProperty('permission_id', permission.permission_id)
                checkbox.setStyleSheet("font-size: 14px;")
                self.checkboxLayout.addWidget(checkbox, i // 2, i % 2)
                
        except Exception as e:
            error_stack = traceback.format_exc()
            logging.error(f"Error loading permissions: {str(e)}\n{error_stack}")
            QMessageBox.critical(self, "错误", f"加载权限列表失败：\n{str(e)}\n\n详细错误：\n{error_stack}")
            
    def edit_role_permissions(self, role):
        """
        编辑角色权限
        
        参数:
        role (Role): 要编辑的角色对象
        """
        try:
            # 选中对应的角色
            index = self.roleComboBox.findData(role.role_id)
            if index >= 0:
                self.roleComboBox.setCurrentIndex(index)
        except Exception as e:
            error_stack = traceback.format_exc()
            logging.error(f"Error editing role permissions: {str(e)}\n{error_stack}")
            QMessageBox.critical(self, "错误", f"编辑角色权限失败：\n{str(e)}\n\n详细错误：\n{error_stack}")
            
    def on_role_selected(self):
        """处理角色选择变更事件"""
        try:
            role_id = self.roleComboBox.currentData()
            if not role_id:
                return
                
            # 查询该角色的权限
            role_permissions = self.session.query(RolePermission).filter_by(role_id=role_id).all()
            permission_ids = {rp.permission_id for rp in role_permissions}
            
            # 更新复选框状态
            for i in range(self.checkboxLayout.count()):
                checkbox = self.checkboxLayout.itemAt(i).widget()
                if checkbox:
                    permission_id = checkbox.property('permission_id')
                    checkbox.setChecked(permission_id in permission_ids)
                    
        except Exception as e:
            error_stack = traceback.format_exc()
            logging.error(f"Error loading role permissions: {str(e)}\n{error_stack}")
            QMessageBox.critical(self, "错误", f"加载角色权限失败：\n{str(e)}\n\n详细错误：\n{error_stack}")
                
    def save_permissions(self):
        """保存权限设置"""
        try:
            role_id = self.roleComboBox.currentData()
            if not role_id:
                return
                
            # 删除原有权限
            self.session.query(RolePermission).filter_by(role_id=role_id).delete()
            
            # 添加新的权限
            for i in range(self.checkboxLayout.count()):
                checkbox = self.checkboxLayout.itemAt(i).widget()
                if checkbox and checkbox.isChecked():
                    permission_id = checkbox.property('permission_id')
                    role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
                    self.session.add(role_permission)
                    
            # 提交更改
            self.session.commit()
            logging.info(f"Permissions saved for role {role_id}")
            QMessageBox.information(self, "成功", "权限设置已保存")
            
        except Exception as e:
            self.session.rollback()
            error_stack = traceback.format_exc()
            logging.error(f"Error saving permissions: {str(e)}\n{error_stack}")
            QMessageBox.critical(self, "错误", f"保存失败：\n{str(e)}\n\n详细错误：\n{error_stack}")
            
    def return_to_user_manage(self):
        """返回用户管理界面"""
        try:
            window_manager = WindowManager()
            self._user_manage_window = user_manage_backend.User_Manage_WindowActions()
            window_manager.register_window('user_manage', self._user_manage_window)
            window_manager.show_window('user_manage')
            
            # 隐藏并关闭当前窗口
            self.hide()
            self.close()
            
            logging.info("Returned to user management page")
        except Exception as e:
            error_stack = traceback.format_exc()
            logging.error(f"Error returning to user management: {str(e)}\n{error_stack}")
            QMessageBox.critical(self, "错误", f"返回用户管理界面失败：\n{str(e)}\n\n详细错误：\n{error_stack}")
            
    def closeEvent(self, event):
        """窗口关闭事件"""
        try:
            self.session.close()
            event.accept()
        except Exception as e:
            error_stack = traceback.format_exc()
            logging.error(f"Error closing window: {str(e)}\n{error_stack}")

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    demo_window = RoleManageWindowActions()
    window_manager = WindowManager()
    window_manager.register_window('role_manage', demo_window)
    window_manager.show_window('role_manage')
    sys.exit(app.exec_()) 