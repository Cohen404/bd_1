import sys
import os
import socket
import tempfile
import zipfile
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt
import requests

class UploadWindow(QMainWindow):
    """
    数据目录上传窗口应用
    支持选择目录，自动压缩并上传
    """
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.temp_zip = None
        
    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle('数据目录上传工具')
        # 设置窗口初始大小和最小大小
        self.resize(600, 450)
        self.setMinimumSize(500, 400)
        
        # 主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 设置默认字体
        font = self.font()
        font.setPointSize(12)
        self.setFont(font)
        
        # 获取本机IP
        self.local_ip = self.get_local_ip()
        
        # 本机IP显示
        ip_layout = QHBoxLayout()
        ip_label = QLabel('本机IP:')
        ip_label.setMinimumWidth(80)
        ip_layout.addWidget(ip_label)
        self.local_ip_label = QLabel(self.local_ip)
        self.local_ip_label.setMinimumHeight(30)
        ip_layout.addWidget(self.local_ip_label, stretch=1)
        layout.addLayout(ip_layout)
        
        # 服务器地址输入
        server_layout = QHBoxLayout()
        server_label = QLabel('服务器IP:')
        server_label.setMinimumWidth(80)
        server_layout.addWidget(server_label)
        self.server_ip_input = QLineEdit('127.0.0.1')
        self.server_ip_input.setMinimumHeight(35)
        server_layout.addWidget(self.server_ip_input, stretch=1)
        layout.addLayout(server_layout)
        
        # 端口输入
        port_layout = QHBoxLayout()
        port_label = QLabel('端口号:')
        port_label.setMinimumWidth(80)
        port_layout.addWidget(port_label)
        self.port_input = QLineEdit('5000')
        self.port_input.setMinimumHeight(35)
        port_layout.addWidget(self.port_input, stretch=1)
        layout.addLayout(port_layout)
        
        # 目录选择
        dir_layout = QHBoxLayout()
        self.dir_path_label = QLabel('未选择目录')
        self.dir_path_label.setMinimumHeight(35)
        dir_layout.addWidget(self.dir_path_label, stretch=1)
        select_dir_btn = QPushButton('选择目录')
        select_dir_btn.setMinimumSize(120, 35)
        select_dir_btn.clicked.connect(self.select_directory)
        dir_layout.addWidget(select_dir_btn)
        layout.addLayout(dir_layout)
        
        # 上传按钮
        upload_btn = QPushButton('上传')
        upload_btn.setMinimumSize(150, 50)
        upload_btn.clicked.connect(self.upload_directory)
        layout.addWidget(upload_btn)
        
        # 状态显示
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMinimumHeight(40)
        layout.addWidget(self.status_label)
        
        # 设置布局间距
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
    def get_local_ip(self):
        """获取本机IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return '127.0.0.1'
        
    def select_directory(self):
        """选择要上传的数据目录"""
        dir_path = QFileDialog.getExistingDirectory(
            self, '选择目录', '', QFileDialog.ShowDirsOnly)
        if dir_path:
            self.dir_path = dir_path
            self.dir_path_label.setText(os.path.basename(dir_path) or dir_path)
            
    def create_zip_from_directory(self, source_dir):
        """
        将选中的目录压缩成ZIP文件
        
        参数:
        - source_dir: 源数据目录
        
        返回:
        - 临时ZIP文件的路径，如果失败则返回None
        """
        try:
            # 创建临时ZIP文件
            self.temp_zip = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
            
            # 获取目录名称
            dir_name = os.path.basename(source_dir)
            
            with zipfile.ZipFile(self.temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 遍历目录
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # 使用相对路径作为ZIP内的路径，确保解压后直接在目标目录下
                        arcname = os.path.relpath(file_path, os.path.dirname(source_dir))
                        zipf.write(file_path, arcname)
                        
            return self.temp_zip.name
        except Exception as e:
            QMessageBox.critical(self, '错误', f'创建ZIP文件失败：{str(e)}')
            if self.temp_zip:
                self.temp_zip.close()
                try:
                    os.unlink(self.temp_zip.name)
                except:
                    pass
                self.temp_zip = None
            return None
            
    def upload_directory(self):
        """压缩并上传目录"""
        if not hasattr(self, 'dir_path'):
            QMessageBox.warning(self, '警告', '请先选择要上传的目录')
            return
            
        server_ip = self.server_ip_input.text().strip()
        port = self.port_input.text().strip()
        
        if not server_ip or not port:
            QMessageBox.warning(self, '警告', '请填写完整的服务器地址和端口')
            return
            
        try:
            self.status_label.setText('正在压缩目录...')
            QApplication.processEvents()  # 更新UI
            
            # 压缩目录
            zip_path = self.create_zip_from_directory(self.dir_path)
            if not zip_path:
                self.status_label.setText('压缩失败')
                return
                
            url = f'http://{server_ip}:{port}/api/upload'
            self.status_label.setText('正在上传...')
            QApplication.processEvents()  # 更新UI
            
            # 准备请求数据
            with open(zip_path, 'rb') as zip_file:
                # 使用原始目录名作为ZIP文件名
                zip_filename = os.path.basename(self.dir_path) + '.zip'
                files = {'file': (zip_filename, zip_file)}
                data = {'username': 'admin'}  # 使用管理员账号上传
                
                # 发送请求
                response = requests.post(url, files=files, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        self.status_label.setText('上传成功！')
                        data_path = result.get('data_path', '')
                        success_msg = f'目录上传成功\n保存路径：{data_path}' if data_path else '目录上传成功'
                        QMessageBox.information(self, '成功', success_msg)
                        
                        # 提示用户刷新数据管理界面
                        QMessageBox.information(self, '提示', '请在数据管理界面点击刷新，查看新上传的数据')
                    else:
                        error_msg = result.get('message', '未知错误')
                        self.status_label.setText('上传失败')
                        QMessageBox.warning(self, '失败', f'服务器返回错误：{error_msg}')
                else:
                    self.status_label.setText('上传失败')
                    QMessageBox.warning(self, '失败', f'服务器返回状态码：{response.status_code}')
                    
        except requests.exceptions.RequestException as e:
            self.status_label.setText('上传失败')
            QMessageBox.critical(self, '错误', f'上传过程中发生错误：{str(e)}')
        except Exception as e:
            self.status_label.setText('上传失败')
            QMessageBox.critical(self, '错误', f'发生未知错误：{str(e)}')
        finally:
            # 清理临时文件
            if self.temp_zip:
                self.temp_zip.close()
                try:
                    os.unlink(self.temp_zip.name)
                except:
                    pass
                self.temp_zip = None
            
    def closeEvent(self, event):
        """窗口关闭事件，清理临时文件"""
        if self.temp_zip:
            self.temp_zip.close()
            try:
                os.unlink(self.temp_zip.name)
            except:
                pass
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UploadWindow()
    window.show()
    sys.exit(app.exec_())