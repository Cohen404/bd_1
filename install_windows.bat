@echo off
set PYTHONIOENCODING=utf-8
chcp 65001
setlocal enabledelayedexpansion

:: 设置控制台编码为UTF-8
set PYTHONIOENCODING=utf-8

:: 检查是否已安装 Conda
echo [CHECK] 检查Conda安装状态...
where conda >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Conda未安装！请先安装Anaconda或Miniconda。
    pause
    exit /b 1
)
echo [OK] Conda已安装

:: 检查conda环境是否已存在
echo [CHECK] 检查conda环境...
call conda env list | find "bj_health" >nul
if %ERRORLEVEL% EQU 0 (
    echo [INFO] conda环境 bj_health 已存在，跳过创建步骤
) else (
    echo [INFO] 正在创建conda环境 bj_health...
    call conda create -n bj_health python=3.10 -y
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] 创建conda环境失败！
        pause
        exit /b 1
    )
    echo [OK] conda环境创建成功
)

:: 激活环境
echo [INFO] 正在激活conda环境...
call activate bj_health
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] 激活conda环境失败！
    pause
    exit /b 1
)
echo [OK] conda环境已激活

:: 检查requirements_windows.txt是否存在
echo [CHECK] 检查依赖文件...
if not exist requirements_windows.txt (
    echo [ERROR] requirements_windows.txt 文件不存在！
    pause
    exit /b 1
)
echo [OK] 依赖文件检查通过

:: 安装依赖包
echo [INFO] 正在安装依赖包...
call pip install -r requirements_windows.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] 安装依赖包失败！
    pause
    exit /b 1
)
echo [OK] 依赖包安装完成

:: 检查PostgreSQL是否安装并设置PATH
echo [CHECK] 检查PostgreSQL安装状态...
where psql >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    :: 尝试在默认安装路径找到psql
    if exist "C:\Program Files\PostgreSQL" (
        for /f "delims=" %%i in ('dir /b "C:\Program Files\PostgreSQL"') do (
            if exist "C:\Program Files\PostgreSQL\%%i\bin\psql.exe" (
                set "PATH=C:\Program Files\PostgreSQL\%%i\bin;%PATH%"
                echo [INFO] 已添加PostgreSQL路径到PATH
                goto :check_psql_again
            )
        )
    )
    :: 检查其他可能的安装路径
    if exist "C:\Program Files (x86)\PostgreSQL" (
        for /f "delims=" %%i in ('dir /b "C:\Program Files (x86)\PostgreSQL"') do (
            if exist "C:\Program Files (x86)\PostgreSQL\%%i\bin\psql.exe" (
                set "PATH=C:\Program Files (x86)\PostgreSQL\%%i\bin;%PATH%"
                echo [INFO] 已添加PostgreSQL路径到PATH
                goto :check_psql_again
            )
        )
    )
    
    echo [ERROR] PostgreSQL未安装或未找到psql！
    echo 请确保已正确安装PostgreSQL，默认安装路径应该是：
    echo C:\Program Files\PostgreSQL\{版本号}\bin
    echo 或手动将PostgreSQL的bin目录添加到系统PATH环境变量中
    echo 下载地址: https://www.postgresql.org/download/windows/
    pause
    exit /b 1
)

:check_psql_again
where psql >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] 即使添加了PATH仍无法找到psql命令！
    echo 请确保PostgreSQL安装正确。
    pause
    exit /b 1
)
echo [OK] PostgreSQL已安装且可以使用

@REM :: 检查PostgreSQL服务是否运行
@REM echo [CHECK] 检查PostgreSQL服务状态...
@REM for /f "tokens=*" %%i in ('sc query state^= all ^| findstr /i "postgresql"') do (
@REM     set "service_found=1"
@REM     for /f "tokens=4" %%j in ('sc query "%%i" ^| findstr "STATE"') do (
@REM         if "%%j"=="RUNNING" (
@REM             echo [OK] PostgreSQL服务正在运行
@REM             goto :postgresql_running
@REM         )
@REM     )
@REM )

