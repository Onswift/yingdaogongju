# 影刀集成使用说明

## 模块结构

```
yingdao/
├── module_validator.py    ← 公共验证模块（不要直接运行，仅供导入）
├── module_robot.py        ← 主流程模块（可运行）
├── module_redeem.py       ← 卡密兑换模块（可运行）
└── README_YINGDAO_USAGE.md ← 本文档
```

---

## 部署步骤

### 步骤 1：在影刀中创建模块

1. 打开影刀编辑器
2. 创建 3 个 Python 模块，分别命名为：
   - `module_validator`（公共模块）
   - `module_robot`（主流程）
   - `module_redeem`（兑换模块）

### 步骤 2：复制代码

| 模块名 | 复制的文件 |
|--------|-----------|
| `module_validator` | `module_validator.py` 全部内容 |
| `module_robot` | `module_robot.py` 全部内容 |
| `module_redeem` | `module_redeem.py` 全部内容 |

### 步骤 3：修改配置

在每个模块的**配置区域**修改：

```python
API_URL = "http://你的服务器 IP:8000/api"
SHADOW_ACCOUNT = "你的影刀账号"
```

---

## 使用方法

### 场景 1：运行机器人主流程

1. 在影刀中运行 `module_robot` 模块
2. 模块会自动：
   - 初始化验证器
   - 检查授权状态
   - 执行机器人任务
   - 定期发送心跳

### 场景 2：兑换卡密

1. 在影刀中运行 `module_redeem` 模块
2. 输入卡密代码
3. 完成兑换

### 场景 3：在自己的模块中使用验证

```python
# 在你的模块开头导入
from module_validator import (
    init_validator,
    check_license_status,
    do_heartbeat,
    LicenseError
)

# 在 main 函数中调用
def main(params):
    # 初始化
    init_validator("http://服务器/api", "你的账号")
    
    # 验证授权
    try:
        result = check_license_status()
        print("授权通过")
    except LicenseError as e:
        print(f"授权失败：{e}")
        return False
    
    # 执行你的业务逻辑
    # ...
    
    return True
```

---

## 模块说明

### module_validator（公共模块）

**不要直接运行**，仅供其他模块导入使用。

提供的函数：
- `init_validator(api_base, shadow_account)` - 初始化验证器
- `check_license_status()` - 检查授权状态
- `do_heartbeat()` - 发送心跳
- `redeem_card(card_code)` - 兑换卡密
- `LicenseError` - 授权异常类

### module_robot（主流程模块）

**可以运行**，是机器人的主流程。

流程：
1. 初始化验证器
2. 验证授权
3. 执行任务（每 3 轮发送一次心跳）
4. 完成任务

### module_redeem（兑换模块）

**可以运行**，用于兑换卡密。

流程：
1. 初始化验证器
2. 获取卡密（预设或手动输入）
3. 兑换卡密
4. 显示结果

---

## 配置说明

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `API_URL` | 授权服务器地址 | `http://localhost:8000/api` |
| `SHADOW_ACCOUNT` | 影刀账号 | `my_account` |
| `CARD_CODE` | 预设卡密（兑换模块用） | `LIC-XXXX-XXXX` |

---

## 常见问题

### Q1: 提示 "module_validator not found"
**A:** 确保 `module_validator` 模块已经创建并保存

### Q2: 授权验证失败
**A:** 
1. 检查服务器是否运行
2. 检查账号是否正确
3. 检查是否已兑换卡密

### Q3: 心跳失败
**A:** 
1. 检查网络连接
2. 检查服务器地址是否正确
3. 确认账号有有效授权

---

## 测试流程

1. **启动本地服务**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

2. **生成测试卡密**
   - 访问 `http://localhost:8000/admin`
   - 生成一个测试卡密

3. **兑换卡密**
   - 在影刀中运行 `module_redeem`
   - 输入卡密完成兑换

4. **运行主流程**
   - 在影刀中运行 `module_robot`
   - 观察输出确认验证通过

---

## 注意事项

1. **模块依赖**：`module_robot` 和 `module_redeem` 依赖 `module_validator`
2. **配置一致**：确保所有模块的配置（API_URL、账号）一致
3. **不要修改**：`module_validator` 不要直接运行，只供导入
4. **main 函数**：可运行的模块必须有 `main(params)` 函数
