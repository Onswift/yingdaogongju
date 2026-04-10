# 影刀机器人授权验证集成指南

## 文件说明

```
yingdao/
├── license_validator.py    # 核心验证模块（必须）
├── robot_example.py        # 机器人示例代码
├── redeem_example.py       # 卡密兑换示例
└── README.md              # 本文档
```

## 快速开始

### 1. 复制验证模块

将 `license_validator.py` 复制到你的影刀机器人项目目录中。

### 2. 基础集成

在你的影刀机器人代码开头添加：

```python
from license_validator import LicenseValidator, ValidationError

# 初始化验证器
validator = LicenseValidator(
    api_base="http://your-server-ip:8000/api",  # 修改为你的服务器地址
    shadow_account="你的影刀账号"
)

# 启动前验证
try:
    validator.check_license()
    print("授权验证通过，开始运行...")
except ValidationError as e:
    print(f"授权验证失败：{e}")
    exit(1)

# 启动心跳（可选，推荐）
validator.start_heartbeat()
```

### 3. 完整示例

参考 `robot_example.py` 的完整集成方式：

```python
from license_validator import LicenseValidator, ValidationError
import time

# ============ 配置 ============
API_BASE_URL = "http://your-server-ip:8000/api"
SHADOW_ACCOUNT = "你的影刀账号"

# ============ 回调函数 ============
def on_license_invalid(result):
    """授权失效时的处理"""
    print(f"授权失效！状态：{result}")
    # 这里可以：
    # 1. 保存当前进度
    # 2. 清理敏感数据
    # 3. 发送通知给管理员
    # 4. 强制退出程序

# ============ 初始化 ============
validator = LicenseValidator(
    api_base=API_BASE_URL,
    shadow_account=SHADOW_ACCOUNT,
    heartbeat_interval=300,  # 5 分钟心跳
    on_license_invalid=on_license_invalid
)

# ============ 主程序 ============
def main():
    # 1. 启动前验证
    try:
        result = validator.check_license()
        print(f"验证成功，剩余{result['remain_days']}天")
    except ValidationError as e:
        print(f"验证失败：{e}")
        return

    # 2. 启动心跳守护
    validator.start_heartbeat()

    try:
        # 3. 执行你的机器人任务
        while True:
            # 你的业务逻辑
            # ...
            time.sleep(60)
    finally:
        # 4. 退出时停止心跳
        validator.stop_heartbeat()

if __name__ == "__main__":
    main()
```

## API 接口说明

### 验证模块方法

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `check_license(raise_error=True)` | 校验授权状态 | `raise_error`: 失败是否抛异常 | `dict` - 授权信息 |
| `heartbeat()` | 心跳上报 | 无 | `dict` - 状态 |
| `start_heartbeat()` | 启动后台心跳 | 无 | 无 |
| `stop_heartbeat()` | 停止心跳 | 无 | 无 |
| `redeem(card_code)` | 兑换卡密 | `card_code`: 卡密 | `dict` - 兑换结果 |

### 响应格式

**check_license 成功响应：**
```python
{
    "status": "active",
    "expire_at": "2026-05-08T12:00:00",
    "remain_days": 30
}
```

**heartbeat 响应：**
```python
{
    "status": "active"  # 或 "expired", "banned", "error"
}
```

**redeem 响应：**
```python
{
    "success": True,
    "status": "active",
    "remain_days": 30,
    "expire_at": "2026-05-08T12:00:00"
}
```

## 部署建议

### 开发环境
```python
API_BASE_URL = "http://localhost:8000/api"
```

### 生产环境
```python
# 使用公网 IP 或域名
API_BASE_URL = "http://your-server-ip:8000/api"
# 或者使用 HTTPS
API_BASE_URL = "https://your-domain.com/api"
```

## 安全建议

1. **心跳间隔**：建议 300 秒（5 分钟），不要太长也不要太短
2. **异常处理**：网络错误时不要立即退出，可以重试 2-3 次
3. **本地缓存**：可以缓存验证结果，避免频繁请求
4. **日志记录**：记录所有验证失败的情况

## 常见问题

### Q: 网络超时怎么办？
A: 默认超时 10 秒，可以在初始化时修改：
```python
validator = LicenseValidator(..., request_timeout=30)
```

### Q: 如何离线运行？
A: 可以添加离线模式：
```python
if not validator.check_license(raise_error=False):
    # 使用本地缓存的授权状态
    pass
```

### Q: 如何在影刀编辑器中调试？
A: 使用本地服务器测试：
```python
API_BASE_URL = "http://127.0.0.1:8000/api"
```
