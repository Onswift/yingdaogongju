# 影刀授权验证 - 模块化版本使用说明

## 模块结构

```
yingdao/
├── module_check_license.py    ← 授权验证模块
├── module_redeem_card.py      ← 卡密兑换模块
├── module_heartbeat.py        ← 心跳上报模块
├── module_robot_main.py       ← 主流程示例
└── README_MODULES.md          ← 本文档
```

---

## 模块说明

### 1. module_check_license（授权验证）

**功能**：验证影刀账号的授权状态

**输入参数**：
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| shadow_account | string | 是 | 影刀账号 |

**返回结果**：
```python
{
    "success": True,
    "status": "active",
    "remain_days": 30,
    "expire_at": "2026-05-08T12:00:00",
    "message": ""
}
```

---

### 2. module_redeem_card（卡密兑换）

**功能**：兑换卡密

**输入参数**：
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| shadow_account | string | 是 | 影刀账号 |
| card_code | string | 是 | 卡密代码 |

**返回结果**：
```python
{
    "success": True,
    "status": "active",
    "remain_days": 365,
    "expire_at": "2027-04-08T12:00:00",
    "message": ""
}
```

---

### 3. module_heartbeat（心跳上报）

**功能**：发送心跳上报

**输入参数**：
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| shadow_account | string | 是 | 影刀账号 |

**返回结果**：
```python
{
    "success": True,
    "status": "active",
    "message": ""
}
```

---

## 部署步骤

### 步骤 1：在影刀中创建模块

1. 打开影刀编辑器
2. 创建 4 个 Python 模块，分别命名为：
   - `module_check_license`
   - `module_redeem_card`
   - `module_heartbeat`
   - `module_robot_main`（可选，示例用）

### 步骤 2：复制代码

将对应的 `.py` 文件内容复制到影刀的模块中

### 步骤 3：修改配置

在每个模块开头的**配置区域**修改：
```python
API_URL = "http://你的服务器 IP:8000/api"
```

---

## 使用方法

### 方式 1：单独调用某个模块

在影刀流程中：

1. **添加 Python 模块**节点
2. 选择对应的模块
3. 设置输入参数
4. 获取返回结果

示例（验证授权）：
```
Python 模块：module_check_license
输入参数：
    shadow_account = "test_user"
返回结果：result = 模块输出
```

---

### 方式 2：在另一个模块中调用

```python
# 调用授权验证
from module_check_license import main as check_license

params = type('Params', (), {'shadow_account': 'test_user'})()
result = check_license(params)

if result.get("success"):
    print(f"授权通过 - 剩余{result['remain_days']}天")
else:
    print(f"授权失败：{result['message']}")
```

---

### 方式 3：运行主流程示例

直接运行 `module_robot_main` 模块：

```
Python 模块：module_robot_main
输入参数（可选）：
    shadow_account = "你的账号"
    card_code = "卡密代码"
```

---

## 使用示例

### 示例 1：验证授权

```
1. 添加「Python 模块」节点
2. 选择：module_check_license
3. 设置参数：shadow_account = "test_user"
4. 输出：result
5. 添加「打印」节点：result.message
```

### 示例 2：兑换卡密

```
1. 添加「Python 模块」节点
2. 选择：module_redeem_card
3. 设置参数：
   - shadow_account = "test_user"
   - card_code = "LIC-XXXX-XXXX"
4. 输出：result
5. 判断：如果 result.success == True，继续执行
```

### 示例 3：完整流程

```
开始
  ↓
[Python] 验证授权 (module_check_license)
  ↓
判断：result.success?
  ├─ 是 → 执行机器人任务
  │        ↓
  │     [循环] 每 3 轮发送心跳 (module_heartbeat)
  │        ↓
  │     结束
  │
  └─ 否 → [Python] 兑换卡密 (module_redeem_card)
           ↓
         判断：兑换成功？
           ├─ 是 → 执行机器人任务
           └─ 否 → 结束（提示错误）
```

---

## 在影刀中设置参数

### 方法 1：直接在节点中设置

在影刀的流程设计器中：
1. 选中「Python 模块」节点
2. 在右侧属性面板找到「输入参数」
3. 添加参数：
   - 名称：`shadow_account`
   - 值：`test_user`

### 方法 2：使用变量

1. 先添加「变量设置」节点
2. 设置变量：`shadow_account = "test_user"`
3. 在「Python 模块」节点引用变量

### 方法 3：从 Excel 读取

1. 添加「读取 Excel」节点
2. 读取账号列表
3. 循环调用验证模块

---

## 返回值处理

每个模块返回的都是字典 (dict)，可以这样处理：

```python
# 在 Python 模块中处理返回值
result = 上一个模块的输出

# 判断是否成功
if result.get("success"):
    # 成功
    status = result.get("status")
    days = result.get("remain_days")
else:
    # 失败
    error_msg = result.get("message")
```

---

## 测试流程

### 1. 测试授权验证

```
模块：module_check_license
参数：shadow_account = "test_user"
预期：如果账号有授权，返回 success=True
```

### 2. 测试卡密兑换

```
模块：module_redeem_card
参数：
    shadow_account = "test_user"
    card_code = "LIC-XXXX-XXXX"（从管理后台获取）
预期：兑换成功，返回 success=True
```

### 3. 测试心跳

```
模块：module_heartbeat
参数：shadow_account = "test_user"
预期：返回 success=True, status="active"
```

---

## 注意事项

1. **每个模块都要配置 API_URL**
2. **参数名称必须正确**（shadow_account, card_code）
3. **返回值是字典**，需要用 .get() 方法获取
4. **影刀中的参数传递**需要在节点属性中设置

---

## 常见问题

**Q: 如何查看返回结果？**
A: 在影刀中添加「打印」节点，输出模块的返回值

**Q: 如何在流程中使用返回结果？**
A: 后续节点可以通过 `上一步输出.参数名` 来获取

**Q: 参数传递失败？**
A: 检查参数名称是否正确（必须是 shadow_account）

**Q: 网络错误？**
A: 检查 API_URL 是否正确，服务器是否运行
