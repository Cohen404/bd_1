# 前端API接口文档

本文档详细描述了前端UI中调用的所有后端API接口，包括输入参数、输出格式和使用场景。

## 目录

- [认证相关API](#认证相关api)
- [用户管理API](#用户管理api)
- [角色管理API](#角色管理api)
- [数据管理API](#数据管理api)
- [健康评估API](#健康评估api)
- [结果管理API](#结果管理api)
- [模型管理API](#模型管理api)
- [参数管理API](#参数管理api)
- [日志管理API](#日志管理api)
- [系统健康检查API](#系统健康检查api)

## 认证相关API

### 1. 用户登录
- **接口**: `POST /api/login`
- **输入参数**:
  ```typescript
  {
    username: string;  // 用户名
    password: string;  // 密码
  }
  ```
- **输出格式**:
  ```typescript
  {
    access_token: string;  // 访问令牌
    token_type: string;    // 令牌类型
    user_id: string;       // 用户ID
    user_type: string;     // 用户类型 (admin/user)
    username: string;      // 用户名
  }
  ```
- **使用场景**: 用户登录认证

### 2. 获取当前用户信息
- **接口**: `GET /api/users/me`
- **输入参数**: 无（需要Bearer Token）
- **输出格式**:
  ```typescript
  {
    user_id: string;
    username: string;
    email?: string;
    phone?: string;
    user_type: 'admin' | 'user';
    last_login?: string;
    created_at: string;
    updated_at?: string;
  }
  ```
- **使用场景**: 获取当前登录用户的详细信息

## 用户管理API

### 1. 获取用户列表
- **接口**: `GET /api/users/`
- **输入参数**:
  ```typescript
  {
    page?: number;     // 页码
    size?: number;     // 每页数量
    search?: string;   // 搜索关键词
  }
  ```
- **输出格式**:
  ```typescript
  {
    items: User[];     // 用户列表
    total: number;     // 总数量
    page: number;      // 当前页码
    size: number;      // 每页数量
  }
  ```
- **使用场景**: 管理员查看用户列表

### 2. 创建用户
- **接口**: `POST /api/users/`
- **输入参数**:
  ```typescript
  {
    username: string;    // 用户名
    password: string;    // 密码
    email?: string;      // 邮箱
    phone?: string;      // 电话
    user_type?: string;  // 用户类型
  }
  ```
- **输出格式**: 创建的用户信息
- **使用场景**: 管理员创建新用户

### 3. 更新用户
- **接口**: `PUT /api/users/{userId}`
- **输入参数**:
  ```typescript
  {
    username?: string;   // 用户名
    email?: string;      // 邮箱
    phone?: string;      // 电话
    password?: string;   // 密码
    user_type?: string;  // 用户类型
  }
  ```
- **输出格式**: 更新后的用户信息
- **使用场景**: 管理员编辑用户信息

### 4. 删除用户
- **接口**: `DELETE /api/users/{userId}`
- **输入参数**: 无
- **输出格式**: 删除结果
- **使用场景**: 管理员删除用户

### 5. 获取用户详情
- **接口**: `GET /api/users/{userId}`
- **输入参数**: 无
- **输出格式**: 用户详细信息
- **使用场景**: 查看特定用户的详细信息

## 角色管理API

### 1. 获取角色列表
- **接口**: `GET /api/roles/`
- **输入参数**:
  ```typescript
  {
    page?: number;  // 页码
    size?: number;  // 每页数量
  }
  ```
- **输出格式**:
  ```typescript
  {
    items: Role[];  // 角色列表
    total: number;  // 总数量
  }
  ```
- **使用场景**: 查看系统角色列表

### 2. 创建角色
- **接口**: `POST /api/roles/`
- **输入参数**:
  ```typescript
  {
    role_name: string;    // 角色名称
    description?: string; // 角色描述
  }
  ```
- **输出格式**: 创建的角色信息
- **使用场景**: 管理员创建新角色

### 3. 更新角色
- **接口**: `PUT /api/roles/{roleId}`
- **输入参数**:
  ```typescript
  {
    role_name?: string;    // 角色名称
    description?: string;  // 角色描述
  }
  ```
- **输出格式**: 更新后的角色信息
- **使用场景**: 管理员编辑角色信息

### 4. 删除角色
- **接口**: `DELETE /api/roles/{roleId}`
- **输入参数**: 无
- **输出格式**: 删除结果
- **使用场景**: 管理员删除角色

### 5. 获取角色权限
- **接口**: `GET /api/roles/{roleId}/permissions`
- **输入参数**: 无
- **输出格式**:
  ```typescript
  Permission[]  // 权限列表
  ```
- **使用场景**: 查看角色拥有的权限

## 数据管理API

### 1. 获取数据列表
- **接口**: `GET /api/data/`
- **输入参数**:
  ```typescript
  {
    page?: number;     // 页码
    size?: number;     // 每页数量
    search?: string;   // 搜索关键词
  }
  ```
- **输出格式**:
  ```typescript
  {
    items: Data[];     // 数据列表
    total: number;     // 总数量
  }
  ```
- **使用场景**: 查看上传的数据文件列表

### 2. 获取前200条数据
- **接口**: `GET /api/data/top-200`
- **输入参数**: 无
- **输出格式**:
  ```typescript
  Data[]  // 前200条数据
  ```
- **使用场景**: 快速选择前200条数据进行批量操作

### 3. 上传单个数据文件
- **接口**: `POST /api/data/`
- **输入参数**: FormData
  ```typescript
  {
    file: File;              // 数据文件
    personnel_id: string;    // 人员ID
    personnel_name: string;  // 人员姓名
  }
  ```
- **输出格式**: 上传结果
- **使用场景**: 上传单个数据文件

### 4. 批量上传数据文件
- **接口**: `POST /api/data/batch-upload`
- **输入参数**: FormData
  ```typescript
  {
    files: File[];  // 多个数据文件
  }
  ```
- **输出格式**:
  ```typescript
  {
    success_count: number;  // 成功上传数量
    failed_count: number;   // 失败数量
    errors?: string[];      // 错误信息列表
  }
  ```
- **使用场景**: 批量上传多个数据文件

### 5. 预处理单个数据
- **接口**: `POST /api/data/{dataId}/preprocess`
- **输入参数**: 无
- **输出格式**: 预处理结果
- **使用场景**: 对单个数据进行预处理

### 6. 批量预处理数据
- **接口**: `POST /api/data/batch-preprocess`
- **输入参数**:
  ```typescript
  {
    data_ids: number[];  // 数据ID列表
  }
  ```
- **输出格式**: 批量预处理结果
- **使用场景**: 批量预处理多个数据

### 7. 批量删除数据
- **接口**: `DELETE /api/data/batch-delete`
- **输入参数**:
  ```typescript
  {
    data_ids: number[];  // 数据ID列表
  }
  ```
- **输出格式**: 删除结果
- **使用场景**: 批量删除多个数据

### 8. 删除单个数据
- **接口**: `DELETE /api/data/{dataId}`
- **输入参数**: 无
- **输出格式**: 删除结果
- **使用场景**: 删除单个数据

### 9. 获取数据详情
- **接口**: `GET /api/data/{dataId}`
- **输入参数**: 无
- **输出格式**: 数据详细信息
- **使用场景**: 查看特定数据的详细信息

### 10. 获取数据图像
- **接口**: `GET /api/health/images/{dataId}`
- **输入参数**: 无
- **输出格式**: 图像数据
- **使用场景**: 获取数据的可视化图像

### 11. 获取单个数据预处理进度
- **接口**: `GET /api/data/progress/single/{dataId}`
- **输入参数**: 无
- **输出格式**:
  ```typescript
  {
    data_id: number;
    personnel_name: string;
    processing_status: string;
    feature_status: string;
    progress_percentage: number;
    message: string;
  }
  ```
- **使用场景**: 查看单个数据的预处理进度

### 12. 获取批量预处理进度
- **接口**: `GET /api/data/progress?data_ids={dataIds}`
- **输入参数**: 无
- **输出格式**: 批量预处理进度信息
- **使用场景**: 查看多个数据的预处理进度

### 13. 更新数据状态
- **接口**: `PUT /api/data/status/{dataId}`
- **输入参数**:
  ```typescript
  {
    processing_status?: string;  // 处理状态
    feature_status?: string;     // 特征状态
  }
  ```
- **输出格式**: 更新结果
- **使用场景**: 更新数据的处理状态

## 健康评估API

### 1. 单个健康评估
- **接口**: `POST /api/health/evaluate`
- **输入参数**:
  ```typescript
  {
    data_id: number;  // 数据ID
  }
  ```
- **输出格式**:
  ```typescript
  {
    id: number;                    // 结果ID
    stress_score: number;          // 应激分数
    depression_score: number;      // 抑郁分数
    anxiety_score: number;         // 焦虑分数
    social_isolation_score: number; // 社交孤立分数
  }
  ```
- **使用场景**: 对单个数据进行健康评估

### 2. 批量健康评估
- **接口**: `POST /api/health/batch-evaluate`
- **输入参数**:
  ```typescript
  {
    data_ids: number[];  // 数据ID列表
  }
  ```
- **输出格式**: 批量评估结果
- **使用场景**: 批量对多个数据进行健康评估

### 3. 获取健康报告
- **接口**: `GET /api/health/reports/{resultId}`
- **输入参数**: 无
- **输出格式**: PDF文件 (blob)
- **使用场景**: 下载健康评估报告

### 4. 获取LED状态
- **接口**: `GET /api/health/led-status/{resultId}`
- **输入参数**: 无
- **输出格式**: LED状态信息
- **使用场景**: 获取评估结果的LED显示状态

## 结果管理API

### 1. 获取结果列表
- **接口**: `GET /api/results/`
- **输入参数**:
  ```typescript
  {
    page?: number;     // 页码
    size?: number;     // 每页数量
    search?: string;   // 搜索关键词
  }
  ```
- **输出格式**:
  ```typescript
  {
    items: Result[];   // 结果列表
    total: number;     // 总数量
  }
  ```
- **使用场景**: 查看健康评估结果列表

### 2. 获取结果详情
- **接口**: `GET /api/results/{resultId}`
- **输入参数**: 无
- **输出格式**: 结果详细信息
- **使用场景**: 查看特定评估结果的详细信息

### 3. 删除结果
- **接口**: `DELETE /api/results/{resultId}`
- **输入参数**: 无
- **输出格式**: 删除结果
- **使用场景**: 删除评估结果

### 4. 获取结果报告
- **接口**: `GET /api/results/{resultId}/report`
- **输入参数**: 无
- **输出格式**: PDF文件 (blob)
- **使用场景**: 下载评估结果报告

## 模型管理API(已完成)

### 1. 获取模型列表
- **接口**: `GET /api/models/`
- **输入参数**:
  ```typescript
  {
    page?: number;  // 页码
    size?: number;  // 每页数量
  }
  ```
- **输出格式**:
  ```typescript
  {
    items: Model[];  // 模型列表
    total: number;   // 总数量
  }
  ```
- **使用场景**: 查看AI模型列表

### 2. 上传模型
- **接口**: `POST /api/models/upload`
- **输入参数**: FormData
  ```typescript
  {
    file: File;        // 模型文件
    model_type: number; // 模型类型
  }
  ```
- **输出格式**: 上传结果
- **使用场景**: 上传新的AI模型

### 3. 删除模型
- **接口**: `DELETE /api/models/{modelId}`
- **输入参数**: 无
- **输出格式**: 删除结果
- **使用场景**: 删除AI模型

### 4. 获取模型详情
- **接口**: `GET /api/models/{modelId}`
- **输入参数**: 无
- **输出格式**: 模型详细信息
- **使用场景**: 查看特定模型的详细信息

## 参数管理API(已完成)

### 1. 获取参数列表
- **接口**: `GET /api/parameters/`
- **输入参数**:
  ```typescript
  {
    page?: number;  // 页码
    size?: number;  // 每页数量
  }
  ```
- **输出格式**:
  ```typescript
  {
    items: Parameter[];  // 参数列表
    total: number;       // 总数量
  }
  ```
- **使用场景**: 查看系统参数列表

### 2. 创建参数
- **接口**: `POST /api/parameters/`
- **输入参数**:
  ```typescript
  {
    param_name: string;    // 参数名称
    param_value: string;   // 参数值
    param_type: string;    // 参数类型
    description?: string;  // 参数描述
  }
  ```
- **输出格式**: 创建的参数信息
- **使用场景**: 创建新的系统参数

### 3. 更新参数
- **接口**: `PUT /api/parameters/{paramId}`
- **输入参数**:
  ```typescript
  {
    param_name?: string;    // 参数名称
    param_value?: string;   // 参数值
    param_type?: string;    // 参数类型
    description?: string;   // 参数描述
  }
  ```
- **输出格式**: 更新后的参数信息
- **使用场景**: 编辑系统参数

### 4. 删除参数
- **接口**: `DELETE /api/parameters/{paramId}`
- **输入参数**: 无
- **输出格式**: 删除结果
- **使用场景**: 删除系统参数

## 日志管理API

### 1. 获取日志列表
- **接口**: `GET /api/logs/`
- **输入参数**:
  ```typescript
  {
    page?: number;     // 页码
    size?: number;     // 每页数量
    search?: string;   // 搜索关键词
  }
  ```
- **输出格式**:
  ```typescript
  {
    items: LogEntry[];  // 日志列表
    total: number;      // 总数量
  }
  ```
- **使用场景**: 查看系统操作日志

## 系统健康检查API（已完成）

### 1. 系统健康检查
- **接口**: `GET /`
- **输入参数**: 无
- **输出格式**: 系统状态信息
- **使用场景**: 检查系统运行状态

## 通用API方法

### 1. 通用GET请求
- **方法**: `apiClient.get<T>(url, config?)`
- **使用场景**: 发送GET请求

### 2. 通用POST请求
- **方法**: `apiClient.post<T>(url, data?, config?)`
- **使用场景**: 发送POST请求

### 3. 通用PUT请求
- **方法**: `apiClient.put<T>(url, data?, config?)`
- **使用场景**: 发送PUT请求

### 4. 通用DELETE请求
- **方法**: `apiClient.delete<T>(url, config?)`
- **使用场景**: 发送DELETE请求

## 认证机制

所有API请求都需要在请求头中包含认证令牌：

```
Authorization: Bearer {access_token}
```

## 错误处理

API响应拦截器会自动处理以下错误状态码：

- **401**: 认证失败，自动跳转到登录页
- **403**: 权限不足
- **404**: 资源不存在
- **422**: 参数验证失败
- **500+**: 服务器内部错误

## 分页参数

大部分列表API都支持分页参数：

- `page`: 页码（从1开始）
- `size`: 每页数量
- `search`: 搜索关键词

## 文件上传

文件上传API使用 `multipart/form-data` 格式，支持：

- 单个文件上传
- 批量文件上传
- 上传进度跟踪

## 数据状态

数据对象包含以下状态字段：

- `processing_status`: 处理状态 (pending/processing/completed/failed)
- `feature_status`: 特征状态 (pending/processing/completed/failed)

## 健康评估分数

健康评估结果包含四个维度的分数：

- `stress_score`: 应激分数 (0-100)
- `depression_score`: 抑郁分数 (0-100)
- `anxiety_score`: 焦虑分数 (0-100)
- `social_isolation_score`: 社交孤立分数 (0-100)

## 模型类型

系统支持以下AI模型类型：

- 0: 普通应激模型
- 1: 抑郁评估模型
- 2: 焦虑评估模型
- 3: 社交孤立评估模型

## 用户类型

系统支持以下用户类型：

- `admin`: 管理员
- `user`: 普通用户

## 注意事项

1. 所有API请求都有30秒超时限制
2. 文件上传支持进度跟踪
3. 批量操作支持进度查询
4. 所有时间字段使用ISO 8601格式
5. 分页从1开始计数
6. 搜索功能支持模糊匹配
7. 删除操作需要确认
8. 上传文件有大小限制
9. 模型文件需要特定格式
10. 参数值需要根据参数类型进行验证
