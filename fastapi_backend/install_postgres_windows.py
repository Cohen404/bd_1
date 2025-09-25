#!/usr/bin/env python3
"""
PostgreSQL Windows安装和配置脚本
支持Windows系统的自动安装和配置
"""
import os
import sys
import subprocess
import platform
import logging
import urllib.request
import zipfile
import shutil
from pathlib import Path
import time
import tempfile

# 导入配置
sys.path.append(str(Path(__file__).parent))
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS, setup_logging

# 设置日志
setup_logging()
logger = logging.getLogger(__name__)

def run_command(command, shell=True, timeout=300):
    """运行命令并返回结果"""
    try:
        logger.info(f"执行命令: {command}")
        process = subprocess.Popen(
            command, 
            shell=shell, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            universal_newlines=True,
            creationflags=subprocess.CREATE_NO_WINDOW if shell else 0
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
    try:
        result = subprocess.run(f"where {command}", shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def is_postgres_installed():
    """检查PostgreSQL是否已安装"""
    return check_command_exists("psql") or check_command_exists("postgres")

def download_file(url, filename):
    """下载文件"""
    try:
        logger.info(f"正在下载: {url}")
        urllib.request.urlretrieve(url, filename)
        logger.info(f"下载完成: {filename}")
        return True
    except Exception as e:
        logger.error(f"下载失败: {e}")
        return False

def install_postgres_windows():
    """在Windows上安装PostgreSQL"""
    logger.info("开始在Windows上安装PostgreSQL...")
    
    # PostgreSQL 14.9 下载链接 (Windows x64)
    postgres_url = "https://get.enterprisedb.com/postgresql/postgresql-14.9-1-windows-x64.exe"
    installer_name = "postgresql-14.9-1-windows-x64.exe"
    
    # 检查是否已安装
    if is_postgres_installed():
        logger.info("PostgreSQL已安装")
        return True
    
    # 下载安装程序
    if not os.path.exists(installer_name):
        if not download_file(postgres_url, installer_name):
            logger.error("PostgreSQL安装程序下载失败")
            return False
    
    # 静默安装PostgreSQL
    logger.info("正在安装PostgreSQL...")
    install_cmd = f"{installer_name} --mode unattended --superpassword {DB_PASS} --servicename postgresql --serviceaccount postgres --servicepassword {DB_PASS} --serverport {DB_PORT}"
    
    success, output = run_command(install_cmd, timeout=600)
    if not success:
        logger.error("PostgreSQL安装失败")
        logger.error(f"安装输出: {output}")
        return False
    
    # 等待安装完成
    logger.info("等待PostgreSQL安装完成...")
    time.sleep(30)
    
    # 启动PostgreSQL服务
    logger.info("启动PostgreSQL服务...")
    success, _ = run_command("net start postgresql")
    if not success:
        logger.warning("PostgreSQL服务启动失败，尝试手动启动")
        # 尝试使用sc命令启动
        run_command("sc start postgresql")
    
    # 等待服务启动
    time.sleep(10)
    
    # 清理安装文件
    try:
        if os.path.exists(installer_name):
            os.remove(installer_name)
            logger.info("安装文件已清理")
    except Exception as e:
        logger.warning(f"清理安装文件失败: {e}")
    
    logger.info("PostgreSQL在Windows上安装成功")
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
    
    # 在Windows上使用psql命令
    postgres_cmd_prefix = ["psql", "-d", "postgres", "-U", "postgres"]
    
    # 设置环境变量
    env = os.environ.copy()
    env['PGPASSWORD'] = DB_PASS
    
    # 创建用户
    success, output = run_command(f'psql -d postgres -U postgres -c "{create_user_sql}"')
    if not success:
        logger.error(f"创建用户失败: {output}")
        return False
    
    # 创建数据库
    success, output = run_command(f'psql -d postgres -U postgres -c "{create_db_sql}"')
    if not success:
        logger.error(f"创建数据库失败: {output}")
        return False
    
    # 授予权限
    success, output = run_command(f'psql -d postgres -U postgres -c "{grant_privileges_sql}"')
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
    """创建.env文件"""
    env_file = Path(__file__).parent / '.env'
    if not env_file.exists():
        env_content = f"""# 数据库配置
DB_HOST={DB_HOST}
DB_PORT={DB_PORT}
DB_NAME={DB_NAME}
DB_USER={DB_USER}
DB_PASS={DB_PASS}

# JWT配置
SECRET_KEY=rjD66zC6e4h58TuPFa3peppOjsUc1dprKtCIVNds4cQ
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 安全配置
BCRYPT_ROUNDS=12

# 其他配置
DEBUG=true
LOG_LEVEL=INFO
"""
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        logger.info(f".env文件已创建: {env_file}")
    else:
        logger.info(".env文件已存在")

def check_windows_version():
    """检查Windows版本"""
    try:
        version = platform.version()
        logger.info(f"Windows版本: {version}")
        return True
    except Exception as e:
        logger.error(f"无法获取Windows版本: {e}")
        return False

def main():
    """主函数"""
    logger.info("开始PostgreSQL Windows安装和配置...")
    
    # 检查是否为Windows系统
    if platform.system().lower() != "windows":
        logger.error("此脚本仅支持Windows系统")
        return False
    
    # 检查Windows版本
    check_windows_version()
    
    # 创建.env文件
    create_env_file()
    
    # 检查PostgreSQL是否已安装
    if is_postgres_installed():
        logger.info("PostgreSQL已安装")
    else:
        # 安装PostgreSQL
        if not install_postgres_windows():
            logger.error("Windows上PostgreSQL安装失败")
            return False
    
    # 等待PostgreSQL服务启动
    logger.info("等待PostgreSQL服务启动...")
    time.sleep(15)
    
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
    
    logger.info("PostgreSQL Windows安装和配置完成！")
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
