# 一键部署说明

## 部署架构

```
本地电脑 --(Git)--> 代码仓库 --(SSH)--> 服务器 (8.138.108.144:8001)
```

## 端口说明

- **容器内部**: 8000 端口
- **服务器外部**: 8001 端口
- **访问地址**: `http://8.138.108.144:8001`

---

## 首次部署（需要在服务器上执行）

### 1. SSH 登录服务器

```bash
ssh root@8.138.108.144
```

### 2. 安装 Docker 和 Docker Compose

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker

# 安装 Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

### 3. 克隆项目代码

```bash
mkdir -p /opt/license-service
cd /opt/license-service
git clone 你的 Git 仓库地址 .
```

### 4. 上传部署脚本

把本地的 `deploy.sh` 上传到服务器：

```bash
# 在本地电脑执行
scp deploy.sh root@8.138.108.144:/opt/license-service/
```

### 5. 赋予执行权限

```bash
chmod +x /opt/license-service/deploy.sh
```

### 6. 配置 .env 文件

```bash
cat > /opt/license-service/.env << EOF
ADMIN_TOKEN=你的强密码
DATABASE_URL=sqlite:///./data/license.db
DEBUG=False
LOG_LEVEL=WARNING
EOF
```

---

## 日常部署（一键）

双击 `deploy.bat` 即可，会自动完成：

1. 提交本地代码到 Git 仓库
2. SSH 连接服务器
3. 执行服务器上的 `deploy.sh`
4. Docker 重新构建并启动

---

## 访问地址

| 服务 | 地址 |
|------|------|
| 管理后台 | `http://8.138.108.144:8001/admin` |
| API 文档 | `http://8.138.108.144:8001/docs` |
| 健康检查 | `http://8.138.108.144:8001/health` |

---

## 常用命令

### 在服务器上执行

```bash
# 查看服务状态
cd /opt/license-service
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 启动服务
docker-compose up -d

# 重新构建
docker-compose build --no-cache
```

### 数据库备份

```bash
# 备份
cp /opt/license-service/data/license.db /opt/license-service/data/license.db.backup.$(date +%Y%m%d)

# 恢复
cp /opt/license-service/data/license.db.backup.20260410 /opt/license-service/data/license.db
docker-compose restart
```

---

## 故障排查

### 部署失败

```bash
# 查看部署日志
ssh root@8.138.108.144 "bash /opt/license-service/deploy.sh"
```

### 服务无法启动

```bash
# 查看容器日志
docker-compose logs license-service

# 检查端口占用
netstat -tlnp | grep 8001
```

### 数据丢失

检查数据卷挂载：

```bash
docker-compose ps
ls -la /opt/license-service/data/
```

---

## 安全建议

1. **修改 ADMIN_TOKEN**：使用强密码
2. **配置防火墙**：只开放必要端口
3. **定期备份**：每天备份数据库
4. **HTTPS**：生产环境建议配置 HTTPS
