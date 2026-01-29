# 北京健康评估系统API

**版本**: 1.0.0
**描述**: 北京健康评估系统的后端API接口
**生成时间**: 2025-08-11 12:32:01

## 🔐 认证
本API使用JWT Bearer Token认证。

### 获取Token
```bash
# 方式1: JSON格式登录
curl -X POST "http://localhost:8000/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 方式2: OAuth2格式登录
curl -X POST "http://localhost:8000/api/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### 使用Token
```bash
curl -X GET "http://localhost:8000/api/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 📚 API接口

### 认证

#### `POST` /api/token
**Login For Access Token**
用户登录接口，获取访问令牌

**成功响应 (200):**
Successful Response
返回数据模型: `Token`

**示例请求:**
```bash
curl -X POST "http://localhost:8000/api/token" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"key": "value"}'
```

#### `POST` /api/login
**Login**
用户登录接口，简化版

**请求体:** JSON格式
参考数据模型: `LoginRequest`

**成功响应 (200):**
Successful Response
返回数据模型: `Token`

**示例请求:**
```bash
curl -X POST "http://localhost:8000/api/login" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"key": "value"}'
```

### 用户管理

#### `POST` /api/users/
**Create User**
创建新用户

**请求体:** JSON格式
参考数据模型: `UserCreate`

**成功响应 (200):**
Successful Response
返回数据模型: `User`

**示例请求:**
```bash
curl -X POST "http://localhost:8000/api/users/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"key": "value"}'
```

#### `GET` /api/users/
**Read Users**
获取用户列表

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| skip | integer | query | 否 |  |
| limit | integer | query | 否 |  |

**成功响应 (200):**
Successful Response

**示例请求:**
```bash
curl -X GET "http://localhost:8000/api/users/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `GET` /api/users/me
**Read User Me**
获取当前用户信息

**成功响应 (200):**
Successful Response
返回数据模型: `User`

**示例请求:**
```bash
curl -X GET "http://localhost:8000/api/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `GET` /api/users/{user_id}
**Read User**
获取特定用户信息

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| user_id | string | path | 是 |  |

**成功响应 (200):**
Successful Response
返回数据模型: `User`

**示例请求:**
```bash
curl -X GET "http://localhost:8000/api/users/{user_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `PUT` /api/users/{user_id}
**Update User**
更新用户信息

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| user_id | string | path | 是 |  |

**请求体:** JSON格式
参考数据模型: `UserUpdate`

**成功响应 (200):**
Successful Response
返回数据模型: `User`

**示例请求:**
```bash
curl -X PUT "http://localhost:8000/api/users/{user_id}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"key": "value"}'
```

#### `DELETE` /api/users/{user_id}
**Delete User**
删除用户

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| user_id | string | path | 是 |  |

**示例请求:**
```bash
curl -X DELETE "http://localhost:8000/api/users/{user_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 数据管理

#### `POST` /api/data/
**Create Data**
上传数据文件

**成功响应 (200):**
Successful Response
返回数据模型: `Data`

**示例请求:**
```bash
curl -X POST "http://localhost:8000/api/data/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"key": "value"}'
```

#### `GET` /api/data/
**Read Data**
获取数据列表

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| skip | integer | query | 否 |  |
| limit | integer | query | 否 |  |
| personnel_id | string | query | 否 |  |
| personnel_name | string | query | 否 |  |

**成功响应 (200):**
Successful Response

**示例请求:**
```bash
curl -X GET "http://localhost:8000/api/data/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `GET` /api/data/{data_id}
**Read Data By Id**
获取特定数据

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| data_id | integer | path | 是 |  |

**成功响应 (200):**
Successful Response
返回数据模型: `Data`

**示例请求:**
```bash
curl -X GET "http://localhost:8000/api/data/{data_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `DELETE` /api/data/{data_id}
**Delete Data**
删除数据

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| data_id | integer | path | 是 |  |

**示例请求:**
```bash
curl -X DELETE "http://localhost:8000/api/data/{data_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 模型管理

#### `GET` /api/models/
**Read Models**
获取模型列表

**成功响应 (200):**
Successful Response

**示例请求:**
```bash
curl -X GET "http://localhost:8000/api/models/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `POST` /api/models/
**Create Model**
上传模型文件

**成功响应 (200):**
Successful Response
返回数据模型: `Model`

**示例请求:**
```bash
curl -X POST "http://localhost:8000/api/models/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"key": "value"}'
```

#### `GET` /api/models/{model_id}
**Read Model**
获取特定模型

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| model_id | integer | path | 是 |  |

