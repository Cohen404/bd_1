# 北京健康评估系统 - 后端API

这是北京健康评估系统的后端API服务，基于FastAPI框架开发，提供用户管理、数据管理、健康评估等功能。

## 项目概述

本系统是一个基于脑电图(EEG)数据的健康评估平台，支持：
- 用户认证和权限管理
- EEG数据上传和预处理
- 多种健康指标评估（压力、抑郁、焦虑、社交孤立）
- 评估报告生成
- 系统日志和监控

## 技术栈

- **后端框架**: FastAPI 0.104.1
- **数据库**: PostgreSQL 14+
- **认证**: JWT + BCrypt
- **数据处理**: NumPy, SciPy, MNE
- **机器学习**: TensorFlow 2.15.0
- **API文档**: 自动生成OpenAPI/Swagger文档

## 系统要求

- Python 3.8+
- PostgreSQL 14+
- macOS 或 Ubuntu 20.04+
- 内存: 最少8GB RAM
- 存储: 最少10GB可用磁盘空间

## 快速开始

### 1. 环境准备

```bash
# 克隆项目（如果需要）
cd fastapi_backend

# 创建Python虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# 安装依赖包
pip install -r requirements.txt
```

### 2. 数据库安装和配置

运行自动安装脚本：

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行PostgreSQL安装脚本
python install_postgres.py
```

脚本会自动：
- 检测操作系统（macOS/Ubuntu）
- 安装PostgreSQL（如果未安装）
- 创建数据库和用户
- 初始化数据表
- 生成`.env`配置文件模板

### 3. 环境配置

编辑`.env`文件，设置必要的配置：

```bash
# 数据库配置
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=bj_health_db
DB_USER=postgres
DB_PASS=你的数据库密码

# JWT配置
SECRET_KEY=你的JWT密钥
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 其他配置
DEBUG=true
BCRYPT_ROUNDS=12
```

### 4. 启动服务

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动开发服务器
python main.py

# 或使用uvicorn直接启动
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后可以访问：
- API服务: http://localhost:8000
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 手动安装PostgreSQL

如果自动安装脚本失败，可以手动安装：

### macOS

```bash
# 使用Homebrew安装
brew install postgresql@14
brew services start postgresql@14

# 创建数据库
createdb bj_health_db
```

### Ubuntu

```bash
# 安装PostgreSQL
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建用户和数据库
sudo -u postgres psql
postgres=# CREATE USER your_user WITH PASSWORD 'your_password';
postgres=# CREATE DATABASE bj_health_db;
postgres=# GRANT ALL PRIVILEGES ON DATABASE bj_health_db TO your_user;
postgres=# \q
```

然后初始化数据表：

```bash
python -c "from database import init_db; init_db()"
```

## API文档和使用

### 主要API端点

| 功能模块 | 端点前缀 | 说明 |
|---------|----------|------|
| 认证 | `/api/token`, `/api/login` | 用户登录获取令牌 |
| 用户管理 | `/api/users/` | 用户增删改查 |
| 数据管理 | `/api/data/` | EEG数据上传和管理 |
| 健康评估 | `/api/health/` | 健康指标评估 |
| 结果管理 | `/api/results/` | 评估结果查询 |
| 模型管理 | `/api/models/` | 机器学习模型管理 |
| 角色权限 | `/api/roles/` | 用户角色和权限管理 |
| 系统参数 | `/api/parameters/` | 系统参数配置 |
| 日志管理 | `/api/logs/` | 系统日志查询 |

### 认证流程

1. 使用用户名密码登录获取JWT令牌：
```bash
curl -X POST "http://localhost:8000/api/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "password"}'
```

2. 在后续请求中携带令牌：
```bash
curl -X GET "http://localhost:8000/api/users/" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 测试

### 1. 基础连接测试

```bash
# 测试服务状态
curl http://localhost:8000/health

# 预期返回
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000000",
  "service": "bj_health_csq_api"
}
```

### 2. 数据库连接测试

```bash
# 测试数据库连接
python -c "
from database import get_db
from sqlalchemy.orm import Session
db = next(get_db())
print('数据库连接成功')
db.close()
"
```

### 3. API功能测试

```bash
# 测试用户登录
curl -X POST "http://localhost:8000/api/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "test", "password": "test"}'

# 测试API文档访问
curl http://localhost:8000/docs
```

### 4. 完整功能测试

运行以下Python脚本进行完整测试：

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. 健康检查
response = requests.get(f"{BASE_URL}/health")
print(f"健康检查: {response.status_code}")

# 2. 获取API文档
response = requests.get(f"{BASE_URL}/docs")
print(f"API文档: {response.status_code}")

