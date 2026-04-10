# 影刀集成代码使用说明

## 文件说明

```
yingdao/
├── license_validator_simple.py    ← 直接复制到影刀中使用
├── README_YINGDAO.md              ← 本文档
└── test_example.py                ← 测试示例
```

---

## 快速开始（3 步）

### 步骤 1：复制代码

将 `license_validator_simple.py` 的**全部内容**复制到影刀机器人的 Python 模块中。

### 步骤 2：修改配置

在影刀中修改这两行：
```python
API_URL = "http://你的服务器 IP:8000/api"
SHADOW_ACCOUNT = "你的影刀账号"
```

### 步骤 3：调用验证

在机器人流程开始时添加：
```python
from license_validator_simple import init_validator, check_license_status, do_heartbeat

# 初始化
init_validator(API_URL, SHADOW_ACCOUNT)

# 启动前验证
try:
    result = check_license_status()
except Exception as e:
    print(f"授权失败：{e}")
    # 退出流程
```

---

## 完整示例（直接复制到影刀）

```python
# ==================== 影刀机器人主流程 ====================

# 导入验证模块
from license_validator_simple import (
    init_validator,
    check_license_status,
    do_heartbeat,
    redeem_card,
    LicenseError
)
import time

# ==================== 配置区域 ====================
API_URL = "http://localhost:8000/api"  # 修改为服务器地址
SHADOW_ACCOUNT = "test_user"           # 修改为你的影刀账号
CARD_CODE = ""                         # 留空，需要兑换时填写

# ==================== 主流程 ====================

def main():
    """机器人主流程"""
    
    # 1. 初始化验证器
    init_validator(API_URL, SHADOW_ACCOUNT)
    
    # 2. 启动前授权验证
    print("正在验证授权...")
    try:
        result = check_license_status()
        print(f"✓ 授权验证通过 - 剩余{result['remain_days']}天")
    except LicenseError as e:
        print(f"✗ 授权失败：{e}")
        # 这里可以添加：发送通知、记录日志等
        return False
    
    # 3. 执行你的机器人任务
    print("开始执行任务...")
    try:
        # 示例：循环执行任务
        for i in range(10):
            # 每轮检查授权（可选，建议每 5-10 轮检查一次）
            if i % 5 == 0:
                hb_result = do_heartbeat()
                if hb_result.get("status") != "active":
                    print(f"[警告] 授权异常：{hb_result}")
                    break
            
            # 你的实际业务逻辑
            print(f"执行第 {i+1} 轮任务...")
            # 这里写你的操作，例如：
            # - 打开浏览器
            # - 抓取数据
            # - 处理 Excel
            time.sleep(1)
        
        print("任务完成！")
        return True
        
    except Exception as e:
        print(f"任务出错：{e}")
        return False

# 执行主流程
if __name__ == "__main__":
    success = main()
    print(f"流程结束 - 成功：{success}")
```

---

## API 参考

### 初始化函数

```python
init_validator(api_base: str, shadow_account: str, heartbeat_interval: int = 300)
```
- `api_base`: API 服务器地址
- `shadow_account`: 影刀账号
- `heartbeat_interval`: 心跳间隔（秒）

### 验证函数

```python
check_license_status(raise_error: bool = True) -> dict
```
返回：
```python
{
    "status": "active",      # 状态：active/expired/banned
    "expire_at": "...",      # 到期时间
    "remain_days": 30        # 剩余天数
}
```

### 心跳函数

```python
do_heartbeat() -> dict
```
返回：
```python
{"status": "active"}
```

### 兑换函数

```python
redeem_card(card_code: str) -> dict
```
返回：
```python
{
    "success": True,
    "status": "active",
    "remain_days": 30,
    "expire_at": "..."
}
```

---

## 常见场景

### 场景 1：启动前验证

```python
from license_validator_simple import init_validator, check_license_status, LicenseError

init_validator("http://服务器 IP:8000/api", "你的账号")

try:
    result = check_license_status()
    print("授权通过，开始运行")
except LicenseError:
    print("授权失败，无法启动")
    # 退出流程
```

### 场景 2：运行时定期检查

```python
# 在循环中
for i in range(100):
    # 每 10 轮检查一次
    if i % 10 == 0:
        result = do_heartbeat()
        if result["status"] != "active":
            print("授权失效，停止运行")
            break
    
    # 你的业务逻辑
    ...
```

### 场景 3：卡密兑换

```python
from license_validator_simple import init_validator, redeem_card

init_validator("http://服务器 IP:8000/api", "你的账号")

# 用户输入卡密
card_code = input("请输入卡密：")

result = redeem_card(card_code)
if result["success"]:
    print(f"兑换成功！剩余{result['remain_days']}天")
else:
    print(f"兑换失败：{result['message']}")
```

### 场景 4：授权失效处理

```python
from license_validator_simple import init_validator, check_license_status, LicenseError
import time

init_validator("http://服务器 IP:8000/api", "你的账号")

max_retry = 3
retry_count = 0

while True:
    try:
        result = check_license_status()
        retry_count = 0  # 重置计数
        print(f"授权正常 - 剩余{result['remain_days']}天")
        
    except LicenseError as e:
        retry_count += 1
        print(f"授权异常（第{retry_count}次）: {e}")
        
        if retry_count >= max_retry:
            print("多次验证失败，停止运行")
            break
    
    time.sleep(300)  # 5 分钟检查一次
```

---

## 注意事项

1. **必须先初始化**：调用任何函数前必须先调用 `init_validator()`
2. **网络超时**：默认超时 10 秒，会自动重试 3 次
3. **异常处理**：建议用 `try-except` 捕获 `LicenseError`
4. **心跳间隔**：建议 300 秒（5 分钟），不要太频繁

---

## 测试流程

### 本地测试

1. 确保服务运行：`http://localhost:8000/api`
2. 在管理后台生成一个卡密
3. 在影刀中运行上述示例代码
4. 观察输出确认验证通过

### 影刀中调试

在影刀 Python 模块中：
1. 添加断点
2. 单步执行
3. 查看变量值
4. 检查控制台输出

---

## 部署到生产环境

1. 修改 `API_URL` 为云服务器地址
2. 确保云服务器 8000 端口可访问
3. 在影刀中保存配置
4. 运行一次完整测试

---

## 错误码说明

| 错误 | 含义 | 处理方式 |
|------|------|----------|
| `LICENSE_NOT_FOUND` | 授权不存在 | 需要先兑换卡密 |
| `LICENSE_EXPIRED` | 授权已过期 | 需要续费 |
| `LICENSE_BANNED` | 账号被禁用 | 联系管理员 |
| `NETWORK_ERROR` | 网络错误 | 检查连接，稍后重试 |
