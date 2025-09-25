# Windows环境快速启动指南

## 🚀 一键安装和启动

### 方法1：使用安装脚本（推荐）
```bash
# 1. 双击运行安装脚本
install_windows.bat

# 2. 按照提示完成安装

# 3. 启动后端服务
start_backend.bat

# 4. 启动前端服务（新开终端）
start_frontend.bat
```

### 方法2：手动安装
```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
venv\Scripts\activate

# 3. 升级pip
python -m pip install --upgrade pip

# 4. 安装依赖
pip install -r requirements.txt

# 5. 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📋 环境要求检查清单

### ✅ 必需软件
- [ ] Python 3.8+ 
- [ ] PostgreSQL 12+
- [ ] Node.js 16+ (前端需要)

### ✅ 可选软件
- [ ] Visual Studio Build Tools (解决编译问题)
- [ ] Git (版本控制)

## 🔧 常见问题解决

### 1. psycopg2安装失败
```bash
# 解决方案1：使用预编译版本
pip install psycopg2-binary --no-cache-dir

# 解决方案2：安装Visual Studio Build Tools
# 下载地址: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

### 2. TensorFlow安装失败
```bash
# 解决方案：使用CPU版本
pip install tensorflow-cpu==2.15.0
```

### 3. 网络问题
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 4. 权限问题
```bash
# 以管理员身份运行PowerShell
# 或使用用户安装
pip install --user -r requirements.txt
```

## 🌐 服务访问地址

- **后端API**: http://localhost:8000
- **前端界面**: http://localhost:3000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 🔑 默认登录账户

- **用户名**: admin
- **密码**: admin123

## 📝 配置文件说明

### .env文件配置
```bash
# 数据库配置
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=bj_health_db
DB_USER=postgres
DB_PASS=your_password_here

# JWT配置
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 安全配置
BCRYPT_ROUNDS=12
```

## 🛠️ 开发工具推荐

### IDE推荐
- **VS Code** + Python扩展
- **PyCharm** Community版
- **Sublime Text** + Anaconda插件

### 数据库工具
- **pgAdmin 4** (PostgreSQL图形界面)
- **DBeaver** (通用数据库工具)

### API测试工具
- **Postman** (API测试)
- **Insomnia** (API测试)
- **curl** (命令行测试)

## 📞 技术支持

如果遇到问题，请检查：
1. Python版本是否符合要求
2. 虚拟环境是否正确激活
3. 数据库服务是否运行
4. 端口是否被占用
5. 防火墙设置是否正确
