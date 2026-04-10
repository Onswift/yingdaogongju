# 授权服务 - 阿里云部署文档

## 部署环境信息

- **操作系统**: Alibaba Cloud Linux 3 (兼容 CentOS/RHEL)
- **Python 版本**: 3.10+
- **服务端口**: 8001
- **域名**: 需要配置

---

## 第一步：连接服务器

```bash
# SSH 登录服务器
ssh root@你的服务器 IP
```

---

## 第二步：安装 Python 和环境

### 2.1 安装 Python 3.10

```bash
# 安装 EPEL 源
dnf install -y epel-release

# 安装 Python 3.10
dnf install -y python3.10 python3.10-pip python3.10-devel

# 验证安装
python3.10 --version
pip3.10 --version
```

### 2.2 安装 Nginx（用于反向代理和 HTTPS）

```bash
dnf install -y nginx
```

---

## 第三步：上传项目代码

### 3.1 在服务器上创建目录

```bash
# 创建应用目录
mkdir -p /var/www/license-service
cd /var/www/license-service
```

### 3.2 上传项目文件

**方式 A：使用 scp 上传（从本地电脑）**

```bash
# 在本地电脑执行（不是 SSH 中）
# 把项目文件夹打包上传
scp -r C:\Users\Administrator\Desktop\license-service-no-device\* root@你的服务器 IP:/var/www/license-service/
```

**方式 B：使用 Git 克隆**

```bash
# 如果有 Git 仓库
git clone 你的仓库地址 /var/www/license-service
cd /var/www/license-service
```

**方式 C：使用宝塔/文件管理器上传**

1. 在本地打包项目为 zip
2. 上传到服务器
3. 解压：`unzip license-service.zip`

---

## 第四步：配置 Python 虚拟环境和依赖

```bash
cd /var/www/license-service

# 创建虚拟环境
python3.10 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

# 额外安装生产环境依赖
pip install gunicorn
```

---

## 第五步：配置环境变量

```bash
# 创建 .env 生产环境配置
cat > .env << EOF
# 应用配置
APP_NAME=License Service
APP_VERSION=1.0.0
DEBUG=False

# 数据库配置（SQLite）
DATABASE_URL=sqlite:///./data/license.db

# 管理员 Token（改成强密码！）
ADMIN_TOKEN=你的强密码_至少 12 位

# 日志配置
LOG_LEVEL=WARNING
EOF
```

**重要**：修改 `ADMIN_TOKEN` 为一个强密码，例如：`Lic3nse_2026!Safe#Admin`

---

## 第六步：初始化数据库

```bash
# 确保在虚拟环境中
source venv/bin/activate

# 创建数据目录
mkdir -p data

# 启动一次应用以初始化数据库
python -c "from app.core.database import init_db; init_db()"

# 验证数据库文件
ls -la data/license.db
```

---

## 第七步：配置 Systemd 服务（开机自启）

```bash
# 创建 systemd 服务文件
cat > /etc/systemd/system/license-service.service << EOF
[Unit]
Description=License Service API
After=network.target

[Service]
Type=notify
User=root
Group=root
WorkingDirectory=/var/www/license-service
Environment="PATH=/var/www/license-service/venv/bin"
ExecStart=/var/www/license-service/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
Restart=always
RestartSec=10
KillSignal=SIGINT
SyslogIdentifier=license-service

[Install]
WantedBy=multi-user.target
EOF
```

```bash
# 重载 systemd 配置
systemctl daemon-reload

# 启动服务
systemctl start license-service

# 设置开机自启
systemctl enable license-service

# 查看服务状态
systemctl status license-service
```

如果状态正常，应该看到 `active (running)`。

---

## 第八步：配置 Nginx 反向代理

```bash
# 创建 Nginx 配置文件
cat > /etc/nginx/conf.d/license-service.conf << EOF
server {
    listen 80;
    server_name 你的域名;  # 改成你的域名，如：license.example.com

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF
```

```bash
# 测试 Nginx 配置
nginx -t

# 重启 Nginx
systemctl restart nginx
```

---

## 第九步：配置 HTTPS（可选但推荐）

使用 Let's Encrypt 免费证书：

```bash
# 安装 certbot
dnf install -y certbot python3-certbot-nginx

# 申请证书（替换为你的域名）
certbot --nginx -d 你的域名

# 按提示输入邮箱和同意条款
# 选择是否重定向 HTTP 到 HTTPS（建议选）
```

证书会自动续期，可以添加定时任务：

```bash
# 添加自动续期
crontab -e
# 添加这行：
0 3 * * * certbot renew --quiet
```

---

## 第十步：配置防火墙

```bash
# 如果使用阿里云安全组，在阿里云控制台配置

# 开放 HTTP (80) 和 HTTPS (443)
# 阿里云控制台 -> 安全组 -> 开放 80/443 端口

# 如果使用了 firewall
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
```

---

## 第十一步：验证部署

```bash
# 测试本地访问
curl http://127.0.0.1:8001/health

# 测试域名访问（如果配置了）
curl http://你的域名/health

# 查看日志
journalctl -u license-service -f

# 查看 Nginx 日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

浏览器访问：
- `http://你的域名/admin` - 管理后台
- `http://你的域名/docs` - API 文档

---

## 常用运维命令

```bash
# 启动服务
systemctl start license-service

# 停止服务
systemctl stop license-service

# 重启服务
systemctl restart license-service

# 查看状态
systemctl status license-service

# 查看日志
journalctl -u license-service -f

# 重启 Nginx
systemctl restart nginx

# 进入虚拟环境
cd /var/www/license-service
source venv/bin/activate

# 更新代码（Git 方式）
cd /var/www/license-service
git pull
systemctl restart license-service
```

---

## 影刀模块配置修改

部署后，影刀模块的 API 地址需要改为你的域名：

```python
# yingdao/module_*.py 中修改
API_URL = "http://你的域名/api"
# 或 HTTPS
API_URL = "https://你的域名/api"
```

---

## 问题排查

### 服务无法启动

```bash
# 查看详细错误
journalctl -u license-service -n 50

# 检查端口占用
netstat -tlnp | grep 8001

# 检查 Python 依赖
source venv/bin/activate
pip list
```

### 数据库错误

```bash
# 检查数据库文件
ls -la data/license.db

# 重新初始化
rm data/license.db
python -c "from app.core.database import init_db; init_db()"
```

### Nginx 502 错误

```bash
# 检查后端服务
systemctl status license-service

# 检查 Nginx 配置
nginx -t
systemctl restart nginx
```

### 权限问题

```bash
# 修复权限
chown -R root:root /var/www/license-service
chmod -R 755 /var/www/license-service
```

---

## 备份数据

```bash
# 备份数据库
cp /var/www/license-service/data/license.db /var/www/license-service/data/license.db.backup.$(date +%Y%m%d)

# 定期备份（添加到 crontab）
0 2 * * * cp /var/www/license-service/data/license.db /var/www/license-service/data/license.db.backup.$(date +\%Y\%m\%d)
```

---

## 部署完成！

访问 `https://你的域名/admin` 使用管理后台。

**重要提醒**：
1. 修改 `.env` 中的 `ADMIN_TOKEN` 为强密码
2. 配置 HTTPS 加密传输
3. 定期备份数据库
4. 监控服务器资源使用情况
