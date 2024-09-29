def read(path):
    file = open(path, mode='r')
    contents = file.read()
    # print(contents)     # 从txt中读取的格式为str
    return contents
    # file.close()


# 将flag改为1，表示当前为管理员操作
def admin_user(path):
    # path = './user_status.txt'
    with open(path, 'w', encoding='UTF-8') as file:
        # 在我们的文本文件中写入替换的数据
        file.write('1')


# 将flag改为0，表示当前为普通用户操作
def ordinary_user(path):
    # path = './user_status.txt'
    with open(path, 'w', encoding='UTF-8') as file:
        # 在我们的文本文件中写入替换的数据
        file.write('0')


if __name__ == '__main__':
    path = 'user_status.txt'
    #     # read(path)
    #     # admin_user(path)
    #     print("------------")
    a = read(path)
    print(a)
#     if a == '1':
#         ordinary_user()
#     b = read()
#     print(b)
