#!/bin/bash

# 数据库连接测试脚本
# 用于验证数据库初始化是否成功

set -e

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

# 读取.env文件
load_env_file() {
    local env_file="$1"
    if [ -f "$env_file" ]; then
        log_info "加载环境变量文件: $env_file"
        while IFS= read -r line; do
            if [[ "$line" =~ ^[[:space:]]*# ]] || [[ -z "$line" ]]; then
                continue
            fi
            if [[ "$line" =~ ^[[:space:]]*([^=]+)=(.*)$ ]]; then
                local key="${BASH_REMATCH[1]}"
                local value="${BASH_REMATCH[2]}"
                key=$(echo "$key" | xargs)
                value=$(echo "$value" | xargs)
                value=$(echo "$value" | sed 's/^["'\'']\|["'\'']$//g')
                export "$key"="$value"
            fi
        done < "$env_file"
    else
        log_error "环境变量文件不存在: $env_file"
        return 1
    fi
}

# 测试数据库连接
test_connection() {
    local user="$1"
    local password="$2"
    local host="$3"
    local port="$4"
    local database="$5"
    
    log_info "测试数据库连接: $user@$host:$port/$database"
    
    if PGPASSWORD="$password" psql -h "$host" -p "$port" -U "$user" -d "$database" -c "\q" 2>/dev/null; then
        log_success "连接成功"
        return 0
    else
        log_error "连接失败"
        return 1
    fi
}

# 查看表结构
show_tables() {
    local user="$1"
    local password="$2"
    local host="$3"
    local port="$4"
    local database="$5"
    
    log_info "查看数据库表:"
    PGPASSWORD="$password" psql -h "$host" -p "$port" -U "$user" -d "$database" -c "\dt"
}

# 查看用户和角色
show_users_and_roles() {
    local user="$1"
    local password="$2"
    local host="$3"
    local port="$4"
    local database="$5"
    
    log_info "查看用户和角色数据:"
    PGPASSWORD="$password" psql -h "$host" -p "$port" -U "$user" -d "$database" -c "
    SELECT 'Users' as type, username, user_type, email FROM tb_user
    UNION ALL
    SELECT 'Roles', role_name, description, '' FROM tb_role
    ORDER BY type, username;
    "
}

# 主函数
main() {
    log_info "开始数据库连接测试..."
    
    # 切换到脚本目录
    cd "$(dirname "$0")"
    
    # 读取环境变量
    if [ -f ".env" ]; then
        load_env_file ".env"
    elif [ -f "env_template" ]; then
        log_warning "未找到.env文件，使用env_template"
        load_env_file "env_template"
    else
        log_error "未找到环境变量文件"
        exit 1
    fi
    
    # 设置默认值
    DB_HOST="${DB_HOST:-127.0.0.1}"
    DB_PORT="${DB_PORT:-5432}"
    DB_NAME="${DB_NAME:-bj_health_db}"
    DB_USER="${DB_USER:-bj_health_user}"
    
    if [ -z "$DB_PASS" ]; then
        log_error "数据库密码未设置"
        exit 1
    fi
    
    # 测试连接
    if test_connection "$DB_USER" "$DB_PASS" "$DB_HOST" "$DB_PORT" "$DB_NAME"; then
        # 显示表结构
        show_tables "$DB_USER" "$DB_PASS" "$DB_HOST" "$DB_PORT" "$DB_NAME"
        
        # 显示用户和角色
        show_users_and_roles "$DB_USER" "$DB_PASS" "$DB_HOST" "$DB_PORT" "$DB_NAME"
        
        log_success "数据库测试完成"
    else
        log_error "数据库连接失败，请检查配置"
        exit 1
    fi
}

# 运行主函数
main "$@" 