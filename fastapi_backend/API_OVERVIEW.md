# 北京健康评估系统 API 接口文档

## 📖 概述

北京健康评估系统是一个基于EEG脑电数据的AI健康评估平台，提供应激、抑郁、焦虑等心理健康指标的评估服务。

- **系统版本**: 1.0.0
- **技术栈**: FastAPI + PostgreSQL + JWT认证
- **文档更新时间**: 2025-08-11

## 🚀 快速开始

### 1. 启动服务

```bash
cd fastapi_backend
source venv/bin/activate
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 访问文档

- **API交互文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc
- **OpenAPI规范**: http://localhost:8000/openapi.json

### 3. 获取认证Token

```bash
# 登录获取Token
curl -X POST "http://localhost:8000/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 返回示例
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "72f220b7-f583-4034-8f44-08b5986c2835",
  "user_type": "admin",
  "username": "admin"
}
```

## 🔑 认证方式

系统使用JWT Bearer Token认证：

```bash
# 在请求头中添加认证信息
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📚 主要功能模块

### 🔐 认证模块 (`/api`)

| 端点 | 方法 | 功能 | 认证 |
|------|------|------|------|
| `/api/login` | POST | 用户登录（JSON格式） | ❌ |
| `/api/token` | POST | 获取Token（OAuth2格式） | ❌ |

### 👤 用户管理 (`/api/users`)

| 端点 | 方法 | 功能 | 认证 |
|------|------|------|------|
| `/api/users/me` | GET | 获取当前用户信息 | ✅ |
| `/api/users/` | GET | 获取用户列表 | ✅ |
| `/api/users/` | POST | 创建新用户 | ✅ |
| `/api/users/{user_id}` | GET/PUT/DELETE | 用户详情/更新/删除 | ✅ |

### 🎭 角色权限 (`/api/roles`)

| 端点 | 方法 | 功能 | 认证 |
|------|------|------|------|
| `/api/roles/` | GET | 获取角色列表 | ✅ |
| `/api/roles/` | POST | 创建角色 | ✅ |
| `/api/roles/{role_id}` | GET/PUT/DELETE | 角色管理 | ✅ |

### 📊 数据管理 (`/api/data`)

| 端点 | 方法 | 功能 | 认证 |
|------|------|------|------|
| `/api/data/` | GET | 获取数据列表 | ✅ |
| `/api/data/upload` | POST | 上传EEG数据文件 | ✅ |
| `/api/data/{data_id}` | GET/DELETE | 数据详情/删除 | ✅ |

### 🧠 AI模型 (`/api/models`)

| 端点 | 方法 | 功能 | 认证 |
|------|------|------|------|
| `/api/models/` | GET | 获取模型列表 | ✅ |
| `/api/models/upload` | POST | 上传模型文件 | ✅ |
| `/api/models/{model_id}` | GET/DELETE | 模型管理 | ✅ |

### 💖 健康评估 (`/api/health`)

| 端点 | 方法 | 功能 | 认证 |
|------|------|------|------|
| `/api/health/evaluate` | POST | 单个数据健康评估 | ✅ |
| `/api/health/batch_evaluate` | POST | 批量健康评估 | ✅ |

### 📈 结果管理 (`/api/results`)

| 端点 | 方法 | 功能 | 认证 |
|------|------|------|------|
| `/api/results/` | GET | 获取评估结果列表 | ✅ |
| `/api/results/{result_id}` | GET/DELETE | 结果详情/删除 | ✅ |
| `/api/results/{result_id}/report` | GET | 下载评估报告 | ✅ |

### ⚙️ 系统管理

| 模块 | 端点前缀 | 功能 |
|------|----------|------|
| 参数管理 | `/api/parameters` | 系统参数配置 |
| 日志管理 | `/api/logs` | 操作日志查看 |

## 🎯 核心业务流程

### 1. 健康评估完整流程

```bash
# 1. 用户登录
TOKEN=$(curl -X POST "http://localhost:8000/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# 2. 上传EEG数据
curl -X POST "http://localhost:8000/api/data/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@eeg_data.csv" \
  -F "personnel_name=张三" \
  -F "personnel_id=P001"

# 3. 获取数据ID并进行健康评估
curl -X POST "http://localhost:8000/api/health/evaluate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"data_id": 1}'

# 4. 获取评估结果
curl -X GET "http://localhost:8000/api/results/" \
  -H "Authorization: Bearer $TOKEN"
```

### 2. 评估结果说明

健康评估返回4个维度的分数（0-100分）：

- **应激评分** (`stress_score`): 0=无应激，100=严重应激
- **抑郁评分** (`depression_score`): 0=无抑郁，100=严重抑郁  
- **焦虑评分** (`anxiety_score`): 0=无焦虑，100=严重焦虑

## 📝 常用API示例

### 获取用户信息

```bash
curl -X GET "http://localhost:8000/api/users/me" \
  -H "Authorization: Bearer $TOKEN"
```

### 上传数据文件

```bash
curl -X POST "http://localhost:8000/api/data/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@data.csv" \
  -F "personnel_name=测试用户" \
  -F "personnel_id=T001"
```

### 健康评估

```bash
curl -X POST "http://localhost:8000/api/health/evaluate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"data_id": 1}'
```

### 获取评估结果

```bash
curl -X GET "http://localhost:8000/api/results/" \
  -H "Authorization: Bearer $TOKEN"
```

## ❌ 错误代码

| 状态码 | 说明 | 解决方案 |
|--------|------|----------|
| 200 | 请求成功 | - |
| 401 | 认证失败 | 检查Token是否有效 |
| 403 | 权限不足 | 联系管理员分配权限 |
| 404 | 资源不存在 | 检查请求的ID是否正确 |
| 422 | 参数验证失败 | 检查请求参数格式 |
| 500 | 服务器错误 | 查看服务器日志 |

## 🔧 系统配置

### 数据库信息

- **类型**: PostgreSQL 15
- **主机**: 127.0.0.1:5432
- **数据库**: bj_health_db
- **默认管理员**: admin/admin123

### 环境变量

关键配置项（在`.env`文件中）：

```env
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=bj_health_db
DB_USER=postgres
DB_PASS=你的密码
SECRET_KEY=你的JWT密钥
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

## 📖 相关文档

- **详细API文档**: `API_DOCS.md`
- **数据库文档**: `README_DATABASE.md`
- **OpenAPI规范**: `openapi_generated.json`
- **在线文档**: http://localhost:8000/docs

## 🆘 技术支持

如遇到问题，请检查：

1. **服务状态**: 访问 http://localhost:8000/health
2. **认证Token**: 确保Token未过期且格式正确
3. **系统日志**: 查看 `log/app.log`
4. **数据库连接**: 使用 `./test_database.sh` 测试

---

*系统开发完成并通过全面测试，所有API接口运行正常！* ✅ 