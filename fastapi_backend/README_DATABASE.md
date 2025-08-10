# PostgreSQL数据库初始化指南

本文档介绍如何使用自动化脚本初始化PostgreSQL数据库。

## 环境要求

- macOS 或 Ubuntu 系统
- Bash shell
- Python 3.7+
- 虚拟环境（推荐）

## 快速开始

### 1. 配置环境变量

复制环境变量模板并修改配置：

```bash
cp env_template .env
```

编辑 `.env` 文件，设置以下必需参数：

```bash
# 数据库配置
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=bj_health_db

# 数据库用户配置（两种方式选一种）
# 方式1: 使用专门的应用用户（推荐生产环境）
# DB_USER=bj_health_user
# DB_PASS=你的应用用户密码

# 方式2: 直接使用postgres超级用户（开发环境）
DB_USER=postgres
DB_PASS=你的postgres密码

# PostgreSQL超级用户密码（初始化时需要）
# 注意：如果DB_USER=postgres，则POSTGRES_SUPERUSER_PASSWORD应该与DB_PASS相同
POSTGRES_SUPERUSER_PASSWORD=你的postgres密码

# JWT密钥（建议生成随机字符串）
SECRET_KEY=你的32位以上随机密钥
```

### 2. 运行初始化脚本

```bash
# 给脚本添加执行权限
chmod +x setup_database.sh

# 运行数据库初始化
./setup_database.sh
```

## 脚本功能

`setup_database.sh` 脚本会自动执行以下操作：

1. **系统检测**：自动识别macOS或Ubuntu系统
2. **PostgreSQL安装**：
   - macOS：使用Homebrew安装
   - Ubuntu：使用apt包管理器安装
3. **服务启动**：启动PostgreSQL服务并设置自启动
4. **数据库创建**：
   - 创建应用数据库用户
   - 创建应用数据库
   - 设置权限
5. **表结构初始化**：根据SQLAlchemy模型创建所有数据表
6. **初始数据创建**：
   - 创建默认角色（admin、user）
   - 创建默认管理员用户（admin/admin123）
   - 创建基本权限
   - 配置角色权限关联

## 数据库表结构

系统包含以下数据表：

### 用户管理
- `tb_user`：用户信息表
- `tb_role`：角色表
- `tb_user_role`：用户角色关联表
- `tb_permission`：权限表
- `tb_role_permission`：角色权限关联表

### 业务数据
- `tb_data`：EEG数据文件信息表
- `tb_result`：健康评估结果表
- `tb_model`：机器学习模型信息表

### 系统配置
- `system_params`：系统参数表
- `tb_parameters`：业务参数表

## 默认账户

初始化完成后，系统会创建以下默认账户：

- **管理员账户**：
  - 用户名：`admin`
  - 密码：`admin123`
  - 权限：所有系统权限

> **安全提示**：生产环境中请立即修改默认密码！

## 手动安装（可选）

如果自动脚本无法正常工作，可以按以下步骤手动安装：

### macOS手动安装

```bash
# 安装Homebrew（如果没有）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# 设置PATH
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
```

### Ubuntu手动安装

```bash
# 更新包列表
sudo apt update

# 安装PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 手动创建数据库

```bash
# 连接到PostgreSQL
sudo -u postgres psql

# 在PostgreSQL中执行：
CREATE USER bj_health_user WITH PASSWORD '你的密码';
CREATE DATABASE bj_health_db OWNER bj_health_user;
GRANT ALL PRIVILEGES ON DATABASE bj_health_db TO bj_health_user;
\q
```

## 故障排除

### 常见问题

1. **权限不足**：
   ```bash
   sudo chmod +x setup_database.sh
   ```

2. **PostgreSQL服务未启动**：
   ```bash
   # macOS
   brew services start postgresql@15
   
   # Ubuntu
   sudo systemctl start postgresql
   ```

3. **连接被拒绝**：
   - 检查PostgreSQL是否正在运行
   - 验证端口5432是否被占用
   - 检查防火墙设置

4. **密码认证失败**：
   - 确认.env文件中的密码正确
   - 检查PostgreSQL的pg_hba.conf配置

### 检查服务状态

```bash
# macOS
brew services list | grep postgresql

# Ubuntu
sudo systemctl status postgresql
```

### 检查数据库连接

```bash
# 使用应用用户连接
PGPASSWORD=你的密码 psql -h 127.0.0.1 -p 5432 -U bj_health_user -d bj_health_db

# 查看表
\dt
```

## 卸载和重置

如需重新初始化数据库：

```bash
# 删除数据库（谨慎操作）
PGPASSWORD=超级用户密码 psql -h 127.0.0.1 -p 5432 -U postgres -c "DROP DATABASE IF EXISTS bj_health_db;"
PGPASSWORD=超级用户密码 psql -h 127.0.0.1 -p 5432 -U postgres -c "DROP USER IF EXISTS bj_health_user;"

# 重新运行初始化脚本
./setup_database.sh
```

## 技术支持

如遇到问题，请检查：

1. 系统日志：`fastapi_backend/log/app.log`
2. PostgreSQL日志：
   - macOS：`/opt/homebrew/var/log/postgresql@15.log`
   - Ubuntu：`/var/log/postgresql/`
3. 脚本输出信息

确保所有环境变量正确设置，并且系统满足依赖要求。 