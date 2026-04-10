# 影刀集成使用说明（单文件版本）

## 文件说明

```
yingdao/
├── license_module.py    ← 单文件完整版本（推荐使用）
└── README_SINGLE_FILE.md ← 本文档
```

---

## 快速开始（3 步）

### 步骤 1：复制代码

将 `license_module.py` 的**全部内容**复制到影刀的一个 Python 模块中。

建议模块命名为：`license_module` 或 `授权验证模块`

### 步骤 2：修改配置

在影刀中修改模块开头的配置：

```python
API_URL = "http://你的服务器 IP:8000/api"
SHADOW_ACCOUNT = "你的影刀账号"
```

### 步骤 3：运行

在影刀中运行该模块即可。

---

## 模块功能

这个单文件模块包含 3 个可运行的流程：

| 流程函数 | 用途 | 调用方式 |
|----------|------|----------|
| `main(params)` | 机器人主流程 | 直接运行模块 |
| `redeem(params)` | 卡密兑换 | 运行模块选择此函数 |
| `test(params)` | 功能测试 | 运行模块选择此函数 |

---

## 使用方法

### 方式 1：直接运行模块

1. 在影刀中打开该模块
2. 点击运行
3. 默认执行 `main(params)` 函数

### 方式 2：在其他模块中调用

```python
# 在你的模块中导入函数
from license_module import main, redeem, test

# 调用主流程
main(params)

# 或调用兑换流程
redeem(params)

# 或调用测试流程
test(params)
```

### 方式 3：作为库使用（高级）

```python
# 导入验证器类
from license_module import LicenseValidator, LicenseError

# 创建验证器
validator = LicenseValidator("http://服务器/api", "你的账号")

# 验证授权
try:
    result = validator.check_license()
    print("授权通过")
except LicenseError:
    print("授权失败")
```

---

## 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `API_URL` | 授权服务器地址 | `http://localhost:8000/api` |
| `SHADOW_ACCOUNT` | 影刀账号 | `test_user` |
| `CARD_CODE` | 预设卡密（兑换用） | `""`（空） |
| `ENABLE_HEARTBEAT` | 是否启用心跳 | `True` |
| `HEARTBEAT_INTERVAL` | 心跳间隔（轮数） | `3` |

---

## 测试流程

### 1. 启动本地服务

```bash
# 在项目目录运行
python -m uvicorn app.main:app --reload
```

### 2. 生成测试卡密

1. 访问 `http://localhost:8000/admin`
2. 输入 Token: `dev-token`
3. 选择卡密类型，生成卡密
4. 记录卡密代码

### 3. 在影刀中测试

1. 复制 `license_module.py` 到影刀
2. 修改 `API_URL = "http://localhost:8000/api"`
3. 修改 `SHADOW_ACCOUNT = "test_user"`
4. 运行 `test(params)` 测试功能
5. 运行 `redeem(params)` 兑换卡密
6. 运行 `main(params)` 执行主流程

---

## 在自己的机器人中使用

### 方法 A：完整使用

```python
# 在你的模块开头
from license_module import LicenseError

# 在 main 函数中
def main(params):
    # 初始化验证器（使用全局变量）
    import license_module
    license_module.API_URL = "http://服务器/api"
    license_module.SHADOW_ACCOUNT = "你的账号"
    license_module._init_validator(
        license_module.API_URL,
        license_module.SHADOW_ACCOUNT
    )

    # 验证授权
    try:
        result = license_module._get_validator().check_license()
        print("授权通过")
    except LicenseError as e:
        print(f"授权失败：{e}")
        return False

    # 你的业务逻辑
    # ...

    return True
```

### 方法 B：简单使用（推荐）

直接复制 `license_module.py` 后，只修改配置，然后运行 `main(params)`。

---

## 错误排查

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 网络错误 | 服务器未启动 | 检查服务是否运行 |
| 授权不存在 | 账号无授权 | 先兑换卡密 |
| 卡密已使用 | 卡密已兑换 | 使用新卡密 |
| 模块导入失败 | 模块名不对 | 确保模块命名正确 |

---

## 注意事项

1. **必须修改配置**：使用前必须修改 `API_URL` 和 `SHADOW_ACCOUNT`
2. **影刀输入**：`input()` 在影刀中可能需要使用影刀的输入组件
3. **心跳间隔**：建议设置为 3-5，不要每轮都检查
4. **超时设置**：网络请求超时为 10 秒
