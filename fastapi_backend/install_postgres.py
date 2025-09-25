#!/usr/bin/env python3
"""
PostgreSQL安装和配置脚本
支持macOS和Ubuntu系统的自动安装和配置
"""
import os
import sys
import subprocess
import platform
import logging
from pathlib import Path
import time
import shutil

# 导入配置
sys.path.append(str(Path(__file__).parent))
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS, setup_logging
from database import DATABASE_URL

# 设置日志
setup_logging()
logger = logging.getLogger(__name__)

def run_command(command, shell=False, timeout=300):
    """运行命令并返回结果"""
    try:
        logger.info(f"执行命令: {command}")
        if shell:
            process = subprocess.Popen(
                command, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
        else:
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
        
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            logger.error(f"命令执行超时: {command}")
            return False, "命令执行超时"
            
        if process.returncode != 0:
            logger.error(f"命令执行失败: {command}")
            logger.error(f"错误输出: {stderr}")
            return False, stderr
        return True, stdout
    except Exception as e:
        logger.error(f"执行命令时发生异常 {command}: {str(e)}")
        return False, str(e)

def check_command_exists(command):
    """检查命令是否存在"""
    return shutil.which(command) is not None

def is_postgres_installed():
    """检查PostgreSQL是否已安装"""
    return check_command_exists("psql") or check_command_exists("postgres")

def install_homebrew_macos():
    """在macOS上安装Homebrew"""
    logger.info("正在安装Homebrew...")
    install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    success, output = run_command(install_cmd, shell=True, timeout=600)
    if success:
        logger.info("Homebrew安装成功")
        # 设置PATH环境变量
        if platform.machine() == 'arm64':  # Apple Silicon
            brew_path = '/opt/homebrew/bin'
        else:  # Intel Mac
            brew_path = '/usr/local/bin'
        
        if brew_path not in os.environ.get('PATH', ''):
            os.environ['PATH'] = f"{brew_path}:{os.environ.get('PATH', '')}"
        return True
    else:
        logger.error("Homebrew安装失败")
        return False

def install_postgres_macos():
    """在macOS上安装PostgreSQL"""
    logger.info("开始在macOS上安装PostgreSQL...")
    
    # 检查并安装Homebrew
    if not check_command_exists("brew"):
        logger.info("未找到Homebrew，正在安装...")
        if not install_homebrew_macos():
            return False
    
    # 更新Homebrew
    logger.info("更新Homebrew...")
    success, _ = run_command(["brew", "update"])
    if not success:
        logger.warning("Homebrew更新失败，继续安装PostgreSQL")
    
    # 安装PostgreSQL
    logger.info("安装PostgreSQL...")
    success, _ = run_command(["brew", "install", "postgresql@14"])
    if not success:
        logger.error("PostgreSQL安装失败")
        return False
    
    # 启动PostgreSQL服务
    logger.info("启动PostgreSQL服务...")
    success, _ = run_command(["brew", "services", "start", "postgresql@14"])
    if not success:
        logger.error("PostgreSQL服务启动失败")
        return False
    
    # 等待服务启动
    time.sleep(10)
    
    logger.info("PostgreSQL在macOS上安装成功")
    return True

def install_postgres_ubuntu():
    """在Ubuntu上安装PostgreSQL"""
    logger.info("开始在Ubuntu上安装PostgreSQL...")
    
    # 更新包列表
    logger.info("更新包列表...")
    success, _ = run_command(["sudo", "apt-get", "update"])
    if not success:
        logger.error("更新包列表失败")
        return False
    
    # 安装PostgreSQL
    logger.info("安装PostgreSQL和相关工具...")
    success, _ = run_command([
        "sudo", "apt-get", "install", "-y", 
        "postgresql", "postgresql-contrib", "postgresql-client"
    ])
    if not success:
        logger.error("PostgreSQL安装失败")
        return False
    
    # 启动并启用PostgreSQL服务
    logger.info("启动PostgreSQL服务...")
    success, _ = run_command(["sudo", "systemctl", "start", "postgresql"])
    if not success:
        logger.error("PostgreSQL服务启动失败")
        return False
    
    success, _ = run_command(["sudo", "systemctl", "enable", "postgresql"])
    if not success:
        logger.warning("PostgreSQL服务自启动设置失败")
    
    # 等待服务启动
    time.sleep(5)
    
    logger.info("PostgreSQL在Ubuntu上安装成功")
    return True

def test_postgres_connection():
    """测试PostgreSQL连接"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database='postgres',  # 连接默认数据库
            user=DB_USER,
            password=DB_PASS
        )
        conn.close()
        return True
    except Exception as e:
        logger.error(f"PostgreSQL连接测试失败: {e}")
        return False

def create_db_and_user():
    """创建数据库和用户"""
    logger.info(f"创建数据库 {DB_NAME} 和用户 {DB_USER}...")
    
    if not DB_PASS:
        logger.error("数据库密码未设置，请设置环境变量 DB_PASS")
        return False
    
    os_name = platform.system().lower()
    
    # 准备SQL命令
    create_user_sql = f"""
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{DB_USER}') THEN
        CREATE USER {DB_USER} WITH PASSWORD '{DB_PASS}';
        RAISE NOTICE '用户 {DB_USER} 已创建';
    ELSE
        RAISE NOTICE '用户 {DB_USER} 已存在';
    END IF;
END
$$;
"""
    
    create_db_sql = f"""
SELECT 'CREATE DATABASE {DB_NAME}' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '{DB_NAME}')\\gexec
"""
    
    grant_privileges_sql = f"""
GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER};
ALTER USER {DB_USER} CREATEDB;
"""
    
    if os_name == "darwin":  # macOS
        postgres_cmd_prefix = ["psql", "-d", "postgres"]
    else:  # Ubuntu
        postgres_cmd_prefix = ["sudo", "-u", "postgres", "psql"]
    
    # 创建用户
    success, output = run_command(postgres_cmd_prefix + ["-c", create_user_sql])
    if not success:
        logger.error(f"创建用户失败: {output}")
        return False
    
    # 创建数据库
    success, output = run_command(postgres_cmd_prefix + ["-c", create_db_sql])
    if not success:
        logger.error(f"创建数据库失败: {output}")
        return False
    
    # 授予权限
    success, output = run_command(postgres_cmd_prefix + ["-c", grant_privileges_sql])
    if not success:
        logger.error(f"授予权限失败: {output}")
        return False
    
    logger.info(f"数据库 {DB_NAME} 和用户 {DB_USER} 创建成功")
    return True

def initialize_database():
    """初始化数据库表"""
    logger.info("初始化数据库表...")
    
    try:
        from database import init_db
        init_db()
        logger.info("数据库表初始化成功")
        return True
    except Exception as e:
        logger.error(f"数据库表初始化失败: {str(e)}")
        return False

def create_env_file():
    """创建.env文件模板"""
    env_file = Path(__file__).parent / '.env'
    if not env_file.exists():
        env_content = f"""# 数据库配置
DB_HOST={DB_HOST}
DB_PORT={DB_PORT}
DB_NAME={DB_NAME}
DB_USER={DB_USER}
DB_PASS=你的数据库密码

# JWT配置
SECRET_KEY=你的JWT密钥
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 其他配置
DEBUG=true
BCRYPT_ROUNDS=12
"""
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        logger.info(f".env文件已创建: {env_file}")
        logger.info("请编辑.env文件，设置正确的配置值")

def main():
    """主函数"""
    logger.info("开始PostgreSQL安装和配置...")
    
    # 创建.env文件模板
    create_env_file()
    
    # 检查PostgreSQL是否已安装
    if is_postgres_installed():
        logger.info("PostgreSQL已安装")
    else:
        # 根据操作系统安装PostgreSQL
        os_name = platform.system().lower()
        if os_name == "darwin":  # macOS
            if not install_postgres_macos():
                logger.error("macOS上PostgreSQL安装失败")
                return False
        elif os_name == "linux":  # Linux
            # 检查是否为Ubuntu/Debian
            try:
                with open('/etc/os-release', 'r') as f:
                    os_info = f.read().lower()
                if 'ubuntu' in os_info or 'debian' in os_info:
                    if not install_postgres_ubuntu():
                        logger.error("Ubuntu上PostgreSQL安装失败")
                        return False
                else:
                    logger.error("不支持的Linux发行版，请手动安装PostgreSQL")
                    return False
            except FileNotFoundError:
                logger.error("无法识别Linux发行版，请手动安装PostgreSQL")
                return False
        else:
            logger.error(f"不支持的操作系统: {os_name}，请手动安装PostgreSQL")
            return False
    
    # 等待PostgreSQL服务启动
    logger.info("等待PostgreSQL服务启动...")
    time.sleep(10)
    
    # 创建数据库和用户
    if not create_db_and_user():
        logger.error("数据库和用户创建失败")
        return False
    
    # 测试连接
    if test_postgres_connection():
        logger.info("PostgreSQL连接测试成功")
    else:
        logger.warning("PostgreSQL连接测试失败，请检查配置")
    
    # 初始化数据库表
    if not initialize_database():
        logger.error("数据库表初始化失败")
        return False
    
    logger.info("PostgreSQL安装和配置完成！")
    logger.info(f"数据库连接URL: {DATABASE_URL}")
    logger.info("请确保在.env文件中设置了正确的数据库密码")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("安装过程被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"安装过程发生未知错误: {e}", exc_info=True)
        sys.exit(1) 