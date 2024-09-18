# md5加密
import hashlib


def md5(arg):
    Hash = hashlib.md5()
    Hash.update(bytes(arg, encoding='utf-8'))
    return Hash.hexdigest()


# if __name__ == '__main__':
#     for i in range(1, 10):
#         print(i)
