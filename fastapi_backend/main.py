from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from datetime import datetime, timedelta
from typing import List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(username)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("log/fastapi.log")
    ]
)

# 创建自定义日志过滤器
class UserFilter(logging.Filter):
    def __init__(self, username="未登录"):
        super().__init__()
        self.username = username

    def filter(self, record):
        if not hasattr(record, 'username'):
            record.username = self.username
        return True

# 获取根日志记录器并添加过滤器
logger = logging.getLogger()
logger.addFilter(UserFilter())

# 创建FastAPI应用
app = FastAPI(
    title="北京健康评估系统API",
    description="北京健康评估系统的后端API接口",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入路由模块
from routers import auth, users, data, models, results, health_evaluate, parameters, roles, logs

# 注册路由
app.include_router(auth.router, prefix="/api", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户管理"])
app.include_router(data.router, prefix="/api/data", tags=["数据管理"])
app.include_router(models.router, prefix="/api/models", tags=["模型管理"])
app.include_router(results.router, prefix="/api/results", tags=["结果管理"])
app.include_router(health_evaluate.router, prefix="/api/health", tags=["健康评估"])
app.include_router(parameters.router, prefix="/api/parameters", tags=["参数管理"])
app.include_router(roles.router, prefix="/api/roles", tags=["角色管理"])
app.include_router(logs.router, prefix="/api/logs", tags=["日志管理"])

@app.get("/")
async def root():
    return {"message": "欢迎使用北京健康评估系统API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 