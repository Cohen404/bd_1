# 文件功能：参数控制界面的后端逻辑
# 该脚本实现了参数控制界面的功能，包括参数显示、保存、更新等操作，以及与数据库的交互

import os
import sys
import time
import front.param_manage_UI as Ui_param_Control
from PyQt5 import QtCore
sys.path.append('../')
from datetime import datetime
from functools import partial
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QRadioButton, QTableWidgetItem, QWidget, QPushButton, QHBoxLayout, \
    QMessageBox, QFileDialog, QInputDialog, QProgressDialog, QListWidgetItem
import shutil
import subprocess
import zipfile
import re
import requests
from front.model_manage_UI import Ui_model_Control
from backend import admin_index_backend, index_backend
from state import operate_user
from util.db_util import SessionClass, HOST, PORT, DATABASE, USERNAME, PASSWORD
from sql_model.tb_parameters import Parameters
from sql_model.tb_user import User
from sql_model.system_params import SystemParams
from util.window_manager import WindowManager

import logging
from config import (
    USER_STATUS_FILE, 
    CURRENT_USER_FILE, 
    LOG_FILE, 
    MODEL_STATUS_FILE,
    DATA_DIR
)
import json

# 定义备份目录
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.backup')
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

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

class BackupThread(QThread):
    """
    备份操作线程类
    """
    finished = pyqtSignal(bool, str)  # 完成信号，传递成功/失败状态和消息
    progress_updated = pyqtSignal(int)  # 添加进度信号

    def __init__(self, backup_path):
        super().__init__()
        self.backup_path = backup_path

    def run(self):
        try:
            logging.info("开始系统备份操作")
            
            # 检查pg_dump是否存在
            if not shutil.which('pg_dump'):
                logging.error("未找到pg_dump命令")
                self.finished.emit(False, "未找到pg_dump命令，请确保已安装PostgreSQL客户端工具")
                return
                
            self.progress_updated.emit(10)
            logging.info("开始创建备份文件")
            
            # 创建ZIP文件
            with zipfile.ZipFile(self.backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 1. 备份数据库
                logging.info("开始备份数据库")
                db_backup_path = os.path.join(BACKUP_DIR, 'temp_db_backup.sql')
                
                dump_command = [
                    'pg_dump',
                    f'--host={HOST}',
                    f'--port={PORT}',
                    f'--username={USERNAME}',
                    f'--dbname={DATABASE}',
                    '--format=p',
                    f'--file={db_backup_path}'
                ]
                
                env = os.environ.copy()
                env['PGPASSWORD'] = PASSWORD
                
                try:
                    logging.info(f"执行数据库备份命令: {' '.join(dump_command)}")
                    process = subprocess.run(
                        dump_command,
                        env=env,
                        timeout=60,
                        capture_output=True,
                        text=True
                    )
                    if process.returncode != 0:
                        error_msg = f"数据库备份失败: {process.stderr}"
                        logging.error(error_msg)
                        raise Exception(error_msg)
                    logging.info("数据库备份完成")
                except subprocess.TimeoutExpired:
                    error_msg = "数据库备份超时"
                    logging.error(error_msg)
                    raise Exception(error_msg)
                    
                self.progress_updated.emit(40)
                
                # 添加数据库备份到zip
                logging.info("将数据库备份添加到压缩文件")
                zipf.write(db_backup_path, 'database.sql')
                os.remove(db_backup_path)
                logging.info("删除临时数据库备份文件")
                
                self.progress_updated.emit(60)
                
                # 2. 备份data目录
                data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
                if os.path.exists(data_dir):
                    logging.info(f"开始备份data目录: {data_dir}")
                    for root, dirs, files in os.walk(data_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(data_dir))
                            logging.info(f"备份文件: {arcname}")
                            zipf.write(file_path, arcname)
                else:
                    logging.warning("data目录不存在")

                # 3. 备份model目录
                model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'model')
                if os.path.exists(model_dir):
                    logging.info(f"开始备份model目录: {model_dir}")
                    for root, dirs, files in os.walk(model_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(model_dir))
                            logging.info(f"备份文件: {arcname}")
                            zipf.write(file_path, arcname)
                else:
                    logging.warning("model目录不存在")

            self.progress_updated.emit(100)
            logging.info(f"系统备份完成，备份文件保存在: {self.backup_path}")
            self.finished.emit(True, self.backup_path)
            
        except Exception as e:
            error_msg = f"备份过程发生错误: {str(e)}"
            logging.error(error_msg)
            self.finished.emit(False, error_msg)

