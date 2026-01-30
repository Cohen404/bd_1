from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from datetime import datetime, timedelta
from typing import List, Optional

# 首先设置日志配置
from config import setup_logging
setup_logging()

# 获取日志记录器
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="急进高原新兵心理应激多模态神经生理监测预警系统API",
    description="急进高原新兵心理应激多模态神经生理监测预警系统的后端API接口",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入路由模块
try:
    from routers import auth, users, data, models, results, health_evaluate, parameters, roles, logs, active_learning, eegs
    
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
    app.include_router(active_learning.router, prefix="/api/active-learning", tags=["主动学习"])
    app.include_router(eegs.router, tags=["EEG数据"])
    
    logger.info("所有路由模块加载成功")
except ImportError as e:
    logger.error(f"导入路由模块失败: {e}")
    raise

@app.get("/")
async def root():
    """根路径接口"""
    return {"message": "欢迎使用急进高原新兵心理应激多模态神经生理监测预警系统API", "status": "running"}

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "bj_health_csq_api"
    }

# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return {"detail": "内部服务器错误", "status_code": 500}

if __name__ == "__main__":
    logger.info("启动急进高原新兵心理应激多模态神经生理监测预警系统API服务器")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 