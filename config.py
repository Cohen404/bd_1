import os

# 获取项目根目录的绝对路径
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# 日志文件路径
LOG_FILE = os.path.join(ROOT_DIR, 'log', 'log.txt')

# 状态文件路径
USER_STATUS_FILE = os.path.join(ROOT_DIR, 'state', 'user_status.txt')
CURRENT_USER_FILE = os.path.join(ROOT_DIR, 'state', 'current_user.txt')
MODEL_STATUS_FILE = os.path.join(ROOT_DIR, 'state', 'status.txt')

# 数据目录
DATA_DIR = os.path.join(ROOT_DIR, 'data')

# 模型目录
MODEL_DIR = os.path.join(ROOT_DIR, 'model')

# 模板目录
TEMPLATE_DIR = os.path.join(ROOT_DIR, 'templates')

# 结果目录
RESULTS_DIR = os.path.join(ROOT_DIR, 'data', 'results')

# 模板文件
TEMPLATE_FILE = os.path.join(TEMPLATE_DIR, 'template.docx')

# 确保必要的目录存在
def ensure_directories():
    """确保所有必要的目录都存在"""
    directories = [
        os.path.dirname(LOG_FILE),
        os.path.dirname(USER_STATUS_FILE),
        DATA_DIR,
        MODEL_DIR,
        TEMPLATE_DIR,
        RESULTS_DIR
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

# 在导入时就确保目录存在
ensure_directories() 