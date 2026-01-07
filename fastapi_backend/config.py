import os
import logging
from dotenv import load_dotenv

# 加载环境变量 - 指定UTF-8编码
load_dotenv(encoding='utf-8')

# 获取项目根目录的绝对路径
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# 日志文件路径
LOG_DIR = os.path.join(ROOT_DIR, 'log')
LOG_FILE = os.path.join(LOG_DIR, 'app.log')

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

# 数据库配置 - 移除硬编码密码，使用环境变量
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'bj_health_db')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', '')  # 移除硬编码密码

# JWT配置 - 使用更安全的默认值
SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(32).hex())  # 生成随机密钥
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24小时

# 安全配置
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))  # bcrypt轮数

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
            try:
                os.makedirs(directory, exist_ok=True)
            except OSError as e:
                print(f"创建目录失败 {directory}: {e}")

# 自定义日志过滤器
class UserFilter(logging.Filter):
    def __init__(self, username="系统"):
        super().__init__()
        self.username = username

    def filter(self, record):
        if not hasattr(record, 'username'):
            record.username = self.username
        return True

def setup_logging():
    """配置统一的日志系统"""
    # 确保日志目录存在
    ensure_directories()
    
    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 清除所有现有的处理程序，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(username)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 创建并配置文件处理程序
    try:
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"无法创建文件日志处理程序: {e}")
    
    # 创建并配置控制台处理程序
    try:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    except Exception as e:
        print(f"无法创建控制台日志处理程序: {e}")
    
    # 添加自定义过滤器
    user_filter = UserFilter()
    for handler in root_logger.handlers:
        handler.addFilter(user_filter)
    
    # 禁用基本配置的传播
    root_logger.propagate = False

# 验证配置
def validate_config():
    """验证重要配置项"""
    issues = []
    
    if not DB_PASS:
        issues.append("数据库密码未设置，请设置环境变量 DB_PASS")
    
    if SECRET_KEY == os.urandom(32).hex():
        issues.append("JWT密钥使用随机生成，建议设置环境变量 SECRET_KEY")
    
    return issues

# 在导入时就确保目录存在并设置日志
ensure_directories()
setup_logging()

# 在开发环境中显示配置验证结果
if os.getenv('DEBUG', '').lower() in ('true', '1', 'yes'):
    config_issues = validate_config()
    if config_issues:
        logger = logging.getLogger(__name__)
        for issue in config_issues:
            logger.warning(f"配置警告: {issue}") 