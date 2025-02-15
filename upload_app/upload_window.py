import sys
import os
import socket
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt
import requests

class UploadWindow(QMainWindow):
    """
    文件上传窗口应用
    """
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle('文件上传工具')
        self.setFixedSize(400, 300)
        
        # 主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 获取本机IP
        self.local_ip = self.get_local_ip()
        
        # 本机IP显示
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(QLabel('本机IP:'))
        self.local_ip_label = QLabel(self.local_ip)
        ip_layout.addWidget(self.local_ip_label)
        layout.addLayout(ip_layout)
        
        # 服务器地址输入
        server_layout = QHBoxLayout()
        server_layout.addWidget(QLabel('服务器IP:'))
        self.server_ip_input = QLineEdit('127.0.0.1')
        server_layout.addWidget(self.server_ip_input)
        layout.addLayout(server_layout)
        
        # 端口输入
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel('端口号:'))
        self.port_input = QLineEdit('5000')
        port_layout.addWidget(self.port_input)
        layout.addLayout(port_layout)
        
        # 文件选择
        file_layout = QHBoxLayout()
        self.file_path_label = QLabel('未选择文件')
        file_layout.addWidget(self.file_path_label)
        select_file_btn = QPushButton('选择文件')
        select_file_btn.clicked.connect(self.select_file)
        file_layout.addWidget(select_file_btn)
        layout.addLayout(file_layout)
        
        # 上传按钮
        upload_btn = QPushButton('上传')
        upload_btn.clicked.connect(self.upload_file)
        layout.addWidget(upload_btn)
        
        # 状态显示
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
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
        
    def select_file(self):
        """选择要上传的文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, '选择文件', '', 'ZIP文件 (*.zip)')
        if file_path:
            self.file_path = file_path
            self.file_path_label.setText(os.path.basename(file_path))
            
    def upload_file(self):
        """上传文件"""
        if not hasattr(self, 'file_path'):
            QMessageBox.warning(self, '警告', '请先选择要上传的文件')
            return
            
        server_ip = self.server_ip_input.text().strip()
        port = self.port_input.text().strip()
        
        if not server_ip or not port:
            QMessageBox.warning(self, '警告', '请填写完整的服务器地址和端口')
            return
            
        try:
            url = f'http://{server_ip}:{port}/api/upload'
            self.status_label.setText('上传中...')
            
            # 准备请求数据
            files = {'file': (os.path.basename(self.file_path), open(self.file_path, 'rb'))}
            data = {'username': 'admin'}  # 使用管理员账号上传
            
            # 发送请求
            response = requests.post(url, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.status_label.setText('上传成功！')
                    QMessageBox.information(self, '成功', '文件上传成功')
                else:
                    self.status_label.setText('上传失败')
                    QMessageBox.warning(self, '失败', result.get('message', '未知错误'))
            else:
                self.status_label.setText('上传失败')
                QMessageBox.warning(self, '失败', f'服务器返回状态码：{response.status_code}')
                
        except requests.exceptions.RequestException as e:
            self.status_label.setText('上传失败')
            QMessageBox.critical(self, '错误', f'上传过程中发生错误：{str(e)}')
        except Exception as e:
            self.status_label.setText('上传失败')
            QMessageBox.critical(self, '错误', f'发生未知错误：{str(e)}')
            
    def closeEvent(self, event):
        """窗口关闭事件"""
        if hasattr(self, 'file_path'):
            try:
                open(self.file_path, 'rb').close()
            except:
                pass
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UploadWindow()
    window.show()
    sys.exit(app.exec_())