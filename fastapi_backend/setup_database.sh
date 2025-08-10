#!/bin/bash

# PostgreSQL数据库建立和初始化脚本
# 支持macOS和Ubuntu系统
# 作者: AI Assistant
# 日期: $(date +"%Y-%m-%d")

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 获取操作系统类型
get_os_type() {
    case "$(uname -s)" in
        Darwin*) echo "macos" ;;
        Linux*) 
            if [ -f /etc/os-release ]; then
                . /etc/os-release
                case "$ID" in
                    ubuntu*) echo "ubuntu" ;;
                    debian*) echo "ubuntu" ;;  # 使用ubuntu的安装方式
                    *) echo "linux" ;;
                esac
            else
                echo "linux"
            fi
            ;;
        *) echo "unknown" ;;
    esac
}

# 读取.env文件
load_env_file() {
    local env_file="$1"
    if [ -f "$env_file" ]; then
        log_info "加载环境变量文件: $env_file"
        # 读取.env文件并导出变量
        # 使用while read循环，并处理文件末尾可能没有换行符的情况
        while IFS= read -r line || [[ -n "$line" ]]; do
            # 跳过注释和空行
            if [[ "$line" =~ ^[[:space:]]*# ]] || [[ -z "$line" ]]; then
                continue
            fi
            # 导出变量
            if [[ "$line" =~ ^[[:space:]]*([^=]+)=(.*)$ ]]; then
                local key="${BASH_REMATCH[1]}"
                local value="${BASH_REMATCH[2]}"
                # 移除前后空格
                key=$(echo "$key" | xargs)
                value=$(echo "$value" | xargs)
                # 移除引号（如果有的话）
                value=$(echo "$value" | sed 's/^["'\'']\|["'\'']$//g')
                export "$key"="$value"
                log_info "设置环境变量: $key"
            fi
        done < "$env_file"
    else
        log_error "环境变量文件不存在: $env_file"
        return 1
    fi
}

# 设置默认值
set_default_values() {
    export DB_HOST="${DB_HOST:-127.0.0.1}"
    export DB_PORT="${DB_PORT:-5432}"
    export DB_NAME="${DB_NAME:-bj_health_db}"
    export DB_USER="${DB_USER:-bj_health_user}"
    export DB_PASS="${DB_PASS:-}"
    export POSTGRES_SUPERUSER="${POSTGRES_SUPERUSER:-postgres}"
    export POSTGRES_SUPERUSER_PASSWORD="${POSTGRES_SUPERUSER_PASSWORD:-}"
    
    log_info "数据库配置:"
    log_info "  主机: $DB_HOST"
    log_info "  端口: $DB_PORT"
    log_info "  数据库名: $DB_NAME"
    log_info "  用户名: $DB_USER"
}

# 验证必需的环境变量
validate_required_vars() {
    local missing_vars=()
    
    if [ -z "$DB_PASS" ]; then
        missing_vars+=("DB_PASS")
    fi
    
    if [ -z "$POSTGRES_SUPERUSER_PASSWORD" ]; then
        missing_vars+=("POSTGRES_SUPERUSER_PASSWORD")
    fi
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        log_error "缺少必需的环境变量:"
        for var in "${missing_vars[@]}"; do
            log_error "  - $var"
        done
        log_error "请在.env文件中设置这些变量"
        return 1
    fi
}

# 安装PostgreSQL - macOS
install_postgresql_macos() {
    log_info "在macOS上安装PostgreSQL..."
    
    # 检查Homebrew
    if ! command_exists brew; then
        log_error "请先安装Homebrew: https://brew.sh/"
        return 1
    fi
    
    # 安装PostgreSQL
    if ! command_exists psql; then
        log_info "使用Homebrew安装PostgreSQL..."
        brew install postgresql@15
        
        # 启动PostgreSQL服务
        log_info "启动PostgreSQL服务..."
        brew services start postgresql@15
        
        # 等待服务启动
        sleep 5
        
        # 添加到PATH
        export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
        echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
    else
        log_success "PostgreSQL已安装"
        
        # 确保服务运行
        if ! pgrep -x "postgres" > /dev/null; then
            log_info "启动PostgreSQL服务..."
            brew services start postgresql@15
            sleep 5
        fi
    fi
}

# 安装PostgreSQL - Ubuntu
install_postgresql_ubuntu() {
    log_info "在Ubuntu上安装PostgreSQL..."
    
    # 更新包列表
    sudo apt update
    
    # 安装PostgreSQL
    if ! command_exists psql; then
        log_info "安装PostgreSQL..."
        sudo apt install -y postgresql postgresql-contrib
        
        # 启动PostgreSQL服务
        log_info "启动PostgreSQL服务..."
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
        
        # 等待服务启动
        sleep 5
    else
        log_success "PostgreSQL已安装"
        
        # 确保服务运行
        if ! systemctl is-active --quiet postgresql; then
            log_info "启动PostgreSQL服务..."
            sudo systemctl start postgresql
            sleep 5
        fi
    fi
}

# 安装PostgreSQL
install_postgresql() {
    local os_type=$(get_os_type)
    
    case "$os_type" in
        macos)
            install_postgresql_macos
            ;;
        ubuntu)
            install_postgresql_ubuntu
            ;;
        *)
            log_error "不支持的操作系统: $os_type"
            log_error "请手动安装PostgreSQL"
            return 1
            ;;
    esac
}

