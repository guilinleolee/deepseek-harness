---
license: UNKNOWN
triggers: ["openspace evolution orchestrator", "OpenSpace Evolution Orchestrator"]
---
# OpenSpace Evolution Orchestrator

## 功能描述

OpenSpace Evolution Orchestrator 是天龙引擎的自演化编排核心，负责协调 165 个自演化 Skills 的 FIX/DERIVED/CAPTURED 三种演化模式。

### 核心能力

- **三重演化模式**: FIX（修复缺陷）、DERIVED（派生新技能）、CAPTURED（捕获工作流）
- **Confirmation Gates**: 演化前确认机制，确保每次演化都有明确的目标和验证标准
- **Anti-loop Guards**: 防循环机制，防止在同一问题上无限演化

### 演化流程

```
┌─────────────────────────────────────────────────────────────┐
│                    Evolution Orchestrator                     │
├─────────────────────────────────────────────────────────────┤
│  1. 检测演化信号                                            │
│     ├── 连续失败 (≥3次) → FIX 模式                         │
│     ├── 重复任务模式 → DERIVED 模式                        │
│     └── 有效工作流 → CAPTURED 模式                          │
│                                                             │
│  2. Confirmation Gate (确认门控)                            │
│     ├── 演化目标明确性验证                                   │
│     ├── 预期结果定义                                        │
│     └── 退出条件设定                                        │
│                                                             │
│  3. Anti-loop Guard (防循环守卫)                            │
│     ├── 演化历史追踪                                        │
│     ├── 相似解检测                                          │
│     └── 循环终止判断                                        │
│                                                             │
│  4. 执行演化                                                │
│     └── 调用 SkillEvolver 完成具体演化                       │
└─────────────────────────────────────────────────────────────┘
```

## 使用方式

```bash
# 启动自演化编排
/openspace-evolution

# 指定演化模式
/openspace-evolution --mode fix --target "skill-name"
/openspace-evolution --mode derived --pattern "task-pattern"
/openspace-evolution --mode captured --workflow "workflow-name"

# 查看演化状态
/openspace-evolution status
/openspace-evolution history
```

## 核心命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `/openspace-evolution` | 启动演化编排器 | `/openspace-evolution --mode fix --target api-design` |
| `/openspace-evolution status` | 查看当前状态 | 显示演化队列、进行中任务 |
| `/openspace-evolution confirm` | 确认演化开始 | `/openspace-evolution confirm --goal "优化API设计"` |
| `/openspace-evolution abort` | 终止演化 | `/openspace-evolution abort --reason "超出范围"` |
| `/openspace-evolution history` | 查看演化历史 | 追踪所有演化记录 |

## 与天龙引擎协同点

| 天龙组件 | 协同方式 | 效果 |
|---------|---------|------|
| **09-02 编排协调师** | Level 7+ 自演化编排 | 超出预设编排的自我进化能力 |
| **10-02 AI研究员** | MIPROv2 优化器协同 | 提示词自动优化 |
| **autoresearch-loop** | 研究循环协同 | 实验假设自动验证 |
| **eval-harness** | 评估框架协同 | pass@k 量化指标验证 |
| **claude-mem** | 记忆层协同 | 演化经验持久化 |

## 演化信号检测规则

```yaml
FIX_trigger:
  condition: "连续失败 ≥ 3次"
  action: "自动触发 FIX 模式"
  confirmation_required: true

DERIVED_trigger:
  condition: "检测到重复任务模式"
  threshold: "5次相似任务"
  action: "建议 DERIVED 模式"
  confirmation_required: true

CAPTURED_trigger:
  condition: "发现有效工作流"
  validation: "至少3次成功执行"
  action: "自动捕获为 Skill"
  confirmation_required: false
```

## Anti-loop Guard 规则

```yaml
loop_detection:
  max_attempts: 5
  similarity_threshold: 0.85
  cooldown_period: "24h"

termination_conditions:
  - "相同问题超过5次尝试"
  - "演化收益 < 10%"
  - "循环依赖链超过3层"
```

## 技能文件

- [SKILL.md](SKILL.md) - 本文件
- [scripts/evolution_orchestrator.py](scripts/evolution_orchestrator.py) - 核心编排脚本
- [scripts/confirmation_gate.py](scripts/confirmation_gate.py) - 确认门控
- [scripts/anti_loop_guard.py](scripts/anti_loop_guard.py) - 防循环守卫
