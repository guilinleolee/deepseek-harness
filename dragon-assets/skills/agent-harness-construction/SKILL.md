---
license: UNKNOWN
name: agent-harness-construction
description: Design and optimize AI agent action spaces, tool definitions, and observation formatting for higher completion rates.
github_repo: affaan-m/everything-claude-code
github_hash: 4e66b2882da9afb9747468b08a253ca2f09c85f3
last_updated: 2026-04-25
source_type: derived
origin: ECC (everything-claude-code)
triggers: ["agent harness construction", "Agent Harness Construction Skill"]
---

# Agent Harness Construction Skill

> 来源: [affaan-m/everything-claude-code/agent-harness-construction](https://github.com/affaan-m/everything-claude-code)

## 功能概述

设计和优化 AI Agent 的动作空间、工具定义和观察格式，以提高任务完成率。

## 核心模型

Agent 输出质量受以下四个维度约束：

```
┌─────────────────────────────────────────────────────────────┐
│  Agent 输出质量四维度                                       │
├─────────────────────────────────────────────────────────────┤
│  1. Action Space Quality    - 动作空间质量                  │
│  2. Observation Quality     - 观察质量                      │
│  3. Recovery Quality       - 错误恢复质量                  │
│  4. Context Budget Quality - 上下文预算质量               │
└─────────────────────────────────────────────────────────────┘
```

## 动作空间设计原则

### 1. 工具命名规范
- 使用稳定、明确的工具名称
- 避免语义重叠的工具

### 2. 输入规范
- 保持输入 schema-first（类型优先）
- 缩小输入范围，降低模糊性

### 3. 输出格式
- 返回确定性的输出形状
- 保证输出可解析

### 4. 粒度规则

| 粒度 | 使用场景 | 示例 |
|------|---------|------|
| **Micro-Tools** | 高风险操作 | deploy, migration, permissions |
| **Medium-Tools** | 常用编辑/读取/搜索循环 | file_read, grep, search |
| **Macro-Tools** | 往返开销占主导时 | batch_process, full_index |

## 观察设计规范

每个工具响应必须包含：

```yaml
status: success|warning|error      # 状态标识
summary: "单行结果描述"              # 一句话总结
next_actions:                         # 可执行的跟进操作
  - "action 1"
  - "action 2"
artifacts:                            # 产物路径
  - file_path
  - id
```

## 错误恢复契约

每个错误路径必须包含：

```yaml
error:
  root_cause_hint: "根本原因提示"    # 原因猜测
  retry_instruction: "安全重试指令"   # 如何重试
  stop_condition: "显式停止条件"     # 何时停止
```

## 上下文预算

| 策略 | 说明 |
|------|------|
| **Minimal System Prompt** | 保持系统提示最小化和不变 |
| **On-Demand Skills** | 将大型指导移至按需加载的技能 |
| **References Over Inline** | 优先引用文件而非内联长文档 |
| **Phase Boundaries** | 在阶段边界压缩，而非任意 Token 阈值 |

## 架构模式

### 三种模式对比

| 模式 | 适用场景 | 推荐度 |
|------|---------|--------|
| **ReAct** | 探索性任务，路径不确定 | ⭐⭐ |
| **Function-calling** | 结构化确定性流程 | ⭐⭐⭐ |
| **Hybrid** (推荐) | ReAct 规划 + 类型化工具执行 | ⭐⭐⭐⭐⭐ |

### Hybrid 模式架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Hybrid Agent 架构                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│    Planning (ReAct)                                         │
│         ↓                                                   │
│    ┌─────────────────────────────────────────────────┐    │
│    │  Tool Selection (Function-calling)                │    │
│    │  ├── Read        (Typed)                        │    │
│    │  ├── Edit        (Typed)                        │    │
│    │  ├── Bash       (Typed)                        │    │
│    │  └── Write      (Typed)                        │    │
│    └─────────────────────────────────────────────────┘    │
│         ↓                                                   │
│    Observation → Next Action                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 基准测试指标

| 指标 | 说明 | 目标 |
|------|------|------|
| **Completion Rate** | 任务完成率 | > 90% |
| **Retries per Task** | 每任务重试次数 | < 2 |
| **pass@1** | 首次成功率 | > 70% |
| **pass@3** | 3次内成功率 | > 90% |
| **Cost per Success** | 每次成功成本 | 优化 |

## 反模式

| 反模式 | 问题 | 解决方案 |
|--------|------|---------|
| **语义重叠工具** | 决策困惑 | 合并或分离 |
| **不透明输出** | 无法恢复 | 添加 next_actions |
| **纯错误输出** | 死胡同 | 包含 recovery_hint |
| **上下文过载** | 性能下降 | 阶段边界压缩 |

## 天龙引擎集成

### 适用岗位

| 岗位 | 集成方式 | 增强能力 |
|------|---------|---------|
| **03构建师** | 工具设计原则 | Agent 构建质量 |
| **10-02 AI研究员** | 架构模式 | 新型 Agent 设计 |
| **02架构师** | 观察设计 | 系统可观测性 |

### 调用示例

```bash
# 设计新工具时
[@构建师] 使用 agent-harness-construction 设计一个代码审查工具

# 优化现有 Agent
[@AI研究员] 使用 action-space-design 优化这个 Agent 的工具集

# 评估工具质量
[@架构师] 使用 observation-design 检查工具输出规范
```

## 参考资料

- [Everything Claude Code](https://github.com/affaan-m/everything-claude-code)
- [ECC agent-harness-construction](https://github.com/affaan-m/everything-claude-code/tree/main/skills/agent-harness-construction)

---

**版本**: V1.0 | **兼容性**: 天龙引擎 V8.65+ | **来源**: ECC

