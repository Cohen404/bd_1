import requests
import os
import zipfile
import tempfile

def create_test_zip():
    """创建测试用的ZIP文件"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文件夹和文件
        test_folder = os.path.join(temp_dir, 'test_data')
        os.makedirs(test_folder)
        
        # 创建一个测试文件
        with open(os.path.join(test_folder, 'test.txt'), 'w') as f:
            f.write('This is a test file')
        
        # 创建ZIP文件
        zip_path = os.path.join(temp_dir, 'test.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(test_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
        
        # 读取ZIP文件内容
        with open(zip_path, 'rb') as f:
            return f.read()

def test_upload():
    """测试上传接口"""
    url = 'http://localhost:5000/api/upload'
    
    # 1. 测试IP白名单
    print("\n1. 测试IP白名单...")
    response = requests.post(url)
    print(f"IP白名单测试响应: {response.status_code}")
    print(f"响应内容: {response.json()}")

    # 2. 测试无文件上传
    print("\n2. 测试无文件上传...")
    response = requests.post(url, data={'username': 'admin'})
    print(f"无文件测试响应: {response.status_code}")
    print(f"响应内容: {response.json()}")

    # 3. 测试无username
    print("\n3. 测试无username...")
    files = {'file': ('test.zip', create_test_zip())}
    response = requests.post(url, files=files)
    print(f"无username测试响应: {response.status_code}")
    print(f"响应内容: {response.json()}")

    # 4. 测试完整上传流程
    print("\n4. 测试完整上传流程...")
    files = {'file': ('test.zip', create_test_zip())}
    data = {'username': 'admin'}  # 确保这个username在数据库中存在
    response = requests.post(url, files=files, data=data)
    print(f"完整上传测试响应: {response.status_code}")
    print(f"响应内容: {response.json()}")

if __name__ == '__main__':
    test_upload() 