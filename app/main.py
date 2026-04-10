from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import logging
import os

from app.core.config import settings
from app.core.database import init_db
from app.core.response import success_response
from app.api import user_router, admin_router

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="影刀小工具授权服务（无设备版）"
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(user_router)
app.include_router(admin_router)

# 挂载静态文件目录
static_path = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_path, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_path), name="static")

# 管理后台页面
@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    """管理后台页面"""
    static_file = os.path.join(static_path, "admin.html")
    if os.path.exists(static_file):
        with open(static_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>请将 admin.html 放到 app/static/ 目录</h1>", status_code=404)


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    logger.info("应用启动中...")
    init_db()
    logger.info("数据库初始化完成")
    logger.info(f"应用启动完成：{settings.APP_NAME} v{settings.APP_VERSION}")


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    return success_response(data={"status": "healthy"})


@app.get("/", tags=["根路径"])
async def root():
    """根路径"""
    return success_response(data={
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs"
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
