# 影刀小工具授权服务（无设备版）

轻量级授权校验系统，专为影刀小工具设计。授权仅绑定影刀账号（shadow_account），不绑定设备。

---

## 快速部署（阿里云）

### 1. 上传项目

将项目文件上传到服务器（如 `/opt/license-service`）：

```bash
# 本地执行
scp -r ./* root@<服务器 IP>:/opt/license-service
```

### 2. 配置 Token

```bash
cd /opt/license-service

# 生成安全 Token（示例）
openssl rand -hex 32
# 输出：a1b2c3d4e5f6g7h8i9j0...

# 编辑 .env 文件
vim .env
# 将 ADMIN_TOKEN 改为你的 Token
```

### 3. 启动服务

```bash
docker compose up -d --build
```

### 4. 验证部署

```bash
# 查看容器状态
docker ps

# 查看日志
docker logs -f license-service

# 测试健康检查
curl http://localhost:8001/health

# 访问 Swagger 文档
# 浏览器打开：http://<服务器 IP>:8001/docs
```

---

## 端口说明

| 容器端口 | 宿主机端口 | 说明 |
|----------|------------|------|
| 8000 | 8001 | API 服务 |

访问地址：`http://<服务器 IP>:8001/docs`

---

## API 接口

### 用户接口（无需鉴权）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/redeem` | 兑换卡密 |
| POST | `/api/check-license` | 校验授权 |
| POST | `/api/heartbeat` | 心跳上报 |

### 管理接口（需要 `X-Admin-Token` 头）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/admin/cards/generate` | 批量生成卡密 |
| GET | `/admin/cards` | 查询卡密列表 |
| POST | `/admin/cards/disable` | 作废卡密 |
| GET | `/admin/licenses` | 查询授权列表 |
| POST | `/admin/licenses/extend` | 手动延期 |
| POST | `/admin/licenses/ban` | 禁用账号 |
| GET | `/admin/logs/redeem` | 兑换日志 |
| GET | `/admin/logs/license` | 授权日志 |

---

## 使用示例

### 1. 生成卡密

```bash
curl -X POST http://<服务器 IP>:8001/admin/cards/generate \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: your-admin-token" \
  -d '{
    "card_type": "month",
    "duration_days": 30,
    "quantity": 10,
    "source": "taobao"
  }'
```

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "count": 10,
    "card_codes": [
      "LIC-ABCD-EFGH-IJKL-MNOP",
      "LIC-QRST-UVWX-YZ12-3456"
    ]
  }
}
```

### 2. 兑换卡密

```bash
curl -X POST http://<服务器 IP>:8001/api/redeem \
  -H "Content-Type: application/json" \
  -d '{
    "card_code": "LIC-ABCD-EFGH-IJKL-MNOP",
    "shadow_account": "user@example.com"
  }'
```

### 3. 校验授权

```bash
curl -X POST http://<服务器 IP>:8001/api/check-license \
  -H "Content-Type: application/json" \
  -d '{
    "shadow_account": "user@example.com"
  }'
```

---

## 数据持久化

数据库文件保存在 `./data/license.db`

备份命令：
```bash
cp ./data/license.db ./data/license.db.backup.$(date +%Y%m%d)
```

---

## 常用运维命令

```bash
# 查看状态
docker ps

# 查看日志
docker logs -f license-service

# 重启
docker restart license-service

# 停止
docker stop license-service

# 启动
docker start license-service

# 进入容器
docker exec -it license-service bash

# 重新构建
docker compose up -d --build
```

---

## 阿里云防火墙配置

在阿里云控制台 > 防火墙 > 添加规则：

| 端口范围 | 授权对象 | 协议 |
|----------|----------|------|
| 8001 | 0.0.0.0/0 | TCP |

---

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `ADMIN_TOKEN` | 管理员 Token | `change-me-in-production` |
| `DATABASE_URL` | 数据库连接 | `sqlite:///./data/license.db` |
| `LOG_LEVEL` | 日志级别 | `INFO` |

---

## 卡密类型

| 类型 | duration_days | 说明 |
|------|---------------|------|
| `month` | 30 | 月卡 |
| `quarter` | 90 | 季卡 |
| `year` | 365 | 年卡 |

---

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1000 | 请求参数错误 |
| 1001 | 未授权 |
| 1004 | 资源不存在 |
| 1005 | 服务器内部错误 |
| 2000 | 卡密不存在 |
| 2001 | 卡密已被使用 |
| 2002 | 卡密已被作废 |
| 2003 | 卡密已过期 |
| 3000 | 授权不存在 |
| 3001 | 授权已过期 |
| 3002 | 授权已被禁用 |

---

## 统一返回格式

成功：
```json
{
  "code": 0,
  "message": "success",
  "data": {...}
}
```

失败：
```json
{
  "code": 非 0,
  "message": "错误描述",
  "data": null
}
```

---

## 影刀集成示例

```python
import requests

API_BASE = "http://<服务器 IP>:8001"
SHADOW_ACCOUNT = get_current_shadow_account()  # 获取当前影刀账号

def redeem_card(card_code):
    """兑换卡密"""
    resp = requests.post(f"{API_BASE}/api/redeem", json={
        "card_code": card_code,
        "shadow_account": SHADOW_ACCOUNT
    })
    data = resp.json()
    if data["code"] == 0:
        save_expire_date(data["data"]["expire_at"])
        return True, "兑换成功"
    return False, data["message"]

def check_license():
    """校验授权"""
    resp = requests.post(f"{API_BASE}/api/check-license", json={
        "shadow_account": SHADOW_ACCOUNT
    })
    data = resp.json()
    if data["code"] == 0 and data["data"]["status"] == "active":
        return True, data["data"]
    return False, data.get("message", "未知错误")
```

---

## License

MIT
