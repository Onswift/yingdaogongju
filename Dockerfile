FROM python:3.11-slim

WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# 安装依赖
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 复制代码
COPY app ./app

# 创建数据目录
RUN mkdir -p /app/data

# 环境变量
ENV DATABASE_URL=sqlite:///./data/license.db \
    ADMIN_TOKEN=change-me-in-production \
    DEBUG=False \
    LOG_LEVEL=INFO \
    APP_HOST=0.0.0.0 \
    APP_PORT=8000

EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
