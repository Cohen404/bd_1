# 一键启动后端和前端服务
# PowerShell版本，支持UTF-8编码

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "一键启动后端和前端服务" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 设置项目根目录
$PROJECT_ROOT = "D:\Code\bd_1"

# 后端目录
$BACKEND_DIR = "$PROJECT_ROOT\fastapi_backend"

# 前端目录
$FRONTEND_DIR = "$PROJECT_ROOT\frontend_ui"

# Conda环境名称
$CONDA_ENV = "bd"

Write-Host "[1/2] 启动后端服务..." -ForegroundColor Yellow
Write-Host "后端路径: $BACKEND_DIR" -ForegroundColor Gray
Write-Host "Conda环境: $CONDA_ENV" -ForegroundColor Gray
Write-Host ""

# 在新窗口中启动后端
$backendScript = @"
cd /d $BACKEND_DIR
conda activate $CONDA_ENV
echo 后端服务启动中...
uvicorn main:app --reload
"@

Start-Process cmd -ArgumentList "/k", $backendScript -WindowStyle Normal
Write-Host "后端服务已在新窗口中启动..." -ForegroundColor Green
Write-Host ""

Start-Sleep -Seconds 3

Write-Host "[2/2] 启动前端服务..." -ForegroundColor Yellow
Write-Host "前端路径: $FRONTEND_DIR" -ForegroundColor Gray
Write-Host ""

# 在新窗口中启动前端
$frontendScript = @"
cd /d $FRONTEND_DIR
echo 前端服务启动中...
npm run dev
"@

Start-Process cmd -ArgumentList "/k", $frontendScript -WindowStyle Normal
Write-Host "前端服务已在新窗口中启动..." -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "所有服务已启动完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "后端服务: http://localhost:8000" -ForegroundColor White
Write-Host "后端API文档: http://localhost:8000/docs" -ForegroundColor White
Write-Host "前端服务: 请查看前端窗口中的地址" -ForegroundColor White
Write-Host ""
Write-Host "提示: 关闭服务请关闭对应的窗口" -ForegroundColor Yellow
Write-Host ""

Read-Host "按回车键退出"
