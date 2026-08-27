---
name: nine-dragons-plan-status
description: "查看九部天龙任务进度 - 阶段状态、成本统计、错误追踪"
invokable: true
---
# 九部天龙任务状态查看

> 一目了然的进度追踪和成本统计

读取项目根目录的task_plan.md并显示紧凑状态摘要。

## 📋 显示内容

### 1. 当前阶段
- 从"## Current Phase"提取
- 显示当前在第几个阶段

### 2. 阶段进度
- 统计各阶段状态(pending/in_progress/complete)
- 计算完成百分比

### 3. 阶段列表
- 显示每个阶段及对应宗师
- 用图标标识状态

### 4. 成本统计
- 预估成本 vs 实际成本
- 最贵/最省阶段
- 总成本汇总

### 5. 错误追踪
- Errors Encountered表中的错误数量
- 最近3个错误

### 6. 文件检查
- 确认3个规划文件是否存在

## 🎨 状态图标

| 状态 | 图标 | 说明 |
|------|------|------|
| pending | ⏸️ | 未开始 |
| in_progress | 🔄 | 进行中 |
| complete | ✅ | 已完成 |
| failed | ❌ | 失败 |
| blocked | 🚫 | 阻塞 |

## 📊 输出格式

```markdown
📋 九部天龙任务状态

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 当前位置: Phase 3 of 7 (42%)
🔄 状态: 进行中

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 阶段进度:

  ✅ Phase 1: Requirements & Discovery (00分析师)
  ✅ Phase 2: Research & Investigation (01调研师)
  🔄 Phase 3: Architecture & Design (02架构师) ← 你在这里
  ⏸️ Phase 4: Implementation (03构建师)
  ⏸️ Phase 5: Testing & Verification (04验证师)
  ⏸️ Phase 6: Code Review (06审查师)
  ⏸️ Phase 7: Delivery (08发布师)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 成本统计:

| 阶段 | 预估 | 实际 | 模型 | 宗师 |
|------|------|------|------|------|
| Phase 1 | $0.01-0.02 | $0.015 | Sonnet | 00analyst |
| Phase 2 | $0.015-0.025 | $0.020 | Sonnet | 01investigator |
| Phase 3 | $0.03-0.05 | $0.040 | Opus | 02architect |
| Phase 4 | $0.02-0.04 | - | Codex | 03builder |
| Phase 5 | $0.02-0.03 | - | Sonnet | 04validator |
| Phase 6 | $0-0.05 | - | Gemini | 06code-reviewer |
| Phase 7 | $0.01 | - | Sonnet | 08publisher |

💵 总成本: $0.075 / $0.105-0.215 (35%)
📊 已完成: 2/7 阶段
⏱️ 预计剩余: $0.03-0.14

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 文件状态:
✅ task_plan.md
✅ findings.md
✅ progress.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 错误追踪:
总计: 3个错误

最近3个:
1. [2026-02-19 10:35] FileNotFoundError - Phase 1
2. [2026-02-19 10:37] JSONDecodeError - Phase 1
3. [2026-02-19 11:15] ValidationError - Phase 2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 建议下一步:
- 继续Phase 3: 架构设计
- 使用Opus模型获得最佳架构决策
- 完成后更新task_plan.md状态为complete
```

## 🔍 如果没有规划文件

```markdown
📋 未找到规划文件

请在项目根目录运行 /plan 命令创建新的规划会话。

或者:
1. 检查是否在正确的项目目录
2. 确认task_plan.md是否存在
```

## 💡 使用场景

### 场景1: 上下文恢复
```
用户: /plan:status

📋 你在Phase 3(架构设计),已完成2/7阶段
🎯 下一步: 继续Phase 3,使用Opus模型
```

### 场景2: 成本检查
```
用户: /plan:status

💰 已花费$0.075,预计还需$0.03-0.14
💡 成本敏感? 可以考虑:
  - Phase 4用Sonnet代替Codex
  - Phase 6用Gemini(免费)代替Opus
```

### 场景3: 进度汇报
```
用户: /plan:status

📊 任务完成度: 28% (2/7阶段)
✅ 已完成: 需求分析、考古摸底
🔄 进行中: 架构设计
⏸️ 待完成: 4个阶段
```

---

## ⚙️ 实现细节

### 读取task_plan.md

```javascript
// 1. 读取文件
const content = fs.readFileSync('task_plan.md', 'utf8');

// 2. 提取Current Phase
const currentPhaseMatch = content.match(/## Current Phase\n*(Phase \d+)/);
const currentPhase = currentPhaseMatch ? currentPhaseMatch[1] : '未设置';

// 3. 统计阶段状态
const total = (content.match(/### Phase/g) || []).length;
const complete = (content.match(/\*\*Status:\*\* complete/g) || []).length;
const inProgress = (content.match(/\*\*Status:\*\* in_progress/g) || []).length;
const pending = (content.match(/\*\*Status:\*\* pending/g) || []).length;

// 4. 提取Cost Summary
// (正则匹配Cost Summary表格)

// 5. 提取Errors Encountered
// (正则匹配Errors Encountered表格)
```

### 显示优化

- 使用表格对齐成本数据
- 用进度条图标表示完成度
- 高亮当前阶段(← 你在这里)
- 按时间倒序显示最近错误

---

## 📚 相关命令

- `/plan` - 创建新规划
- `/nine-dragons-help` - 智能助手
- `/nine-dragons-cost-opt` - 成本优化建议

---

## 🔧 技术说明

此命令应该:
1. 快速读取(不重读整个文件,只提取关键信息)
2. 缓存友好(相同查询不重复计算)
3. 错误容忍(文件不存在或格式错误时优雅降级)
4. 视觉清晰(用表格、图标、进度条增强可读性)
