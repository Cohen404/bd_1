# 北京健康评估系统 FastAPI 后端

## 环境准备与运行流程

### 1. 创建 Python 虚拟环境

#### Mac/Linux
```bash
cd fastapi_backend
python3 -m venv venv
```

#### Windows
```cmd
cd fastapi_backend
python -m venv venv
```

### 2. 激活虚拟环境

#### Mac/Linux
```bash
source venv/bin/activate
```

#### Windows
```cmd
venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 首次运行前需手动创建日志目录

```bash
mkdir -p log
```

### 5. 运行后端服务

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## API接口列表

### 认证接口
- `POST /api/token`: OAuth2标准登录接口
- `POST /api/login`: 简化版登录接口

### 用户管理接口
- `POST /api/users/`: 创建新用户
- `GET /api/users/`: 获取用户列表
- `GET /api/users/me`: 获取当前用户信息
- `GET /api/users/{user_id}`: 获取特定用户信息
- `PUT /api/users/{user_id}`: 更新用户信息
- `DELETE /api/users/{user_id}`: 删除用户

### 数据管理接口
- `POST /api/data/`: 上传数据文件
- `GET /api/data/`: 获取数据列表
- `GET /api/data/{data_id}`: 获取特定数据
- `DELETE /api/data/{data_id}`: 删除数据

### 模型管理接口
- `POST /api/models/`: 上传模型文件
- `GET /api/models/`: 获取模型列表
- `GET /api/models/{model_id}`: 获取特定模型
- `DELETE /api/models/{model_id}`: 删除模型

### 健康评估接口
- `POST /api/health/evaluate`: 对指定数据进行健康评估
- `POST /api/health/batch-evaluate`: 批量健康评估
- `GET /api/health/reports/{result_id}`: 获取评估报告

### 结果管理接口
- `GET /api/results/`: 获取结果列表
- `GET /api/results/{result_id}`: 获取特定结果
- `GET /api/results/{result_id}/report`: 获取结果报告文件
- `DELETE /api/results/{result_id}`: 删除结果

### 参数管理接口
- `POST /api/parameters/`: 创建系统参数
- `GET /api/parameters/`: 获取参数列表
- `GET /api/parameters/{param_id}`: 获取特定参数
- `PUT /api/parameters/{param_id}`: 更新参数
- `DELETE /api/parameters/{param_id}`: 删除参数

### 角色管理接口
- `POST /api/roles/`: 创建角色
- `GET /api/roles/`: 获取角色列表
- `GET /api/roles/{role_id}`: 获取特定角色
- `PUT /api/roles/{role_id}`: 更新角色
- `DELETE /api/roles/{role_id}`: 删除角色
- `POST /api/roles/{role_id}/permissions`: 为角色添加权限
- `DELETE /api/roles/{role_id}/permissions/{permission_id}`: 从角色中移除权限

### 日志管理接口
- `GET /api/logs/`: 获取日志列表

## 代码结构

```
fastapi_backend/
├── auth.py                    # 认证相关功能
├── config.py                  # 配置文件
├── data_feature_calculation.py # 数据特征计算模块
├── data_preprocess.py         # 数据预处理模块
├── database.py                # 数据库连接
├── main.py                    # 主应用入口
├── model_inference.py         # 模型推理模块
├── models.py                  # 数据库模型
├── requirements.txt           # 依赖列表
├── schemas.py                 # Pydantic模型
└── routers/                   # 路由模块
    ├── __init__.py
    ├── auth.py                # 认证路由
    ├── data.py                # 数据管理路由
    ├── health_evaluate.py     # 健康评估路由
    ├── logs.py                # 日志管理路由
    ├── models.py              # 模型管理路由
    ├── parameters.py          # 参数管理路由
    ├── results.py             # 结果管理路由
    ├── roles.py               # 角色管理路由
    └── users.py               # 用户管理路由
```

## 访问API文档

服务启动后，可以通过以下URL访问API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc 