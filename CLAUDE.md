# AURA-X-KYS-CLI (融合 KISS/YAGNI/SOLID - 命令行版)

## 核心理念

本协议旨在指导一个集成在 IDE 中的超智能 AI 编程助手设计的终极控制与协作框架。它在 AURA-X 的自适应性和上下文感知能力之上，融合三大工程原则：

### **KISS (Keep It Simple, Stupid)**
- 优先选择最简单的解决方案
- 避免过度设计
- 代码清晰优于聪明技巧

### **YAGNI (You Aren't Gonna Need It)**
- 不要添加当前不需要的功能
- 拒绝假设性需求
- 按需实现，拒绝预判

### **SOLID**
- **S**ingle Responsibility - 单一职责
- **O**pen/Closed - 开闭原则
- **L**iskov Substitution - 里氏替换
- **I**nterface Segregation - 接口隔离
- **D**ependency Inversion - 依赖倒置

---

## 工作模式

### 默认行为
1. **先理解，后行动** - 修改任何代码前先读取并理解
2. **最小改动** - 每次只解决一个问题
3. **确认驱动** - 不确定时先询问用户

### 命令式交互

```bash
# 查看项目状态
/status

# 执行任务
执行 --task "重构用户模块" --principle "SOLID"

# 代码审查
review --file "app/main.py" --focus "security,performance"

# 生成文档
doc --scope "api" --format "markdown"
```

---

## 工程原则

### 1. 代码质量
- 函数不超过 50 行
- 类不超过 500 行
- 嵌套不超过 3 层
- 必须有错误处理

### 2. 测试要求
- 新功能必须附带测试
- 测试覆盖率 > 80%
- 优先集成测试

### 3. 安全要求
- 不提交敏感信息
- 输入必须验证
- SQL 必须参数化

### 4. 性能要求
- N+1 查询必须优化
- 大数据集必须分页
- 缓存策略必须明确

---

## 项目上下文

当前项目：授权管理系统
- 后端：FastAPI + SQLAlchemy + SQLite
- 前端：纯 HTML + JavaScript
- 部署：Alibaba Cloud Linux + uvicorn
- 端口：8001

---

## 交互规范

### 回复风格
- 简洁直接，不赘述
- 代码优先，解释为辅
- 错误信息完整

### 禁止行为
- 不要主动添加注释
- 不要重构未要求的代码
- 不要使用 emoji
- 不要估计时间

### 必须确认
- 删除文件/数据前
- 修改配置文件前
- 推送代码到远程前
- 添加新依赖前

---

## 命令参考

| 命令 | 说明 |
|------|------|
| `/help` | 获取帮助 |
| `/status` | 查看项目状态 |
| `/review` | 代码审查 |
| `/test` | 运行测试 |
| `/deploy` | 部署项目 |

---

## 特殊指令

```
--dry-run    # 模拟执行，不实际修改
--verbose    # 详细输出
--force      # 强制执行（需用户确认）
--rollback   # 回滚上次操作
```

---

**版本**: 1.0
**最后更新**: 2026-04-11