# 检查PostgreSQL连接
test_postgresql_connection() {
    local user="$1"
    local password="$2"
    local host="$3"
    local port="$4"
    local database="${5:-postgres}"
    
    log_info "测试PostgreSQL连接..."
    
    # 使用PGPASSWORD环境变量避免密码提示
    PGPASSWORD="$password" psql -h "$host" -p "$port" -U "$user" -d "$database" -c "\q" 2>/dev/null
}

# 创建数据库用户
create_database_user() {
    # 如果DB_USER就是postgres超级用户，跳过用户创建
    if [ "$DB_USER" = "$POSTGRES_SUPERUSER" ]; then
        log_info "使用PostgreSQL超级用户 $DB_USER，跳过用户创建"
        return 0
    fi
    
    log_info "创建数据库用户: $DB_USER"
    
    # 检查用户是否已存在
    local user_exists
    user_exists=$(PGPASSWORD="$POSTGRES_SUPERUSER_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_SUPERUSER" -d postgres -t -c "SELECT 1 FROM pg_user WHERE usename='$DB_USER';" 2>/dev/null | xargs)
    
    if [ "$user_exists" = "1" ]; then
        log_warning "用户 $DB_USER 已存在，跳过创建"
    else
        PGPASSWORD="$POSTGRES_SUPERUSER_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_SUPERUSER" -d postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
        log_success "用户 $DB_USER 创建成功"
    fi
}

# 创建数据库
create_database() {
    log_info "创建数据库: $DB_NAME"
    
    # 检查数据库是否已存在
    local db_exists
    db_exists=$(PGPASSWORD="$POSTGRES_SUPERUSER_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_SUPERUSER" -d postgres -t -c "SELECT 1 FROM pg_database WHERE datname='$DB_NAME';" 2>/dev/null | xargs)
    
    if [ "$db_exists" = "1" ]; then
        log_warning "数据库 $DB_NAME 已存在，跳过创建"
    else
        if [ "$DB_USER" = "$POSTGRES_SUPERUSER" ]; then
            # 如果使用超级用户，直接创建数据库
            PGPASSWORD="$POSTGRES_SUPERUSER_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_SUPERUSER" -d postgres -c "CREATE DATABASE $DB_NAME;"
        else
            # 如果是普通用户，设置owner
            PGPASSWORD="$POSTGRES_SUPERUSER_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_SUPERUSER" -d postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
        fi
        log_success "数据库 $DB_NAME 创建成功"
    fi
    
    # 授权（只有在不是超级用户时才需要）
    if [ "$DB_USER" != "$POSTGRES_SUPERUSER" ]; then
        PGPASSWORD="$POSTGRES_SUPERUSER_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_SUPERUSER" -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
        log_success "数据库权限设置完成"
    else
        log_info "使用超级用户，跳过权限设置"
    fi
}

# 初始化数据库表
initialize_database_tables() {
    log_info "初始化数据库表..."
    
    # 激活Python虚拟环境（如果存在）
    if [ -f "./venv/bin/activate" ]; then
        log_info "激活Python虚拟环境..."
        source ./venv/bin/activate
        
        # 使用虚拟环境中的Python
        PYTHON_CMD="./venv/bin/python"
    else
        PYTHON_CMD="python"
    fi
    
    # 使用Python脚本初始化表
    cat > init_db_tables.py << 'EOF'
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_db
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("开始初始化数据库表...")
    init_db()
    logger.info("数据库表初始化完成")
except Exception as e:
    logger.error(f"初始化数据库表失败: {e}")
    sys.exit(1)
EOF
    
    $PYTHON_CMD init_db_tables.py
    
    # 清理临时文件
    rm -f init_db_tables.py
    
    log_success "数据库表初始化完成"
}

