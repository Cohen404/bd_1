@echo off
echo ========================================
echo 北京健康评估系统 - Windows环境安装脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [信息] 检测到Python版本:
python --version

REM 检查Node.js是否安装
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 未检测到Node.js，前端无法运行
    echo 下载地址: https://nodejs.org/
    echo 继续安装后端依赖...
    echo.
)

REM 创建虚拟环境
echo [步骤1] 创建Python虚拟环境...
if exist venv (
    echo [信息] 虚拟环境已存在，跳过创建
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [错误] 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo [成功] 虚拟环境创建完成
)

REM 激活虚拟环境
echo [步骤2] 激活虚拟环境...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [错误] 虚拟环境激活失败
    pause
    exit /b 1
)
echo [成功] 虚拟环境已激活

REM 升级pip
echo [步骤3] 升级pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [警告] pip升级失败，继续安装依赖
)

REM 安装依赖包
echo [步骤4] 安装Python依赖包...
echo [信息] 这可能需要几分钟时间，请耐心等待...
pip install -r requirements_windows.txt
if %errorlevel% neq 0 (
    echo [错误] 依赖包安装失败
    echo [建议] 尝试以下解决方案:
    echo 1. 检查网络连接
    echo 2. 使用国内镜像: pip install -r requirements_windows.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
    echo 3. 安装Visual Studio Build Tools
    pause
    exit /b 1
)
echo [成功] Python依赖包安装完成

REM 检查PostgreSQL
echo [步骤5] 检查PostgreSQL...
psql --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 未检测到PostgreSQL
    echo [建议] 请安装PostgreSQL 12+
    echo 下载地址: https://www.postgresql.org/download/windows/
    echo.
    echo [重要] 安装PostgreSQL后需要:
    echo 1. 创建数据库: createdb bj_health_db
    echo 2. 配置.env文件中的数据库连接信息
) else (
    echo [成功] 检测到PostgreSQL
    psql --version
)

REM 创建.env文件模板
echo [步骤6] 创建环境配置文件...
if not exist .env (
    echo # 数据库配置 > .env
    echo DB_HOST=127.0.0.1 >> .env
    echo DB_PORT=5432 >> .env
    echo DB_NAME=bj_health_db >> .env
    echo DB_USER=postgres >> .env
    echo DB_PASS=your_password_here >> .env
    echo. >> .env
    echo # JWT配置 >> .env
    echo SECRET_KEY=your_secret_key_here >> .env
    echo ACCESS_TOKEN_EXPIRE_MINUTES=1440 >> .env
    echo. >> .env
    echo # 安全配置 >> .env
    echo BCRYPT_ROUNDS=12 >> .env
    echo. >> .env
    echo # 其他配置 >> .env
    echo DEBUG=true >> .env
    echo LOG_LEVEL=INFO >> .env
    echo [成功] .env配置文件已创建
    echo [重要] 请编辑.env文件，设置正确的数据库密码和JWT密钥
) else (
    echo [信息] .env文件已存在，跳过创建
)

REM 创建启动脚本
echo [步骤7] 创建启动脚本...
echo @echo off > start_backend.bat
echo echo 启动FastAPI后端服务... >> start_backend.bat
echo call venv\Scripts\activate.bat >> start_backend.bat
echo uvicorn main:app --host 0.0.0.0 --port 8000 --reload >> start_backend.bat
echo pause >> start_backend.bat

echo @echo off > start_frontend.bat
echo echo 启动React前端服务... >> start_frontend.bat
echo cd ..\frontend_ui >> start_frontend.bat
echo npm run dev >> start_frontend.bat
echo pause >> start_frontend.bat

echo [成功] 启动脚本已创建

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo [下一步操作]
echo 1. 编辑 .env 文件，设置数据库密码和JWT密钥
echo 2. 确保PostgreSQL服务正在运行
echo 3. 创建数据库: createdb bj_health_db
echo 4. 运行后端: start_backend.bat
echo 5. 运行前端: start_frontend.bat
echo.
echo [访问地址]
echo - 后端API: http://localhost:8000
echo - 前端界面: http://localhost:3000
echo - API文档: http://localhost:8000/docs
echo.
echo [默认账户]
echo - 用户名: admin
echo - 密码: admin123
echo.
pause