**成功响应 (200):**
Successful Response
返回数据模型: `Model`

**示例请求:**
```bash
curl -X GET "http://localhost:8000/api/models/{model_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `DELETE` /api/models/{model_id}
**Delete Model**
删除模型

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| model_id | integer | path | 是 |  |

**示例请求:**
```bash
curl -X DELETE "http://localhost:8000/api/models/{model_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 结果管理

#### `GET` /api/results/
**Read Results**
获取结果列表

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| skip | integer | query | 否 |  |
| limit | integer | query | 否 |  |
| data_id | string | query | 否 |  |

**成功响应 (200):**
Successful Response

**示例请求:**
```bash
curl -X GET "http://localhost:8000/api/results/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `GET` /api/results/{result_id}
**Read Result**
获取特定结果

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| result_id | integer | path | 是 |  |

**成功响应 (200):**
Successful Response
返回数据模型: `Result`

**示例请求:**
```bash
curl -X GET "http://localhost:8000/api/results/{result_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `DELETE` /api/results/{result_id}
**Delete Result**
删除结果

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| result_id | integer | path | 是 |  |

**示例请求:**
```bash
curl -X DELETE "http://localhost:8000/api/results/{result_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `GET` /api/results/{result_id}/report
**Read Result Report**
获取结果报告文件

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| result_id | integer | path | 是 |  |

**成功响应 (200):**
Successful Response

**示例请求:**
```bash
curl -X GET "http://localhost:8000/api/results/{result_id}/report" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 健康评估

#### `POST` /api/health/evaluate
**Evaluate Health**
对指定的数据进行健康评估

**请求体:** JSON格式
参考数据模型: `HealthEvaluateRequest`

**成功响应 (200):**
Successful Response
返回数据模型: `Result`

**示例请求:**
```bash
curl -X POST "http://localhost:8000/api/health/evaluate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"key": "value"}'
```

#### `POST` /api/health/batch-evaluate
**Batch Evaluate Health**
批量健康评估

**请求体:** JSON格式
参考数据模型: `BatchHealthEvaluateRequest`

**成功响应 (200):**
Successful Response

**示例请求:**
```bash
curl -X POST "http://localhost:8000/api/health/batch-evaluate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"key": "value"}'
```

#### `GET` /api/health/reports/{result_id}
**Get Evaluate Report**
获取评估报告

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| result_id | integer | path | 是 |  |

**成功响应 (200):**
Successful Response
返回数据模型: `Result`

**示例请求:**
```bash
curl -X GET "http://localhost:8000/api/health/reports/{result_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 参数管理

#### `POST` /api/parameters/
**Create Parameter**
创建系统参数

**请求体:** JSON格式
参考数据模型: `ParameterCreate`

**成功响应 (200):**
Successful Response
返回数据模型: `Parameter`

**示例请求:**
```bash
curl -X POST "http://localhost:8000/api/parameters/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"key": "value"}'
```

#### `GET` /api/parameters/
**Read Parameters**
获取参数列表

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| skip | integer | query | 否 |  |
| limit | integer | query | 否 |  |
| param_type | string | query | 否 |  |

**成功响应 (200):**
Successful Response

**示例请求:**
```bash
curl -X GET "http://localhost:8000/api/parameters/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `GET` /api/parameters/{param_id}
**Read Parameter**
获取特定参数

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| param_id | integer | path | 是 |  |

**成功响应 (200):**
Successful Response
返回数据模型: `Parameter`

**示例请求:**
```bash
curl -X GET "http://localhost:8000/api/parameters/{param_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `PUT` /api/parameters/{param_id}
**Update Parameter**
更新参数

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| param_id | integer | path | 是 |  |

**请求体:** JSON格式
参考数据模型: `ParameterUpdate`

**成功响应 (200):**
Successful Response
返回数据模型: `Parameter`

**示例请求:**
```bash
curl -X PUT "http://localhost:8000/api/parameters/{param_id}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"key": "value"}'
```

#### `DELETE` /api/parameters/{param_id}
**Delete Parameter**
删除参数

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| param_id | integer | path | 是 |  |

**示例请求:**
```bash
curl -X DELETE "http://localhost:8000/api/parameters/{param_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 角色管理

#### `POST` /api/roles/
**Create Role**
创建角色

**请求体:** JSON格式
参考数据模型: `RoleCreate`

**成功响应 (200):**
Successful Response
返回数据模型: `Role`

**示例请求:**
```bash
curl -X POST "http://localhost:8000/api/roles/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"key": "value"}'
```

