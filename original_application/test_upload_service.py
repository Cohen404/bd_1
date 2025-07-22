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
        logging.info(f"成功创建压缩文件: {output_zip}")
        return True
    except Exception as e:
        logging.error(f"创建压缩文件失败: {str(e)}")
        return False

def test_upload():
    """测试上传接口"""
    url = 'http://10.168.2.152:5000/api/upload'
    test_username = 'admin'  # 使用管理员账号进行测试
    
    print("\n1. 测试IP白名单...")
    # 1.1 测试允许的IP (本地)
    print("1.1 测试允许的IP (本地)...")
    response = requests.post(url)
    print(f"允许的IP测试响应: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    # 1.2 测试不允许的IP
    print("\n1.2 测试不允许的IP...")
    headers = {'X-Forwarded-For': '192.168.1.200'}  # 一个不在白名单中的IP
    response = requests.post(url, headers=headers)
    print(f"不允许的IP测试响应: {response.status_code}")
    print(f"响应内容: {response.json()}")

    # 2. 测试无文件上传
    print("\n2. 测试无文件上传...")
    data = {'username': test_username}
    response = requests.post(url, data=data)
    print(f"无文件测试响应: {response.status_code}")
    print(f"响应内容: {response.json()}")

    # 3. 测试无用户名
    print("\n3. 测试无用户名...")
    temp_zip = None
    try:
        # 创建临时ZIP文件
        temp_zip = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        if not create_test_zip('tmp/abcde', temp_zip.name):
            print("创建测试压缩文件失败")
            return
        
        with open(temp_zip.name, 'rb') as zip_file:
            files = {'file': ('test.zip', zip_file)}
            response = requests.post(url, files=files)
            print(f"无用户名测试响应: {response.status_code}")
            print(f"响应内容: {response.json()}")

        # 4. 测试完整上传流程
        print("\n4. 测试完整上传流程...")
        data = {'username': test_username}
        with open(temp_zip.name, 'rb') as zip_file:
            files = {'file': ('test.zip', zip_file)}
            response = requests.post(url, files=files, data=data)
            print(f"完整上传测试响应: {response.status_code}")
            print(f"响应内容: {response.json()}")
    
    finally:
        # 确保文件句柄已关闭
        if temp_zip:
            temp_zip.close()
            try:
                # 尝试删除临时文件
                os.unlink(temp_zip.name)
            except Exception as e:
                logging.warning(f"删除临时文件失败: {str(e)}")

if __name__ == '__main__':
    # 确保测试数据目录存在
    if not os.path.exists('tmp/abcde'):
        print("错误: 测试数据目录不存在")
        logging.error("测试数据目录不存在")
    else:
        logging.info("开始运行上传服务测试...")
        test_upload()
        logging.info("上传服务测试完成") 