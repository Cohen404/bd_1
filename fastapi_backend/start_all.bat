@echo off
chcp 65001 >nul
echo ========================================
echo Start Backend and Frontend Services
echo ========================================
echo.

REM Set project root directory
set PROJECT_ROOT=D:\Code\bd_1

REM Backend directory
set BACKEND_DIR=%PROJECT_ROOT%\fastapi_backend

REM Frontend directory
set FRONTEND_DIR=%PROJECT_ROOT%\frontend_ui

REM Conda environment name
set CONDA_ENV=bd

echo [1/2] Starting backend service...
echo Backend path: %BACKEND_DIR%
echo Conda env: %CONDA_ENV%
echo.

REM Start backend in new window
start "FastAPI Backend" cmd /k "cd /d %BACKEND_DIR% && conda activate %CONDA_ENV% && echo Starting backend service... && uvicorn main:app --reload"

echo Backend service started in new window...
echo.

timeout /t 3 /nobreak >nul

echo [2/2] Starting frontend service...
echo Frontend path: %FRONTEND_DIR%
echo.

REM Start frontend in new window
start "Frontend UI" cmd /k "cd /d %FRONTEND_DIR% && echo Starting frontend service... && npm run dev"

echo Frontend service started in new window...
echo.

echo ========================================
echo All services started successfully!
echo ========================================
echo.
echo Backend service: http://localhost:8000
echo Backend API docs: http://localhost:8000/docs
echo Frontend service: Check frontend window for address
echo.
echo Tip: Close services by closing corresponding windows
echo.

pause
