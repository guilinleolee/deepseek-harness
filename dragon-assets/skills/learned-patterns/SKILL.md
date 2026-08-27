---
license: UNKNOWN
triggers: ["learned patterns", "Learned Patterns - 九部经验积累系统"]
---
# Learned Patterns - 九部经验积累系统

## L0: 一句话描述
每个Agent积累领域特定经验的有效模式和反模式，避免重复犯错。

## L1: 使用场景

### 触发条件
- **新任务开始时**: 查看是否有相关经验
- **任务完成时**: 记录有效经验和反模式
- **遇到困难时**: 搜索类似问题的解决方案
- **复盘时**: 分析失败原因，更新模式库

### 适用Agent
天龙九部（00-09）各自维护独立的经验积累。

## L2: 详细文档

### 核心理念

Learned Patterns源自Professor Synapse，每个Agent都应该积累：
- **Effective Patterns（有效模式）**: 在该领域被验证有效的做法
- **Anti-Patterns（反模式）**: 该领域中容易导致问题的做法

```
┌─────────────────────────────────────────────────────────────┐
│              Learned Patterns 双层架构                         │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: lessons.md (全局经验)                             │
│    - 跨Agent通用经验                                        │
│    - 重大教训                                               │
│    - 硬编码模式                                             │
│                                                             │
│  Layer 2: learned-patterns.md (Agent级经验) ← 本技能      │
│    - Agent特定领域经验                                       │
│    - 细微差别                                               │
│    - 模式演变                                               │
└─────────────────────────────────────────────────────────────┘
```

### 九部经验积累目录

```
天龙九部各自的经验积累:
├── 00分析师/
│   ├── learned-patterns.md    # 问题分析模式
│   └── case-studies.md        # 案例研究
├── 01调研师/
│   ├── learned-patterns.md    # 调研方法模式
│   └── domain-patterns.md     # 领域知识
├── 02架构师/
│   ├── learned-patterns.md    # 架构决策模式
│   └── tradeoffs.md          # 权衡案例
├── 03构建师/
│   ├── learned-patterns.md    # 代码实现模式
│   └── refactoring.md         # 重构经验
├── 04验证师/
│   ├── learned-patterns.md    # 测试验证模式
│   └── bugs.md               # Bug模式库
├── 05安全师/
│   ├── learned-patterns.md    # 安全模式
│   └── vulnerabilities.md     # 漏洞模式
├── 06审查师/
│   ├── learned-patterns.md    # 审查模式
│   └── review-checklists.md   # 审查清单
├── 07记录师/
│   ├── learned-patterns.md    # 文档模式
│   └── templates.md           # 模板库
├── 08发布师/
│   ├── learned-patterns.md    # 发布模式
│   └── incidents.md           # 事故案例
└── 09编排协调师/
    ├── learned-patterns.md    # 编排模式
    └── orchestrations.md     # 编排案例
```

### Learned Patterns标准格式

```markdown
# [Agent名称] Learned Patterns

## 📅 最后更新: YYYY-MM-DD

---

## ✅ Effective Patterns (有效模式)

### Pattern 1: [模式名称]
**发现场景**: [在什么情况下发现这个模式]
**做法**: [具体有效的做法]
**效果**: [带来的好处]
**验证**: [已验证次数] | [最近验证日期]

### Pattern 2: [模式名称]
...

---

## ❌ Anti-Patterns (反模式)

### Anti-Pattern 1: [反模式名称]
**问题场景**: [在什么情况下出现问题]
**问题表现**: [具体问题]
**根本原因**: [为什么会导致问题]
**解决方案**: [如何避免/修复]
**教训**: [从中学到的核心教训]

### Anti-Pattern 2: [反模式名称]
...

---

## 🔄 Pattern版本历史

| 版本 | 日期 | 变更 | 原因 |
|------|------|------|------|
| v1.0 | YYYY-MM-DD | 初始创建 | - |
| v1.1 | YYYY-MM-DD | 新增Pattern | 发现新有效模式 |
```

### Pattern记录模板

```markdown
### Pattern-N: [名称]
**类型**: ✅有效模式 / ❌反模式
**领域**: [问题分析/架构设计/代码实现...]
**发现时间**: YYYY-MM-DD
**发现任务**: [相关任务描述]

**描述**:
[详细描述]

**适用条件**:
- 当[条件1]时
- 当[条件2]时

**不适用**:
- 当[排除条件1]时
- 当[排除条件2]时

**相关Pattern**:
- Pattern-X (类似但不同)
- Anti-Pattern-Y (相反做法)

**验证记录**:
| 日期 | 任务 | 结果 | 备注 |
|------|------|------|------|
| | | ✅成功/⚠️部分/❌失败 | |
```

## 与其他系统的协同

### 与lessons.md协同

```yaml
# lessons.md (全局经验)
优先级: P0
适用范围: 跨Agent通用教训
记录标准: 四条铁律
  - 需要发现 (非文档查询)
  - 可复用 (有助于未来任务)
  - 明确触发条件 (具体错误/症状)
  - 已验证 (实际有效)

# learned-patterns.md (Agent级经验)
优先级: P1
适用范围: Agent特定领域
记录标准: 五要素
  - 模式名称
  - 适用条件
  - 具体做法
  - 效果评估
  - 版本追踪
```

### 与Convener Protocol协同

```
Convener辩论 → 发现某方案经常失败
    ↓
检查相关Agent的learned-patterns.md
    ↓
利用反模式避免重复踩坑
    ↓
辩论结果加入新模式
```

## 使用命令

```bash
# 搜索相关模式
grep -r "[关键词]" skills/learned-patterns/*/learned-patterns.md

# 查看特定Agent模式
cat skills/learned-patterns/00分析师/learned-patterns.md

# 添加新模式（使用标准格式）
# 参考上述Pattern记录模板

# 更新反模式
# 记录问题场景、根本原因、解决方案
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-04-18 | 初始版本，基于Professor Synapse Learned Patterns |
