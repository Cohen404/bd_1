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
    QMessageBox, QFileDialog, QInputDialog, QProgressDialog
import shutil
import subprocess
import zipfile
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

    def __init__(self, backup_path):
        super().__init__()
        self.backup_path = backup_path

    def run(self):
        """
        执行备份操作
        """
        try:
            # 创建ZIP文件
            with zipfile.ZipFile(self.backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 1. 备份数据库文件
                db_backup_path = os.path.join(BACKUP_DIR, 'temp_db_backup.sql')
                
                # 使用pg_dump备份数据库
                dump_command = [
                    'pg_dump',
                    f'--host={HOST}',
                    f'--port={PORT}',
                    f'--username={USERNAME}',
                    f'--dbname={DATABASE}',
                    '--format=p',  # plain text format
                    f'--file={db_backup_path}'
                ]
                
                # 设置环境变量PGPASSWORD
                env = os.environ.copy()
                env['PGPASSWORD'] = PASSWORD
                
                # 执行pg_dump命令
                process = subprocess.Popen(
                    dump_command,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                _, stderr = process.communicate()
                
                if process.returncode != 0:
                    raise Exception(f"数据库备份失败: {stderr.decode()}")
                
                # 添加数据库备份文件到zip
                zipf.write(db_backup_path, 'database.sql')
                os.remove(db_backup_path)  # 删除临时文件

                # 2. 备份data目录
                data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
                if os.path.exists(data_dir):
                    for root, dirs, files in os.walk(data_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(data_dir))
                            zipf.write(file_path, arcname)

                # 3. 备份model目录
                model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'model')
                if os.path.exists(model_dir):
                    for root, dirs, files in os.walk(model_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(model_dir))
                            zipf.write(file_path, arcname)

            self.finished.emit(True, self.backup_path)
        except Exception as e:
            self.finished.emit(False, str(e))

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
        path = USER_STATUS_FILE
        user_status = operate_user.read(path)
        
        try:
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
            # 查找现有记录
            existing_data = session.query(SystemParams).filter(SystemParams.id == 1).first()

            if existing_data is not None:
                # 更新现有记录
                logging.info("Updating existing SystemParams record.")
                existing_data.eeg_frequency = float(self.sample_freq.text())
                existing_data.electrode_count = int(self.electrode_numbers.text())
                existing_data.scale_question_num = int(self.question_num.text())
                existing_data.model_num = int(self.model_num.text())
            else:
                # 创建新记录
                logging.info("Creating new SystemParams record.")
                new_data = SystemParams(
                    param_id='PARAM_001',  # 设置一个固定的param_id
                    eeg_frequency=float(self.sample_freq.text()),
                    electrode_count=int(self.electrode_numbers.text()),
                    scale_question_num=int(self.question_num.text()),
                    model_num=int(self.model_num.text()),
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
