# 健康管理系统

## 项目说明
这是一个基于PyQt5和PostgreSQL的健康管理系统。

## 环境要求
- Python 3.10+
- PostgreSQL 12+
- CUDA 12.3
- NVIDIA GPU Driver 550.142+
- Qt 5.15.9
- 其他依赖见requirements.txt

## 数据库配置
1. 安装PostgreSQL数据库
2. 创建数据库：
```bash
# 使用PostgreSQL命令行创建数据库
sudo -u postgres psql -c "CREATE DATABASE bj_health_manage;"

# 或者在psql命令行中执行：
CREATE DATABASE bj_health_manage;
```
3. 配置数据库连接：
   - 主机：127.0.0.1
   - 端口：5432
   - 数据库：bj_health_manage
   - 用户名：postgres
   - 密码：postgres

4. 初始化数据库：
```bash
python util/init_db.py
```

## 安装步骤
1. 克隆项目到本地

2. 安装系统依赖：
```bash
# 安装Qt相关依赖
sudo apt-get install libxcb-xinerama0 libxcb-cursor0 libxcb1 libxcb-icccm4 \
    libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
    libxcb-render0 libxcb-shape0 libxcb-shm0 libxcb-sync1 libxcb-util1 \
    libxcb-xfixes0 libxcb-xkb1 libxkbcommon-x11-0
```

3. 配置Qt环境变量：
```bash
# 添加到 ~/.bashrc 文件
export QT_DEBUG_PLUGINS=1
export QT_QPA_PLATFORM=xcb
```

4. 安装Python依赖：
```bash
# 安装基本依赖
pip install -r requirements.txt

# 安装特定版本的Qt包
pip install PyQt5==5.15.9 PyQtWebEngine==5.15.6
```

5. 初始化数据库：
```bash
psql -U postgres -d health_manage -f sql_model/init.sql
```

6. 运行程序：
```bash
python run.py
```

## 目录结构
- backend/: 后端逻辑代码
- front/: 前端界面代码
- sql_model/: 数据库模型和SQL脚本
- util/: 工具函数
- config/: 配置文件
- requirements.txt: 项目依赖

## 数据库表结构
### 用户表(tb_user)
- user_id: 用户ID（主键）
- username: 用户名
- password: 密码（加密存储）
- email: 邮箱
- phone: 电话号码
- user_type: 用户类型（admin/user）
- last_login: 最后登录时间
- created_at: 创建时间
- updated_at: 更新时间

### 数据表(tb_data)
- id: 数据ID（主键，自增）
- personnel_id: 人员ID
- data_path: 文件路径
- upload_user: 上传用户类型
- personnel_name: 人员姓名
- user_id: 关联用户ID
- upload_time: 上传时间

### 结果表(tb_result)
- id: 结果ID（主键，自增）
- result_time: 结果计算时间
- stress_score: 应激评分
- depression_score: 抑郁评分
- anxiety_score: 焦虑评分
- report_path: 报告路径
- user_id: 关联用户ID

### 模型表(tb_model)
- id: 模型ID（主键，自增）
- model_type: 模型类型
- model_path: 模型路径
- create_time: 创建时间

### 系统参数表(tb_system_params)
- param_id: 参数ID（主键）
- eeg_frequency: 脑电数据采样频率
- electrode_count: 电极数量
- scale_question_num: 量表问题数量
- model_num: 系统中可用的模型数量
- id: 系统ID

### 角色表(tb_role)
- role_id: 角色ID（主键）
- role_name: 角色名称
- description: 角色描述
- created_at: 创建时间

### 用户角色关联表(tb_user_role)
- user_id: 用户ID
- role_id: 角色ID

### 权限表(tb_permission)
- permission_id: 权限ID（主键）
- permission_name: 权限名称
- page_url: 页面URL
- description: 权限描述
- created_at: 创建时间

### 角色权限关联表(tb_role_permission)
- role_id: 角色ID
- permission_id: 权限ID