# 3. 测试登录（需要先创建测试用户）
login_data = {"username": "test", "password": "test"}
response = requests.post(f"{BASE_URL}/api/login", json=login_data)
print(f"用户登录: {response.status_code}")

if response.status_code == 200:
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 4. 测试受保护的API
    response = requests.get(f"{BASE_URL}/api/users/", headers=headers)
    print(f"用户列表: {response.status_code}")
```

## 目录结构

```
fastapi_backend/
├── main.py                 # 主应用入口
├── config.py              # 配置管理
├── database.py            # 数据库连接
├── models.py              # 数据模型
├── schemas.py             # Pydantic模式
├── auth.py                # 认证和权限
├── requirements.txt       # 依赖包列表
├── install_postgres.py    # PostgreSQL安装脚本
├── data_preprocess.py     # 数据预处理
├── data_feature_calculation.py  # 特征计算
├── model_inference.py     # 模型推理
├── routers/              # API路由模块
│   ├── auth.py           # 认证路由
│   ├── users.py          # 用户管理路由
│   ├── data.py           # 数据管理路由
│   ├── health_evaluate.py # 健康评估路由
│   ├── results.py        # 结果管理路由
│   ├── models.py         # 模型管理路由
│   ├── roles.py          # 角色管理路由
│   ├── parameters.py     # 参数管理路由
│   └── logs.py           # 日志管理路由
├── data/                 # 数据存储目录
├── model/                # 机器学习模型目录
├── templates/            # 报告模板目录
├── log/                  # 日志文件目录
└── venv/                 # Python虚拟环境
```

## 常见问题

### 1. 数据库连接问题

**问题**: `psycopg2.OperationalError: could not connect to server`

**解决方案**:
- 确保PostgreSQL服务正在运行
- 检查`.env`文件中的数据库配置
- 验证数据库用户权限

```bash
# 检查PostgreSQL状态
# macOS
brew services list | grep postgresql

# Ubuntu
sudo systemctl status postgresql
```

### 2. 依赖包安装问题

**问题**: 某些包安装失败

**解决方案**:
```bash
# 升级pip
pip install --upgrade pip

# 安装系统依赖（Ubuntu）
sudo apt-get install python3-dev postgresql-server-dev-all

# 重新安装依赖
pip install -r requirements.txt
```

### 3. 权限问题

**问题**: `Permission denied`错误

**解决方案**:
- 确保虚拟环境已激活
- 检查文件和目录权限
- 使用正确的用户运行服务

### 4. 端口占用问题

**问题**: `Address already in use`

**解决方案**:
```bash
# 查找占用端口的进程
lsof -i :8000

# 终止进程
kill -9 PID

# 或使用不同端口
uvicorn main:app --port 8001
```

## 性能优化

### 1. 数据库优化

- 为常用查询字段添加索引
- 使用连接池管理数据库连接
- 定期维护数据库统计信息

### 2. 应用优化

- 启用响应缓存
- 使用异步处理长时间任务
- 优化EEG数据处理算法

### 3. 部署优化

- 使用Gunicorn多进程部署
- 配置反向代理（Nginx）
- 启用GZIP压缩

## 开发指南

### 添加新的API端点

1. 在`routers/`目录下创建或编辑路由文件
2. 在`schemas.py`中定义数据模式
3. 在`models.py`中添加数据模型（如需要）
4. 在`main.py`中注册新路由

### 数据库迁移

```bash
# 修改models.py后重新创建表
python -c "
from database import engine, Base
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print('数据库表已重新创建')
"
```

## 部署指南

### 1. 生产环境配置

```bash
# 安装生产服务器
pip install gunicorn

# 创建生产配置文件
cat > gunicorn_config.py << EOF
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
max_requests = 1000
preload_app = True
EOF

# 启动生产服务器
gunicorn main:app -c gunicorn_config.py
```

### 2. 使用Docker部署

```dockerfile
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["gunicorn", "main:app", "-c", "gunicorn_config.py"]
```

### 3. 系统服务配置

创建systemd服务文件：

```bash
sudo cat > /etc/systemd/system/bj-health-api.service << EOF
[Unit]
Description=Beijing Health Assessment API
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/fastapi_backend
Environment=PATH=/path/to/fastapi_backend/venv/bin
ExecStart=/path/to/fastapi_backend/venv/bin/gunicorn main:app -c gunicorn_config.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启用并启动服务
sudo systemctl enable bj-health-api
sudo systemctl start bj-health-api
```

## 贡献指南

1. Fork项目仓库
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，请联系开发团队或提交Issue。 