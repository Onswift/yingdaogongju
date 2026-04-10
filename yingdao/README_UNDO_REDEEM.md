# 防误操作功能说明

## 功能概述

为防止用户误操作（同一账号重复兑换卡密），实现了以下功能：

### 方案 1：兑换前检查 ✅

在兑换卡密前，检查该账号是否已有有效授权，如有则提示警告。

### 方案 2：撤销兑换功能 ✅

在管理后台可以撤销误操作的兑换，恢复卡密并扣除相应授权天数。

---

## API 改动

### 1. 兑换接口 `/api/redeem`

**新增返回字段**：
```python
{
    "success": True,
    "status": "active",
    "remain_days": 365,
    "expire_at": "2027-04-08T12:00:00",
    "has_existing_license": True,    # 是否已有授权
    "old_expire_at": "2026-05-08",   # 原到期时间
    "added_days": 365                # 本次增加的天数
}
```

---

### 2. 撤销兑换接口 `/admin/licenses/undo-redeem`

**请求**：
```json
POST /admin/licenses/undo-redeem
{
    "card_code": "LIC-XXXX-XXXX",
    "shadow_account": "test_user"
}
```

**响应**：
```python
# 成功
{
    "code": 0,
    "message": "已撤销兑换，扣除 365 天授权"
}

# 失败
{
    "code": 1001,
    "message": "该卡密不是此账号兑换的"
}
```

---

## 影刀模块改动

### module_redeem_card.py

**新增功能**：
1. 兑换前自动检查账号是否已有授权
2. 如有授权，返回警告信息
3. 可通过 `force_redeem=True` 参数跳过警告

**返回结果**：
```python
# 首次兑换
{
    "success": True,
    "status": "active",
    "remain_days": 30,
    "expire_at": "...",
    "has_existing_license": False,
    "message": ""
}

# 累加兑换
{
    "success": True,
    "status": "active",
    "remain_days": 120,
    "expire_at": "...",
    "has_existing_license": True,
    "old_expire_at": "...",
    "added_days": 90,
    "warning": "累加兑换成功！原授权 +90 天"
}

# 已有授权（需要确认）
{
    "success": False,
    "need_confirm": True,
    "warning": "该账号已有有效授权（剩余 30 天，到期：2026-05-08）",
    "current_status": "active",
    "current_remain_days": 30,
    "current_expire_at": "2026-05-08",
    "message": "检测到账号已有授权，继续兑换将累加天数。请确认后再次尝试（设置 force_redeem=True）。"
}
```

---

## 管理后台改动

### 卡密列表

**新增"撤销"按钮**：
- 仅对"已使用"状态的卡密显示
- 点击后弹出确认对话框
- 撤销后：
  - 卡密恢复为"未使用"状态
  - 该账号的授权天数扣除相应天数
  - 授权列表自动刷新

---

## 使用流程

### 正常兑换流程

```
1. 用户输入账号和卡密
   ↓
2. 调用 module_redeem_card
   ↓
3. 模块自动检查是否有授权
   ↓
4a. 无授权 → 直接兑换
4b. 有授权 → 返回警告 → 用户确认后再次调用（force_redeem=True）
   ↓
5. 完成兑换
```

### 撤销兑换流程

```
1. 管理员发现误操作
   ↓
2. 打开管理后台
   ↓
3. 在卡密列表找到该卡密
   ↓
4. 点击"撤销"按钮
   ↓
5. 确认撤销
   ↓
6. 卡密恢复未使用，授权天数扣除
```

---

## 影刀中使用示例

### 方式 1：简单调用（无确认）

```python
from module_redeem_card import main as redeem

params = type('Params', (), {
    'shadow_account': 'test_user',
    'card_code': 'LIC-XXXX-XXXX'
})()

result = redeem(params)

if result.get("need_confirm"):
    # 显示警告，让用户确认
    print(result.get("warning"))
    # 用户确认后再次调用
    params = type('Params', (), {
        'shadow_account': 'test_user',
        'card_code': 'LIC-XXXX-XXXX',
        'force_redeem': True
    })()
    result = redeem(params)
```

### 方式 2：带确认流程

```
开始
  ↓
[输入] 账号、卡密
  ↓
[Python] 兑换卡密 (module_redeem_card)
  ↓
判断：result.need_confirm?
  ├─ 是 → [弹窗] 显示警告，询问是否继续
  │        ↓
  │     判断：用户确认？
  │        ├─ 是 → 再次调用（force_redeem=True）
  │        └─ 否 → 结束
  │
  └─ 否 → 判断：result.success?
           ├─ 是 → 显示成功
           └─ 否 → 显示错误
```

---

## 注意事项

1. **撤销限制**：
   - 只能撤销"已使用"状态的卡密
   - 卡密必须属于该账号
   - 撤销后天数为负数会导致授权过期

2. **兑换检查**：
   - 只检查"active"状态的授权
   - 过期或被禁用的授权不会触发警告

3. **数据一致性**：
   - 撤销操作会写入日志
   - 建议只在误操作后立即使用

---

## 测试建议

1. **测试重复兑换检查**：
   - 用一个账号兑换两次卡密
   - 观察第一次是否正常，第二次是否有警告

2. **测试撤销功能**：
   - 兑换一个卡密
   - 在管理后台点击"撤销"
   - 检查卡密是否恢复、授权是否扣除

3. **测试 force_redeem**：
   - 有授权的情况下，设置 `force_redeem=True`
   - 观察是否正常累加
