import os
import sys

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
from util.db_util import SessionClass
import logging

app = Flask(__name__)

# 配置日志
logging.basicConfig(
    filename='../log/upload_service.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 定义允许访问的IP白名单
ALLOWED_IPS = {
    '127.0.0.1',  # localhost
    '192.168.1.100',  # 示例IP，请根据实际需求修改
    # 在这里添加其他允许的IP地址
}

def check_ip_whitelist():
    """检查请求IP是否在白名单中"""
    client_ip = request.remote_addr
    return client_ip in ALLOWED_IPS

@app.route('/api/upload', methods=['POST'])
def upload_data():
    """
    接收数据上传请求的API端点
    
    参数:
    - file: ZIP文件(二进制)
    - username: 用户名
    
    返回:
    JSON格式的响应，包含:
    - success: 布尔值，表示是否成功
    - message: 字符串，响应消息
    - data_path: 字符串，成功时返回数据存储路径
    """
    # 检查IP白名单
    if not check_ip_whitelist():
        logging.warning(f"Unauthorized IP attempt: {request.remote_addr}")
        return jsonify({
            'success': False, 
            'message': '未授权的IP地址'
        }), 403

    try:
        # 验证请求参数
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '未找到文件'}), 400
        
        username = request.form.get('username')
        if not username:
            return jsonify({'success': False, 'message': '未提供username'}), 400

        # 验证用户是否存在
        session = SessionClass()
        user = session.query(User).filter(User.username == username).first()
        if not user:
            session.close()
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        uploaded_file = request.files['file']
        if not uploaded_file.filename.endswith('.zip'):
            return jsonify({'success': False, 'message': '仅支持ZIP文件'}), 400

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
                return jsonify({'success': False, 'message': 'ZIP文件中未找到有效目录'}), 400

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
                    personnel_id=str(user.user_id),
                    data_path=target_dir,
                    upload_time=datetime.now(),
                    user_id=str(user.user_id),
                    personnel_name=user.username,
                    upload_user=1 if user.user_type == 'admin' else 0
                )

                session.add(new_data)
                session.commit()

                logging.info(f"Data uploaded successfully via API. Path: {target_dir}, User: {user.username}")
                
                return jsonify({
                    'success': True,
                    'message': '数据上传成功',
                    'data_path': target_dir
                }), 200

            except Exception as e:
                session.rollback()
                if os.path.exists(target_dir):
                    shutil.rmtree(target_dir)
                logging.error(f"Database error during API upload: {str(e)}")
                return jsonify({'success': False, 'message': f'数据库错误: {str(e)}'}), 500
            
            finally:
                session.close()

    except Exception as e:
        logging.error(f"Error in upload API: {str(e)}")
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500

if __name__ == '__main__':
    print("service started")
    app.run(host='0.0.0.0', port=5000) 