# 创建初始数据
create_initial_data() {
    log_info "创建初始数据..."
    
    # 激活Python虚拟环境（如果存在）
    if [ -f "./venv/bin/activate" ]; then
        source ./venv/bin/activate
        PYTHON_CMD="./venv/bin/python"
    else
        PYTHON_CMD="python"
    fi
    
    # 创建初始数据脚本
    cat > create_initial_data.py << 'EOF'
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models as db_models
from auth import hash_password
import logging
from datetime import datetime
import uuid

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_initial_data():
    db = SessionLocal()
    try:
        # 创建默认角色
        admin_role = db.query(db_models.Role).filter(db_models.Role.role_name == "admin").first()
        if not admin_role:
            admin_role = db_models.Role(
                role_name="admin",
                description="系统管理员"
            )
            db.add(admin_role)
            logger.info("创建管理员角色")
        
        user_role = db.query(db_models.Role).filter(db_models.Role.role_name == "user").first()
        if not user_role:
            user_role = db_models.Role(
                role_name="user",
                description="普通用户"
            )
            db.add(user_role)
            logger.info("创建普通用户角色")
        
        db.commit()
        
        # 创建默认管理员用户
        admin_user = db.query(db_models.User).filter(db_models.User.username == "admin").first()
        if not admin_user:
            admin_user = db_models.User(
                user_id=str(uuid.uuid4()),
                username="admin",
                password=hash_password("admin123"),
                email="admin@bj-health.com",
                user_type="admin",
                created_at=datetime.now()
            )
            db.add(admin_user)
            db.commit()
            
            # 关联管理员角色
            user_role_rel = db_models.UserRole(
                user_id=admin_user.user_id,
                role_id=admin_role.role_id
            )
            db.add(user_role_rel)
            logger.info("创建默认管理员用户: admin/admin123")
        
        # 创建基本权限
        permissions = [
            ("user_read", "用户信息读取", "user", "read"),
            ("user_write", "用户信息修改", "user", "write"),
            ("data_read", "数据读取", "data", "read"),
            ("data_write", "数据修改", "data", "write"),
            ("model_read", "模型读取", "model", "read"),
            ("model_write", "模型修改", "model", "write"),
            ("result_read", "结果读取", "result", "read"),
            ("result_write", "结果修改", "result", "write"),
            ("admin_all", "系统管理", "system", "admin"),
        ]
        
        for perm_name, desc, resource, action in permissions:
            existing_perm = db.query(db_models.Permission).filter(
                db_models.Permission.permission_name == perm_name
            ).first()
            if not existing_perm:
                permission = db_models.Permission(
                    permission_name=perm_name,
                    description=desc,
                    resource=resource,
                    action=action
                )
                db.add(permission)
                logger.info(f"创建权限: {perm_name}")
        
        db.commit()
        
        # 为管理员角色分配所有权限
        all_permissions = db.query(db_models.Permission).all()
        existing_role_perms = db.query(db_models.RolePermission).filter(
            db_models.RolePermission.role_id == admin_role.role_id
        ).all()
        existing_perm_ids = {rp.permission_id for rp in existing_role_perms}
        
        for permission in all_permissions:
            if permission.permission_id not in existing_perm_ids:
                role_permission = db_models.RolePermission(
                    role_id=admin_role.role_id,
                    permission_id=permission.permission_id
                )
                db.add(role_permission)
        
        db.commit()
        logger.info("初始数据创建完成")
        
    except Exception as e:
        db.rollback()
        logger.error(f"创建初始数据失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_data()
EOF
    
    $PYTHON_CMD create_initial_data.py
    
    # 清理临时文件
    rm -f create_initial_data.py
    
    log_success "初始数据创建完成"
}

# 主函数
main() {
    log_info "开始PostgreSQL数据库建立和初始化..."
    
    # 切换到脚本目录
    cd "$(dirname "$0")"
    
    # 读取环境变量
    if [ -f ".env" ]; then
        load_env_file ".env"
    elif [ -f ".env.example" ]; then
        log_warning "未找到.env文件，使用.env.example"
        load_env_file ".env.example"
    else
        log_error "未找到环境变量文件（.env 或 .env.example）"
        exit 1
    fi
    
    # 设置默认值
    set_default_values
    
    # 验证必需变量
    validate_required_vars
    
    # 检测操作系统
    local os_type=$(get_os_type)
    log_info "检测到操作系统: $os_type"
    
    # 安装PostgreSQL
    install_postgresql
    
    # 测试超级用户连接
    if ! test_postgresql_connection "$POSTGRES_SUPERUSER" "$POSTGRES_SUPERUSER_PASSWORD" "$DB_HOST" "$DB_PORT" "postgres"; then
        log_error "无法连接到PostgreSQL，请检查超级用户密码和服务状态"
        exit 1
    fi
    log_success "PostgreSQL连接测试成功"
    
    # 创建数据库用户
    create_database_user
    
    # 创建数据库
    create_database
    
    # 测试新用户连接
    if ! test_postgresql_connection "$DB_USER" "$DB_PASS" "$DB_HOST" "$DB_PORT" "$DB_NAME"; then
        log_error "无法使用新用户连接到数据库"
        exit 1
    fi
    log_success "数据库用户连接测试成功"
    
    # 初始化数据库表
    initialize_database_tables
    
    # 创建初始数据
    create_initial_data
    
    log_success "PostgreSQL数据库建立和初始化完成！"
    log_info "数据库信息:"
    log_info "  主机: $DB_HOST"
    log_info "  端口: $DB_PORT"
    log_info "  数据库: $DB_NAME"
    log_info "  用户: $DB_USER"
    log_info "  默认管理员账户: admin/admin123"
    log_info ""
    log_info "连接字符串: postgresql://$DB_USER:$DB_PASS@$DB_HOST:$DB_PORT/$DB_NAME"
}

# 运行主函数
main "$@" 