@REM :: 如果没有找到运行中的PostgreSQL服务
@REM echo [WARN] 未找到运行中的PostgreSQL服务
@REM echo [INFO] 尝试直接连接PostgreSQL...

:: 尝试直接连接数据库测试是否可用
psql -U postgres -c "\q" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] 可以连接到PostgreSQL
    goto :postgresql_running
) else (
    echo [ERROR] 无法连接到PostgreSQL！
    echo 请确保PostgreSQL服务正在运行。
    pause
    exit /b 1
)

:postgresql_running

:: 检查数据库是否已存在
echo [CHECK] 检查数据库是否已存在...
set "db_exists="
for /f "tokens=1" %%a in ('psql -U postgres -c "SELECT datname FROM pg_database WHERE datname='bj_health_db';"') do (
    if "%%a"=="bj_health_db" set "db_exists=true"
)

if defined db_exists (
    echo [INFO] 数据库已存在，正在删除...
    :: 断开所有连接
    psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='bj_health_db';"
    :: 删除数据库
    psql -U postgres -c "DROP DATABASE bj_health_db;"
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] 删除数据库失败！
        pause
        exit /b 1
    )
    echo [OK] 数据库已删除
)

:: 检查用户是否存在
echo [CHECK] 检查数据库用户是否存在...
set "user_exists="
for /f "tokens=1" %%a in ('psql -U postgres -c "SELECT usename FROM pg_user WHERE usename='bj_health_user';"') do (
    if "%%a"=="bj_health_user" set "user_exists=true"
)

if defined user_exists (
    echo [INFO] 数据库用户已存在，正在删除...
    psql -U postgres -c "DROP OWNED BY bj_health_user;"
    psql -U postgres -c "DROP USER bj_health_user;"
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] 删除用户失败！
        pause
        exit /b 1
    )
    echo [OK] 数据库用户已删除
)

:: 创建新用户
echo [INFO] 创建数据库用户...
psql -U postgres -c "CREATE USER bj_health_user WITH PASSWORD 'bj_health_pass';"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] 创建用户失败！
    pause
    exit /b 1
)
echo [OK] 数据库用户创建成功

:: 创建新数据库
echo [INFO] 创建数据库...
psql -U postgres -c "CREATE DATABASE bj_health_db OWNER bj_health_user;"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] 创建数据库失败！
    pause
    exit /b 1
)
echo [OK] 数据库创建成功

:: 初始化数据库表和数据
echo [INFO] 正在初始化数据库表和数据...
python util/init_db.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] 初始化数据库表和数据失败！
    pause
    exit /b 1
)
echo [OK] 数据库表和数据初始化完成

:: 检查sql_model.sql是否存在
echo [CHECK] 检查数据库模型文件...
if not exist sql_model.sql (
    echo [ERROR] sql_model.sql 文件不存在！
    pause
    exit /b 1
)
echo [OK] 数据库模型文件检查通过

:: 导入数据库结构
echo [INFO] 正在导入数据库结构...
psql -U bj_health_user -d bj_health_db -f sql_model.sql
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] 导入数据库结构失败！
    pause
    exit /b 1
)
echo [OK] 数据库结构导入完成

:: 检查并创建环境变量文件
echo [CHECK] 检查环境变量文件...
if exist .env (
    echo [INFO] .env文件已存在，将被覆盖
)
echo [INFO] 正在创建.env文件...
(
echo DB_HOST=localhost
echo DB_PORT=5432
echo DB_NAME=bj_health_db
echo DB_USER=bj_health_user
echo DB_PASS=bj_health_pass
echo SECRET_KEY=your_secret_key_here
echo DEBUG=False
) > .env
echo [OK] 环境变量文件创建完成

echo.
echo [SUCCESS] 安装完成！
echo.
echo 使用说明：
echo 1. 每次运行程序前，请先运行: conda activate bj_health
echo 2. 然后运行主程序即可
echo.
pause 