#### `GET` /api/roles/
**Read Roles**
获取角色列表

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| skip | integer | query | 否 |  |
| limit | integer | query | 否 |  |

**成功响应 (200):**
Successful Response

**示例请求:**
```bash
curl -X GET "http://localhost:8000/api/roles/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `GET` /api/roles/{role_id}
**Read Role**
获取特定角色

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| role_id | integer | path | 是 |  |

**成功响应 (200):**
Successful Response
返回数据模型: `Role`

**示例请求:**
```bash
curl -X GET "http://localhost:8000/api/roles/{role_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `PUT` /api/roles/{role_id}
**Update Role**
更新角色

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| role_id | integer | path | 是 |  |

**请求体:** JSON格式
参考数据模型: `RoleUpdate`

**成功响应 (200):**
Successful Response
返回数据模型: `Role`

**示例请求:**
```bash
curl -X PUT "http://localhost:8000/api/roles/{role_id}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"key": "value"}'
```

#### `DELETE` /api/roles/{role_id}
**Delete Role**
删除角色

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| role_id | integer | path | 是 |  |

**示例请求:**
```bash
curl -X DELETE "http://localhost:8000/api/roles/{role_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `GET` /api/roles/{role_id}/permissions
**Get Role Permissions**
获取角色的所有权限

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| role_id | integer | path | 是 |  |

**成功响应 (200):**
Successful Response

**示例请求:**
```bash
curl -X GET "http://localhost:8000/api/roles/{role_id}/permissions" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `POST` /api/roles/{role_id}/permissions
**Add Permission To Role**
为角色添加权限

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| role_id | integer | path | 是 |  |

**请求体:** JSON格式
参考数据模型: `RolePermissionCreate`

**成功响应 (200):**
Successful Response
返回数据模型: `RolePermission`

**示例请求:**
```bash
curl -X POST "http://localhost:8000/api/roles/{role_id}/permissions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"key": "value"}'
```

#### `DELETE` /api/roles/{role_id}/permissions/{permission_id}
**Remove Permission From Role**
从角色中移除权限

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| role_id | integer | path | 是 |  |
| permission_id | integer | path | 是 |  |

**示例请求:**
```bash
curl -X DELETE "http://localhost:8000/api/roles/{role_id}/permissions/{permission_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 日志管理

#### `GET` /api/logs/
**Read Logs**
获取日志列表

**请求参数:**
| 参数名 | 类型 | 位置 | 必须 | 描述 |
|--------|------|------|------|------|
| start_date | string | query | 否 |  |
| end_date | string | query | 否 |  |
| username | string | query | 否 |  |
| level | string | query | 否 |  |
| limit | integer | query | 否 |  |

**成功响应 (200):**
Successful Response

**示例请求:**
```bash
curl -X GET "http://localhost:8000/api/logs/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 其他

#### `GET` /
**Root**
根路径接口

**成功响应 (200):**
Successful Response

**示例请求:**
```bash
curl -X GET "http://localhost:8000/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `GET` /health
**Health Check**
健康检查接口

**成功响应 (200):**
Successful Response

**示例请求:**
```bash
curl -X GET "http://localhost:8000/health" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📋 数据模型

### BatchHealthEvaluateRequest
| 字段名 | 类型 | 必须 | 描述 |
|--------|------|------|------|
| data_ids | array[integer] | 是 |  |

### Body_create_data_api_data__post
| 字段名 | 类型 | 必须 | 描述 |
|--------|------|------|------|
| personnel_id | string | 是 |  |
| personnel_name | string | 是 |  |
| file | string (binary) | 是 |  |

### Body_create_model_api_models__post
| 字段名 | 类型 | 必须 | 描述 |
|--------|------|------|------|
| model_type | integer | 是 |  |
| file | string (binary) | 是 |  |

### Body_login_for_access_token_api_token_post
| 字段名 | 类型 | 必须 | 描述 |
|--------|------|------|------|
| grant_type | string | 否 |  |
| username | string | 是 |  |
| password | string | 是 |  |
| scope | string | 否 |  |
| client_id | string | 否 |  |
| client_secret | string | 否 |  |

### Data
| 字段名 | 类型 | 必须 | 描述 |
|--------|------|------|------|
| personnel_id | string | 是 |  |
| data_path | string | 是 |  |
| upload_user | integer | 是 |  |
| personnel_name | string | 是 |  |
| user_id | string | 是 |  |
| id | integer | 是 |  |
| upload_time | string (date-time) | 是 |  |

### HealthEvaluateRequest
| 字段名 | 类型 | 必须 | 描述 |
|--------|------|------|------|
| data_id | integer | 是 |  |

