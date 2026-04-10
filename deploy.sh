#!/bin/bash

echo "========================================"
echo         授权服务部署脚本
echo "========================================"
echo ""

cd /opt/license-service

# 拉取最新代码
echo "[1/6] 拉取最新代码..."
git pull
if [ $? -ne 0 ]; then
    echo "[错误] Git pull 失败"
    exit 1
fi
echo "[成功] 代码已更新"
echo ""

# 创建必要的目录
echo "[2/6] 创建目录..."
mkdir -p /opt/license-service/data
echo "[成功] 目录已创建"
echo ""

# 创建 .env 文件（如果不存在）
echo "[3/6] 检查配置文件..."
if [ ! -f .env ]; then
    cat > .env << EOF
ADMIN_TOKEN=dev-token
DATABASE_URL=sqlite:///./data/license.db
DEBUG=False
LOG_LEVEL=INFO
EOF
    echo "已创建 .env 文件"
else
    echo ".env 文件已存在"
fi
echo ""

# 检测 Docker Compose 命令
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
elif docker-compose version &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "[错误] 未找到 Docker Compose，请先安装"
    exit 1
fi

echo "使用命令：$DOCKER_COMPOSE"
echo ""

# 停止旧服务
echo "[4/6] 停止旧服务..."
$DOCKER_COMPOSE down
echo "[成功] 旧服务已停止"
echo ""

# 构建镜像
echo "[5/6] 构建镜像..."
$DOCKER_COMPOSE build
if [ $? -ne 0 ]; then
    echo "[错误] 构建失败"
    exit 1
fi
echo "[成功] 镜像已构建"
echo ""

# 启动新服务
echo "[6/6] 启动新服务..."
$DOCKER_COMPOSE up -d
if [ $? -ne 0 ]; then
    echo "[错误] 启动失败"
    exit 1
fi
echo "[成功] 新服务已启动"
echo ""

# 查看服务状态
echo "========================================"
echo         服务状态
echo "========================================"
$DOCKER_COMPOSE ps
echo ""
echo "========================================"
echo         部署完成！
echo "========================================"
echo ""
echo "访问地址："
echo "  管理后台：http://8.138.108.144:8001/admin"
echo "  API 文档：http://8.138.108.144:8001/docs"
echo ""
