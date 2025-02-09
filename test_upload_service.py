import requests
import os
import zipfile
import tempfile
import shutil
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_test_zip(source_dir, output_zip):
    """
    创建测试用的ZIP文件
    
    参数:
    - source_dir: 源数据目录
    - output_zip: 输出的ZIP文件路径
    """
    try:
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(source_dir))
                    zipf.write(file_path, arcname)
        logging.info(f"成功创建ZIP文件: {output_zip}")
        return True
    except Exception as e:
        logging.error(f"创建ZIP文件失败: {str(e)}")
        return False

def test_upload():
    """测试上传接口"""
    url = 'http://localhost:5000/api/upload'
    
    # 1. 测试IP白名单
    print("\n1. 测试IP白名单...")
    # 1.1 测试允许的IP (localhost)
    print("1.1 测试允许的IP (localhost)...")
    response = requests.post(url)
    print(f"允许的IP测试响应: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    # 1.2 测试不允许的IP
    print("\n1.2 测试不允许的IP...")
    # 通过设置X-Forwarded-For头来模拟不同的IP
    headers = {'X-Forwarded-For': '192.168.1.200'}  # 一个不在白名单中的IP
    response = requests.post(url, headers=headers)
    print(f"不允许的IP测试响应: {response.status_code}")
    print(f"响应内容: {response.json()}")

    # 2. 测试无文件上传
    print("\n2. 测试无文件上传...")
    data = {'user_id': 'admin001'}  # 使用管理员用户ID
    response = requests.post(url, data=data)
    print(f"无文件测试响应: {response.status_code}")
    print(f"响应内容: {response.json()}")

    # 3. 测试无user_id
    print("\n3. 测试无user_id...")
    # 创建临时ZIP文件
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
        if not create_test_zip('tmp/control_2', temp_zip.name):
            print("创建测试ZIP文件失败")
            return
        
        files = {'file': ('test.zip', open(temp_zip.name, 'rb'))}
        response = requests.post(url, files=files)
        print(f"无user_id测试响应: {response.status_code}")
        print(f"响应内容: {response.json()}")

    # 4. 测试完整上传流程
    print("\n4. 测试完整上传流程...")
    # 使用管理员用户ID
    data = {'user_id': 'admin001'}
    files = {'file': ('test.zip', open(temp_zip.name, 'rb'))}
    response = requests.post(url, files=files, data=data)
    print(f"完整上传测试响应: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    # 清理临时文件
    os.unlink(temp_zip.name)

if __name__ == '__main__':
    # 确保测试数据目录存在
    if not os.path.exists('tmp/control_2'):
        print("错误: 测试数据目录 'tmp/control_2' 不存在")
    else:
        test_upload() 