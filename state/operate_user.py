def read(path):
    """读取文件内容"""
    with open(path, mode='r') as file:
        contents = file.read().strip()
        return contents


def save_user(path, username):
    """保存用户名到文件"""
    with open(path, 'w', encoding='UTF-8') as file:
        file.write(username)


# 将flag改为1，表示当前为管理员操作
def admin_user(path):
    with open(path, 'w', encoding='UTF-8') as file:
        file.write('1')


# 将flag改为0，表示当前为普通用户操作
def ordinary_user(path):
    with open(path, 'w', encoding='UTF-8') as file:
        file.write('0')


if __name__ == '__main__':
    path = 'user_status.txt'
    a = read(path)
    print(a)
