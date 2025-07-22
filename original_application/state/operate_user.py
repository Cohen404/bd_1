import os

def ensure_file_exists(path):
    """确保文件存在，如果不存在则创建"""
    if not os.path.exists(path):
        # 确保目录存在
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        # 创建文件
        with open(path, 'w', encoding='UTF-8') as file:
            file.write('')

def read(path):
    """读取文件内容"""
    with open(path, mode='r') as file:
        contents = file.read().strip()
        return contents

def save_user(path, username):
    """保存用户名到文件"""
    ensure_file_exists(path)
    with open(path, 'w', encoding='UTF-8') as file:
        file.write(username)

def admin_user(path):
    """将flag改为1，表示当前为管理员操作"""
    ensure_file_exists(path)
    with open(path, 'w', encoding='UTF-8') as file:
        file.write('1')

def ordinary_user(path):
    """将flag改为0，表示当前为普通用户操作"""
    ensure_file_exists(path)
    with open(path, 'w', encoding='UTF-8') as file:
        file.write('0')

if __name__ == '__main__':
    path = 'user_status.txt'
    a = read(path)
    print(a)
