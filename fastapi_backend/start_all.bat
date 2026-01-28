@echo off
chcp 65001 >nul
echo ========================================
echo 一键启动后端和前端服务
echo ========================================
echo.

REM 设置项目根目录
set PROJECT_ROOT=D:\Code\bd_1

REM 后端目录
set BACKEND_DIR=%PROJECT_ROOT%\fastapi_backend

REM 前端目录
set FRONTEND_DIR=%PROJECT_ROOT%\frontend_ui

REM Conda环境名称
set CONDA_ENV=bd

echo [1/2] 启动后端服务...
echo 后端路径: %BACKEND_DIR%
echo Conda环境: %CONDA_ENV%
echo.

REM 在新窗口中启动后端
start "FastAPI后端" cmd /k "cd /d %BACKEND_DIR% && conda activate %CONDA_ENV% && echo 后端服务启动中... && uvicorn main:app --reload"

echo 后端服务已在新窗口中启动...
echo.

timeout /t 3 /nobreak >nul

echo [2/2] 启动前端服务...
echo 前端路径: %FRONTEND_DIR%
echo.

REM 在新窗口中启动前端
start "前端UI" cmd /k "cd /d %FRONTEND_DIR% && echo 前端服务启动中... && npm run dev"

echo 前端服务已在新窗口中启动...
echo.

echo ========================================
echo 所有服务已启动完成！
echo ========================================
echo.
echo 后端服务: http://localhost:8000
echo 后端API文档: http://localhost:8000/docs
echo 前端服务: 请查看前端窗口中的地址
echo.
echo 提示: 关闭服务请关闭对应的窗口
echo.

pause
