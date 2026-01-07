@echo off
chcp 65001 >nul
echo ========================================
echo PostgreSQL Windows 安装脚本
echo ========================================
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorLevel% == 0 (
    echo 检测到管理员权限，继续安装...
) else (
    echo 警告: 建议以管理员身份运行此脚本
    echo 按任意键继续，或关闭窗口取消...
    pause >nul
)


echo 启动PostgreSQL服务...
net start postgresql

echo 清理安装文件...
del postgresql-installer.exe

:create_env
echo.
echo 步骤 3: 创建环境配置文件...
if not exist ".env" (
    echo # 数据库配置 > .env
    echo DB_HOST=127.0.0.1 >> .env
    echo DB_PORT=5432 >> .env
    echo DB_NAME=bj_health_db >> .env
    echo DB_USER=postgres >> .env
    echo DB_PASS=tj654478 >> .env
    echo. >> .env
    echo # JWT配置 >> .env
    echo SECRET_KEY=rjD66zC6e4h58TuPFa3peppOjsUc1dprKtCIVNds4cQ >> .env
    echo ACCESS_TOKEN_EXPIRE_MINUTES=1440 >> .env
    echo. >> .env
    echo # 安全配置 >> .env
    echo BCRYPT_ROUNDS=12 >> .env
    echo. >> .env
    echo # 其他配置 >> .env
    echo DEBUG=true >> .env
    echo LOG_LEVEL=INFO >> .env
    echo .env 文件已创建
) else (
    echo .env 文件已存在
)

echo.
echo 步骤 4: 创建数据库和用户...
set PGPASSWORD=tj654478
psql -d postgres -U postgres -c "CREATE USER postgres WITH PASSWORD 'tj654478';" 2>nul
psql -d postgres -U postgres -c "CREATE DATABASE bj_health_db;" 2>nul
psql -d postgres -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE bj_health_db TO postgres;" 2>nul
psql -d postgres -U postgres -c "ALTER USER postgres CREATEDB;" 2>nul

echo.
echo 步骤 5: 初始化数据库表...
python -c "from database import init_db; init_db()" 2>nul
if %errorLevel% == 0 (
    echo 数据库表初始化成功
) else (
    echo 数据库表初始化失败，请检查Python环境和依赖
)

echo.
echo 步骤 6: 测试数据库连接...
python -c "from database import engine; print('数据库连接成功' if engine.connect() else '连接失败')" 2>nul

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 数据库配置:
echo - 主机: 127.0.0.1
echo - 端口: 5432
echo - 数据库: bj_health_db
echo - 用户: postgres
echo - 密码: tj654478
echo.
echo 下一步:
echo 1. 激活虚拟环境: venv\Scripts\activate
echo 2. 启动应用: uvicorn main:app --reload
echo.
pause