### LoginRequest
| 字段名 | 类型 | 必须 | 描述 |
|--------|------|------|------|
| username | string | 是 |  |
| password | string | 是 |  |

### Model
| 字段名 | 类型 | 必须 | 描述 |
|--------|------|------|------|
| model_type | integer | 是 |  |
| model_path | string | 是 |  |
| id | integer | 是 |  |
| create_time | string (date-time) | 是 |  |

### Parameter
| 字段名 | 类型 | 必须 | 描述 |
|--------|------|------|------|
| param_name | string | 是 |  |
| param_value | string | 是 |  |
| param_type | string | 是 |  |
| description | string | 否 |  |
| id | integer | 是 |  |
| created_at | string (date-time) | 是 |  |
| updated_at | string | 否 |  |

### ParameterCreate
| 字段名 | 类型 | 必须 | 描述 |
|--------|------|------|------|
| param_name | string | 是 |  |
| param_value | string | 是 |  |
| param_type | string | 是 |  |
| description | string | 否 |  |

### ParameterUpdate
| 字段名 | 类型 | 必须 | 描述 |
|--------|------|------|------|
| param_name | string | 否 |  |
| param_value | string | 否 |  |
| param_type | string | 否 |  |
| description | string | 否 |  |

### Permission
| 字段名 | 类型 | 必须 | 描述 |
|--------|------|------|------|
| permission_name | string | 是 |  |
| description | string | 否 |  |
| resource | string | 是 |  |
| action | string | 是 |  |
| permission_id | integer | 是 |  |

### Result
| 字段名 | 类型 | 必须 | 描述 |
|--------|------|------|------|
| stress_score | number | 是 |  |
| depression_score | number | 是 |  |
| anxiety_score | number | 是 |  |
| user_id | string | 是 |  |
| data_id | string | 否 |  |
| report_path | string | 否 |  |
| id | integer | 是 |  |
| result_time | string (date-time) | 是 |  |

### Role
| 字段名 | 类型 | 必须 | 描述 |
|--------|------|------|------|
| role_name | string | 是 |  |
| description | string | 否 |  |
| role_id | integer | 是 |  |
| created_at | string (date-time) | 是 |  |

### RoleCreate
| 字段名 | 类型 | 必须 | 描述 |
|--------|------|------|------|
| role_name | string | 是 |  |
| description | string | 否 |  |

### RolePermission
| 字段名 | 类型 | 必须 | 描述 |
|--------|------|------|------|
| role_id | integer | 是 |  |
| permission_id | integer | 是 |  |
| id | integer | 是 |  |

### RolePermissionCreate
| 字段名 | 类型 | 必须 | 描述 |
|--------|------|------|------|
| role_id | integer | 是 |  |
| permission_id | integer | 是 |  |

### RoleUpdate
| 字段名 | 类型 | 必须 | 描述 |
|--------|------|------|------|
| role_name | string | 否 |  |
| description | string | 否 |  |

### Token
| 字段名 | 类型 | 必须 | 描述 |
|--------|------|------|------|
| access_token | string | 是 |  |
| token_type | string | 是 |  |
| user_id | string | 是 |  |
| user_type | string | 是 |  |
| username | string | 是 |  |

### User
| 字段名 | 类型 | 必须 | 描述 |
|--------|------|------|------|
| username | string | 是 |  |
| email | string | 否 |  |
| phone | string | 否 |  |
| user_type | string | 否 |  |
| user_id | string | 是 |  |
| last_login | string | 否 |  |
| created_at | string (date-time) | 是 |  |
| updated_at | string | 否 |  |

### UserCreate
| 字段名 | 类型 | 必须 | 描述 |
|--------|------|------|------|
| username | string | 是 |  |
| email | string | 否 |  |
| phone | string | 否 |  |
| user_type | string | 否 |  |
| password | string | 是 |  |

### UserUpdate
| 字段名 | 类型 | 必须 | 描述 |
|--------|------|------|------|
| username | string | 否 |  |
| email | string | 否 |  |
| phone | string | 否 |  |
| password | string | 否 |  |
| user_type | string | 否 |  |

### ValidationError
| 字段名 | 类型 | 必须 | 描述 |
|--------|------|------|------|
| loc | array[object] | 是 |  |
| msg | string | 是 |  |
| type | string | 是 |  |

## ⚠️ 错误代码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（未登录或token无效） |
| 403 | 禁止访问（权限不足） |
| 404 | 资源不存在 |
| 422 | 参数验证失败 |
| 500 | 服务器内部错误 |
