import os
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取项目根目录的绝对路径
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# 日志文件路径
LOG_DIR = os.path.join(ROOT_DIR, 'log')
LOG_FILE = os.path.join(LOG_DIR, 'log.txt')

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

# 数据库配置
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'bj_health_db')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'tj654478')

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-jwt")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时

# 确保必要的目录存在
def ensure_directories():
    """确保所有必要的目录都存在"""
    directories = [
        LOG_DIR,
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

def setup_logging():
    """配置日志系统"""
    # 确保日志目录存在
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 清除所有现有的处理程序
    root_logger.handlers = []
    
    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(username)s - %(message)s')
    
    # 创建并配置文件处理程序
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # 创建并配置控制台处理程序
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # 添加处理程序到根日志记录器
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # 禁用 basicConfig 的传播
    logging.propagate = False 