class RestoreThread(QThread):
    """
    恢复操作线程类
    """
    finished = pyqtSignal(bool, str)  # 完成信号，传递成功/失败状态和消息

    def __init__(self, backup_file):
        super().__init__()
        self.backup_file = backup_file

    def run(self):
        """
        执行恢复操作
        """
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # 创建临时目录
            temp_dir = os.path.join(BACKUP_DIR, 'temp_restore')
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)

            try:
                # 解压备份文件到临时目录
                with zipfile.ZipFile(self.backup_file, 'r') as zipf:
                    zipf.extractall(temp_dir)

                # 1. 恢复数据库
                db_backup = os.path.join(temp_dir, 'database.sql')
                if os.path.exists(db_backup):
                    # 设置环境变量PGPASSWORD
                    env = os.environ.copy()
                    env['PGPASSWORD'] = PASSWORD

                    # 先删除所有现有连接
                    drop_connections_command = [
                        'psql',
                        f'--host={HOST}',
                        f'--port={PORT}',
                        f'--username={USERNAME}',
                        f'--dbname=postgres',  # 连接到默认数据库
                        '-c', f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{DATABASE}' AND pid <> pg_backend_pid();"
                    ]
                    
                    process = subprocess.Popen(
                        drop_connections_command,
                        env=env,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    process.communicate()

                    # 删除现有数据库
                    drop_db_command = [
                        'dropdb',
                        f'--host={HOST}',
                        f'--port={PORT}',
                        f'--username={USERNAME}',
                        DATABASE
                    ]
                    
                    process = subprocess.Popen(
                        drop_db_command,
                        env=env,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    process.communicate()

                    # 创建新数据库
                    create_db_command = [
                        'createdb',
                        f'--host={HOST}',
                        f'--port={PORT}',
                        f'--username={USERNAME}',
                        DATABASE
                    ]
                    
                    process = subprocess.Popen(
                        create_db_command,
                        env=env,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    process.communicate()

                    # 恢复数据库
                    restore_command = [
                        'psql',
                        f'--host={HOST}',
                        f'--port={PORT}',
                        f'--username={USERNAME}',
                        f'--dbname={DATABASE}',
                        '-f', db_backup
                    ]
                    
                    process = subprocess.Popen(
                        restore_command,
                        env=env,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    _, stderr = process.communicate()
                    
                    if process.returncode != 0:
                        raise Exception(f"数据库恢复失败: {stderr.decode()}")

                # 2. 恢复data目录
                data_backup = os.path.join(temp_dir, 'data')
                if os.path.exists(data_backup):
                    data_dir = os.path.join(base_dir, 'data')
                    if os.path.exists(data_dir):
                        shutil.rmtree(data_dir)
                    shutil.copytree(data_backup, data_dir)

                # 3. 恢复model目录
                model_backup = os.path.join(temp_dir, 'model')
                if os.path.exists(model_backup):
                    model_dir = os.path.join(base_dir, 'model')
                    if os.path.exists(model_dir):
                        shutil.rmtree(model_dir)
                    shutil.copytree(model_backup, model_dir)

                self.finished.emit(True, "")
            finally:
                # 清理临时目录
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)

        except Exception as e:
            self.finished.emit(False, str(e))

class ParamControl(Ui_param_Control.Ui_param_Control, QWidget):
    """
    参数控制界面的主要类，继承自前端UI类和QWidget
    """
    def __init__(self):
        """
        初始化参数控制界面
        """
        super(Ui_param_Control.Ui_param_Control, self).__init__()
        self.init_ui()
        self.SHOWUi()

        self.return_btn.clicked.connect(self.returnIndex)
        self.save_button.clicked.connect(self.savetoDB)
        self.backup_button.clicked.connect(self.backup_system)
        self.restore_button.clicked.connect(self.restore_system)
        
        # 从文件中读取用户类型并设置userType
        path = USER_STATUS_FILE
        user = operate_user.read(path)  # 0表示普通用户，1表示管理员
        userType = "Regular user" if user == 0 else "Administrator"

        # 配置 logging 模块
        logging.basicConfig(
            filename=LOG_FILE,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(userType)s - %(message)s'
        )

        # 添加滤器
        logger = logging.getLogger()
        logger.addFilter(UserFilter(userType))

        # 注册窗口到WindowManager
        window_manager = WindowManager()
        window_manager.register_window('param_control', self)

        self._admin_window = None
        self.upload_service_process = None
        self.ip_whitelist = {'127.0.0.1'}  # 默认包含localhost
        
        # 获取当前用户名
        with open(CURRENT_USER_FILE, 'r') as f:
            self.username = f.read().strip()
        
        # 连接上传服务控制按钮事件
        self.service_toggle_btn.clicked.connect(self.toggle_upload_service)
        self.add_ip_btn.clicked.connect(self.add_ip_to_whitelist)
        self.delete_ip_btn.clicked.connect(self.delete_selected_ip)  # 连接删除按钮事件
        
        # 允许删除IP白名单中的项目
        self.ip_list.itemDoubleClicked.connect(self.remove_ip_from_whitelist)
        
        # 初始化IP白名单显示
        self.refresh_ip_list()
        
        # 显示参数
        self.SHOWUi()

    def is_valid_ip(self, ip):
        """
        验证IP地址格式是否正确
        
        参数:
        ip (str): IP地址
        
        返回:
        bool: IP地址是否有效
        """
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
        
        # 检查每个数字是否在0-255范围内
        parts = ip.split('.')
        return all(0 <= int(part) <= 255 for part in parts)

    def add_ip_to_whitelist(self):
        """添加IP到白名单"""
        ip = self.ip_input.text().strip()
        
        if not ip:
            QMessageBox.warning(self, "警告", "请输入IP地址")
            return
            
        if not self.is_valid_ip(ip):
            QMessageBox.warning(self, "警告", "请输入有效的IP地址")
            return
            
        if ip in self.ip_whitelist:
            QMessageBox.warning(self, "警告", "该IP已在白名单中")
            return
            
        self.ip_whitelist.add(ip)
        self.refresh_ip_list()
        self.ip_input.clear()
        
        # 如果服务正在运行，更新服务的白名单
        self.update_service_whitelist()
        
        logging.info(f"{self.username} - Added IP {ip} to whitelist")

    def remove_ip_from_whitelist(self, item):
        """
        从白名单中删除IP
        
        参数:
        item (QListWidgetItem): 列表项
        """
        ip = item.text()
        reply = QMessageBox.question(self, '确认', f'确定要删除IP {ip} 吗？',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                                   
        if reply == QMessageBox.Yes:
            self.ip_whitelist.remove(ip)
            self.refresh_ip_list()
            
            # 如果服务正在运行，更新服务的白名单
            self.update_service_whitelist()
            
            logging.info(f"{self.username} - Removed IP {ip} from whitelist")

    def refresh_ip_list(self):
        """刷新IP白名单显示"""
        self.ip_list.clear()
        for ip in sorted(self.ip_whitelist):
            item = QListWidgetItem(ip)
            self.ip_list.addItem(item)

    def update_service_whitelist(self):
        """更新运行中的上传服务的IP白名单"""
        if self.upload_service_process is not None:
            try:
                response = requests.post('http://localhost:5000/api/update_whitelist', 
                                      json={'whitelist': list(self.ip_whitelist)})
                if response.status_code == 200:
                    logging.info(f"{self.username} - Updated upload service whitelist")
                else:
                    logging.error(f"{self.username} - Failed to update upload service whitelist")
            except Exception as e:
                logging.error(f"{self.username} - Error updating whitelist: {str(e)}")

    def toggle_upload_service(self):
        """切换上传服务的开启/关闭状态"""
        if self.upload_service_process is None:
            # 启动服务
            try:
                # 准备环境变量
                env = os.environ.copy()
                # 将IP白名单转换为JSON字符串并通过环境变量传递
                env['ALLOWED_IPS'] = json.dumps(list(self.ip_whitelist))
                env['LOG_FILE'] = LOG_FILE
                env['USERNAME'] = self.username
                
                # 启动上传服务进程
                cmd = [sys.executable, 'backend/upload_service.py']
                self.upload_service_process = subprocess.Popen(
                    cmd,
                    env=env
                )
                
                self.service_toggle_btn.setText('关闭服务')
                self.service_toggle_btn.setStyleSheet("""
                    QPushButton {
                        font-size: 20px;
                        height: 60px;
                        width: 180px;
                        color: white;
                        background-color: rgb(215, 0, 0);
                        border-radius: 10px;
                    }
                    QPushButton:hover {
                        background-color: rgb(195, 0, 0);
                    }
                """)
                
                logging.info(f"{self.username} - Started upload service")
                QMessageBox.information(self, "成功", "上传服务已启动")
                
            except Exception as e:
                logging.error(f"{self.username} - Failed to start upload service: {str(e)}")
                QMessageBox.critical(self, "错误", f"启动上传服务失败：{str(e)}")
                self.upload_service_process = None
                
        else:
            # 关闭服务
            try:
                self.upload_service_process.terminate()
                self.upload_service_process = None
                
                self.service_toggle_btn.setText('开启服务')
                self.service_toggle_btn.setStyleSheet("""
                    QPushButton {
                        font-size: 20px;
                        height: 60px;
                        width: 180px;
                        color: white;
                        background-color: rgb(0, 120, 215);
                        border-radius: 10px;
                    }
                    QPushButton:hover {
                        background-color: rgb(0, 100, 195);
                    }
                """)
                
                logging.info(f"{self.username} - Stopped upload service")
                QMessageBox.information(self, "成功", "上传服务已关闭")
                
            except Exception as e:
                logging.error(f"{self.username} - Failed to stop upload service: {str(e)}")
                QMessageBox.critical(self, "错误", f"关闭上传服务失败：{str(e)}")

    def closeEvent(self, event):
        """
        窗口关闭事件处理
        
        参数:
        event: 关闭事件
        """
        # 关闭上传服务
        if self.upload_service_process is not None:
            try:
                self.upload_service_process.terminate()
                self.upload_service_process = None
                logging.info(f"{self.username} - Upload service stopped on window close")
            except Exception as e:
                logging.error(f"{self.username} - Error stopping upload service on window close: {str(e)}")
        
        event.accept()

    def show_progress_dialog(self, title, label_text, duration_ms=600000):  # 10分钟 = 600000毫秒
        """
        显示进度对话框
        
        参数:
        title: 对话框标题
        label_text: 提示文本
        duration_ms: 持续时间（毫秒）
        """
        progress = QProgressDialog(label_text, None, 0, 100, self)
        progress.setWindowTitle(title)
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)  # 禁用取消按钮
        progress.setMinimumDuration(0)  # 立即显示
        progress.setAutoClose(True)
        progress.setAutoReset(False)
        
        # 计算更新间隔（每次增加1%需要的时间）
        interval = duration_ms / 99  # 分99步，最后一步单独处理
        
        # 创建定时器
        timer = QTimer(self)
        current_progress = [0]  # 使用列表存储当前进度，以便在lambda中修改
        
        def update_progress():
            current_progress[0] += 1
            if current_progress[0] >= 99:
                timer.stop()
                progress.setValue(100)
            else:
                progress.setValue(current_progress[0])
        
        timer.timeout.connect(update_progress)
        timer.start(int(interval))
        
        return progress, timer

    def backup_system(self):
        """
        系统备份功能
        备份内容包括：
        1. 数据库文件
        2. data目录（数据存储）
        3. model目录（模型文件）
        4. data/results目录（结果报告）
        """
        try:
            # 先显示进度对话框
            progress, timer = self.show_progress_dialog("系统备份", "正在备份系统数据，请耐心等待...")
            progress.show()  # 立即显示进度条
            QApplication.processEvents()  # 立即处理事件，确保进度条显示

            # 创建时间戳作为备份文件名的一部分
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'system_backup_{timestamp}.zip'
            backup_path = os.path.join(BACKUP_DIR, backup_filename)

            # 创建并启动备份线程
            self.backup_thread = BackupThread(backup_path)
            
            def on_backup_finished(success, message):
                timer.stop()
                progress.close()
                if success:
                    logging.info(f"System backup created successfully: {backup_filename}")
                    QMessageBox.information(self, "备份成功", f"系统备份已完成！\n备份文件位置：{message}")
                else:
                    logging.error(f"Backup failed: {message}")
                    QMessageBox.critical(self, "备份失败", f"备份过程中发生错误：{message}")
                self.backup_thread = None

            self.backup_thread.finished.connect(on_backup_finished)
            self.backup_thread.start()

        except Exception as e:
            if 'timer' in locals():
                timer.stop()
            if 'progress' in locals():
                progress.close()
            logging.error(f"Backup failed: {str(e)}")
            QMessageBox.critical(self, "备份失败", f"备份过程中发生错误：{str(e)}")

    def restore_system(self):
        """
        系统恢复功能
        从备份文件恢复系统，包括：
        1. 数据库文件
        2. data目录
        3. model目录
        4. data/results目录
        """
        try:
            # 先显示进度对话框
            progress, timer = self.show_progress_dialog("系统恢复", "正在准备恢复系统数据...")
            progress.show()  # 立即显示进度条
            QApplication.processEvents()  # 立即处理事件，确保进度条显示

            # 选择备份文件
            backup_file, _ = QFileDialog.getOpenFileName(
                self,
                "选择备份文件",
                BACKUP_DIR,
                "备份文件 (system_backup_*.zip)"
            )

            if not backup_file:
                timer.stop()
                progress.close()
                return

            # 确认恢复操作
            reply = QMessageBox.question(
                self,
                '确认恢复',
                '此操作将覆盖当前系统数据，恢复完成后需要重新登录。是否继续？',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.No:
                timer.stop()
                progress.close()
                return

            # 更新进度条文本
            progress.setLabelText("正在恢复系统数据，请耐心等待...")
            QApplication.processEvents()

            # 创建并启动恢复线程
            self.restore_thread = RestoreThread(backup_file)
            
            def on_restore_finished(success, message):
                timer.stop()
                progress.close()
                if success:
                    logging.info("System restored successfully")
                    QMessageBox.information(self, "恢复成功", "系统恢复已完成！系统将退出到登录界面。")
                    # 退出到登录界面
                    self.logout_and_return_to_login()
                else:
                    logging.error(f"Restore failed: {message}")
                    QMessageBox.critical(self, "恢复失败", f"恢复过程中发生错误：{message}")
                self.restore_thread = None

            self.restore_thread.finished.connect(on_restore_finished)
            self.restore_thread.start()

        except Exception as e:
            if 'timer' in locals():
                timer.stop()
            if 'progress' in locals():
                progress.close()
            logging.error(f"Restore failed: {str(e)}")
            QMessageBox.critical(self, "恢复失败", f"恢复过程中发生错误：{str(e)}")

    def logout_and_return_to_login(self):
        """
        退出登录并返回到登录界面
        """
        try:
            # 清除用户状态
            with open(USER_STATUS_FILE, 'w') as f:
                f.write('0')  # 设置为未登录状态
            
            # 清除当前用户信息
            if os.path.exists(CURRENT_USER_FILE):
                os.remove(CURRENT_USER_FILE)
            
            # 关闭所有已注册的窗口
            window_manager = WindowManager()
            for window_name in list(window_manager._windows.keys()):
                window = window_manager.get_window(window_name)
                if window:
                    window.close()
            window_manager._windows.clear()
            
            # 创建并显示登录窗口
            from PyQt5.QtWidgets import QMainWindow
            from front.init_login_UI import Ui_MainWindow
            
            login_window = QMainWindow()
            ui = Ui_MainWindow()
            ui.setupUi(login_window)
            login_window.show()
            
        except Exception as e:
            logging.error(f"Error in logout: {str(e)}")
            QMessageBox.critical(self, "错误", f"退出登录时发生错误：{str(e)}")

    def returnIndex(self):
        """
        返回到相应的主页面
        根据用户类型返回到管理员或普通用户页面
        """
        start_time = time.time()  # 记录开始时间
        
        path = USER_STATUS_FILE
        user_status = operate_user.read(path)
        
        try:
            # 关闭上传服务
            if self.upload_service_process is not None:
                try:
                    self.upload_service_process.terminate()
                    self.upload_service_process = None
                    logging.info(f"{self.username} - Upload service stopped on return to index")
                except Exception as e:
                    logging.error(f"{self.username} - Error stopping upload service on return to index: {str(e)}")

            window_manager = WindowManager()
            if user_status == '1':  # 管理员
                # 检查是否已存在admin窗口
                admin_window = window_manager.get_window('admin')
                if not admin_window:
                    admin_window = admin_index_backend.AdminWindowActions()
                    window_manager.register_window('admin', admin_window)
                window_manager.show_window('admin')
            else:  # 普通用户
                # 检查是否已存在index窗口
                index_window = window_manager.get_window('index')
                if not index_window:
                    index_window = index_backend.Index_WindowActions()
                    window_manager.register_window('index', index_window)
                window_manager.show_window('index')
            
            # 隐藏并关闭当前窗口
            self.hide()
            self.close()
            
            # 记录返回耗时
            end_time = time.time()
            elapsed_ms = int((end_time - start_time) * 1000)  # 转换为毫秒
            logging.info(f"返回首页耗时: {elapsed_ms}毫秒")
            
            logging.info("Returned to index page successfully")
        except Exception as e:
            logging.error(f"Error in return_index: {str(e)}")
            QMessageBox.critical(self, "错误", f"返回主页时发生错误：{str(e)}")

    def savetoDB(self):
        """
        保存参数到数据库的处理函数
        """
        logging.info("Starting database save operation.")
        session = SessionClass()

        try:
            # 参数验证
            try:
                eeg_freq = float(self.sample_freq.text())
                electrode_count = int(self.electrode_numbers.text())
                question_num = int(self.question_num.text())
                model_num = int(self.model_num.text())
                
                # 检查是否为负数
                if eeg_freq < 0:
                    raise ValueError("脑电采样频率不能为负数")
                if electrode_count < 0:
                    raise ValueError("电极数量不能为负数") 
                if question_num < 0:
                    raise ValueError("量表题目数不能为负数")
                if model_num < 0:
                    raise ValueError("模型数量不能为负数")
                    
            except ValueError as ve:
                QMessageBox.warning(self, "输入错误", str(ve))
                logging.warning(f"Parameter validation failed: {str(ve)}")
                return

            # 查找现有记录
            existing_data = session.query(SystemParams).filter(SystemParams.id == 1).first()

            if existing_data is not None:
                # 记录修改前的值
                old_values = {
                    "eeg_frequency": existing_data.eeg_frequency,
                    "electrode_count": existing_data.electrode_count,
                    "scale_question_num": existing_data.scale_question_num,
                    "model_num": existing_data.model_num
                }
                
                # 更新现有记录
                logging.info("Updating existing SystemParams record.")
                existing_data.eeg_frequency = eeg_freq
                existing_data.electrode_count = electrode_count
                existing_data.scale_question_num = question_num
                existing_data.model_num = model_num
                
                # 记录修改的内容
                changes = []
                if old_values["eeg_frequency"] != eeg_freq:
                    changes.append(f"脑电采样频率: {old_values['eeg_frequency']} -> {eeg_freq}")
                if old_values["electrode_count"] != electrode_count:
                    changes.append(f"电极数量: {old_values['electrode_count']} -> {electrode_count}")
                if old_values["scale_question_num"] != question_num:
                    changes.append(f"量表题目数: {old_values['scale_question_num']} -> {question_num}")
                if old_values["model_num"] != model_num:
                    changes.append(f"模型数量: {old_values['model_num']} -> {model_num}")
                    
                if changes:
                    logging.info(f"Parameter changes: {'; '.join(changes)}")
                else:
                    logging.info("No parameter values were changed")
                    
            else:
                # 创建新记录
                logging.info("Creating new SystemParams record with values: "
                            f"eeg_frequency={eeg_freq}, "
                            f"electrode_count={electrode_count}, "
                            f"scale_question_num={question_num}, "
                            f"model_num={model_num}")
                            
                new_data = SystemParams(
                    param_id='PARAM_001',  # 设置一个固定的param_id
                    eeg_frequency=eeg_freq,
                    electrode_count=electrode_count,
                    scale_question_num=question_num,
                    model_num=model_num,
                    id=1  # 设置固定的id
                )
                session.add(new_data)

            session.commit()
            logging.info("Database transaction committed successfully.")
            QMessageBox.information(self, "成功", "参数保存成功！")

        except Exception as e:
            session.rollback()
            logging.error(f"Failed to save parameters: {e}")
            QMessageBox.critical(self, "错误", f"保存参数时发生错误：{str(e)}")
        finally:
            session.close()
            logging.info("Database session closed.")

        self.SHOWUi()

    def SHOWUi(self):
        """
        显示参数控制界面的UI，并从数据库加载最新的参数值
        """
        session = SessionClass()
        try:
            data = session.query(SystemParams).filter(SystemParams.id == 1).first()
            if data is not None:
                self.sample_freq.setText(str(data.eeg_frequency))
                self.electrode_numbers.setText(str(data.electrode_count))
                self.question_num.setText(str(data.scale_question_num))
                self.model_num.setText(str(data.model_num))
            else:
                # 如果没有数据，设置默认值
                self.sample_freq.setText("")
                self.electrode_numbers.setText("")
                self.question_num.setText("")
                self.model_num.setText("")
        except Exception as e:
            logging.error(f"Error loading parameters: {e}")
            QMessageBox.critical(self, "错误", f"加载参数时发生错误：{str(e)}")
        finally:
            session.close()

    def delete_selected_ip(self):
        """删除选中的IP地址"""
        selected_items = self.ip_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择要删除的IP地址")
            return
            
        item = selected_items[0]  # 获取选中的项
        self.remove_ip_from_whitelist(item)
