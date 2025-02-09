import os
import sys
import json

sys.path.append('../')

from flask import Flask, request, jsonify
import os
import shutil
import zipfile
import tempfile
from datetime import datetime
from sqlalchemy import func
from sql_model.tb_data import Data
from sql_model.tb_user import User
from sql_model.tb_role import Role
from sql_model.tb_role_permission import RolePermission
from util.db_util import SessionClass
import logging

# 创建日志目录
os.makedirs('../log', exist_ok=True)

app = Flask(__name__)

# 添加用户名过滤器
class UsernameFilter(logging.Filter):
    def __init__(self, username):
        super().__init__()
        self.username = username

    def filter(self, record):
        record.username = self.username
        return True

# 配置日志
def setup_logger():
    """配置日志系统"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # 清除现有的处理器
    logger.handlers.clear()
    
    # 创建文件处理器
    file_handler = logging.FileHandler('../log/log.txt')
    file_handler.setLevel(logging.INFO)
    
    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(username)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # 添加处理器到logger
    logger.addHandler(file_handler)
    
    return logger

# 从环境变量获取IP白名单和用户名，如果没有则使用默认值
try:
    ALLOWED_IPS = set(json.loads(os.environ.get('ALLOWED_IPS', '["127.0.0.1"]')))
    username = os.environ.get('USERNAME', 'system')
except json.JSONDecodeError:
    ALLOWED_IPS = {'127.0.0.1'}
    username = 'system'
    logging.error("Failed to parse ALLOWED_IPS from environment, using default")

# 设置日志系统
logger = setup_logger()
logger.addFilter(UsernameFilter(username))

# 设置Werkzeug日志
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.addFilter(UsernameFilter(username))

def get_client_ip():
    """获取客户端真实IP地址"""
    # 首先尝试获取X-Forwarded-For头
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        # 取第一个IP（最原始的客户端IP）
        return forwarded_for.split(',')[0].strip()
    # 如果没有X-Forwarded-For头，使用远程地址
    return request.remote_addr

def check_ip_whitelist():
    """检查请求IP是否在白名单中"""
    client_ip = get_client_ip()
    logging.info(f"Incoming request from IP: {client_ip}")
    return client_ip in ALLOWED_IPS

def check_user_permission(user_id):
    """
    检查用户是否有上传数据的权限
    
    参数:
    - user_id: 用户ID
    
    返回:
    - bool: 是否有权限
    """
    session = SessionClass()
    try:
        # 检查用户是否存在
        user = session.query(User).filter(User.user_id == user_id).first()
        if not user:
            return False
            
        # 管理员直接有权限
        if user.user_type == 'admin':
            return True
            
        # 检查普通用户的权限
        return True  # 目前系统设计中普通用户也可以上传数据
    except Exception as e:
        logging.error(f"Error checking user permission: {str(e)}")
        return False
    finally:
        session.close()

@app.route('/api/update_whitelist', methods=['POST'])
def update_whitelist():
    """
    更新IP白名单
    
    参数:
    - whitelist: IP地址列表
    
    返回:
    JSON格式的响应，包含:
    - success: 布尔值，表示是否成功
    - message: 字符串，响应消息
    """
    try:
        data = request.get_json()
        if not data or 'whitelist' not in data:
            return jsonify({'success': False, 'message': 'No whitelist provided'}), 400
            
        whitelist = set(data['whitelist'])
        global ALLOWED_IPS
        ALLOWED_IPS = whitelist
        
        logging.info("IP whitelist updated")
        return jsonify({'success': True, 'message': 'Whitelist updated successfully'}), 200
        
    except Exception as e:
        logging.error(f"Error updating whitelist: {str(e)}")
        return jsonify({'success': False, 'message': f'Error updating whitelist: {str(e)}'}), 500

@app.route('/api/upload', methods=['POST'])
def upload_data():
    """
    接收数据上传请求的API端点
    
    参数:
    - file: ZIP文件(二进制)
    - user_id: 用户ID
    
    返回:
    JSON格式的响应，包含:
    - success: 布尔值，表示是否成功
    - message: 字符串，响应消息
    - data_path: 字符串，成功时返回数据存储路径
    """
    # 检查IP白名单
    if not check_ip_whitelist():
        client_ip = get_client_ip()
        logging.warning(f"Unauthorized IP attempt: {client_ip}")
        return jsonify({
            'success': False, 
            'message': 'Unauthorized IP address'
        }), 403

    try:
        # 验证请求参数
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file found'}), 400
        
        user_id = request.form.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'No user_id provided'}), 400

        # 验证用户权限
        if not check_user_permission(user_id):
            return jsonify({'success': False, 'message': 'User not authorized'}), 403

        # 获取用户信息
        session = SessionClass()
        user = session.query(User).filter(User.user_id == user_id).first()
        if not user:
            session.close()
            return jsonify({'success': False, 'message': 'User not found'}), 404

        # 更新日志用户名
        logger.removeFilter(logger.filters[0])
        logger.addFilter(UsernameFilter(user.username))

        uploaded_file = request.files['file']
        if not uploaded_file.filename.endswith('.zip'):
            return jsonify({'success': False, 'message': 'Only ZIP files are supported'}), 400

        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 保存ZIP文件到临时目录
            zip_path = os.path.join(temp_dir, 'upload.zip')
            uploaded_file.save(zip_path)

            # 解压ZIP文件到临时目录
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # 获取解压后的文件夹名称
            extracted_items = os.listdir(temp_dir)
            extracted_dir = None
            for item in extracted_items:
                if item != 'upload.zip' and os.path.isdir(os.path.join(temp_dir, item)):
                    extracted_dir = item
                    break

            if not extracted_dir:
                return jsonify({'success': False, 'message': 'No valid directory found in ZIP file'}), 400

            # 构建目标路径
            target_base_dir = '../data'
            target_dir = os.path.join(target_base_dir, extracted_dir)

            # 处理重名
            suffix = 1
            original_name = extracted_dir
            while os.path.exists(target_dir):
                new_name = f"{original_name}_{suffix}"
                target_dir = os.path.join(target_base_dir, new_name)
                suffix += 1

            # 确保目标目录存在
            os.makedirs(target_base_dir, exist_ok=True)

            # 复制文件到目标目录
            shutil.copytree(os.path.join(temp_dir, extracted_dir), target_dir)

            try:
                # 获取最大ID
                max_id = session.query(func.max(Data.id)).scalar()
                if max_id is None:
                    max_id = 0
                max_id = max_id + 1

                # 创建数据记录
                new_data = Data(
                    id=max_id,
                    personnel_id=str(user.user_id),  # 使用用户ID作为人员ID
                    data_path=target_dir,
                    upload_time=datetime.now(),
                    user_id=str(user.user_id),
                    personnel_name=user.username,
                    upload_user=1 if user.user_type == 'admin' else 0
                )

                session.add(new_data)
                session.commit()

                logging.info(f"Data uploaded successfully. Path: {target_dir}")
                
                return jsonify({
                    'success': True,
                    'message': 'Data uploaded successfully',
                    'data_path': target_dir
                }), 200

            except Exception as e:
                session.rollback()
                if os.path.exists(target_dir):
                    shutil.rmtree(target_dir)
                logging.error(f"Database error during upload: {str(e)}")
                return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
            
            finally:
                session.close()

    except Exception as e:
        logging.error(f"Error in upload API: {str(e)}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    logging.info("Upload service started")
    app.run(host='0.0.0.0', port=5000) 