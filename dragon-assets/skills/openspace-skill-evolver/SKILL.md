---
license: UNKNOWN
triggers: ["openspace skill evolver", "OpenSpace Skill Evolver"]
---
# OpenSpace Skill Evolver

## 功能描述

OpenSpace Skill Evolver 是天龙引擎的技能自演化引擎，负责执行 FIX/DERIVED/CAPTURED 三种技能演化操作。

### 三种演化模式

| 模式 | 触发条件 | 操作 | 输出 |
|------|---------|------|------|
| **FIX** | 连续失败 ≥3次 | 修复技能缺陷 | 修复后的 Skill |
| **DERIVED** | 重复任务模式 ≥5次 | 派生新技能 | 新 Skill |
| **CAPTURED** | 有效工作流 ≥3次成功 | 捕获为 Skill | CAPTURED Skill |

### 演化流程

```
┌─────────────────────────────────────────────────────────────┐
│                    Skill Evolver                              │
├─────────────────────────────────────────────────────────────┤
│  FIX 模式:                                                  │
│  1. 分析失败原因 → 定位问题 → 修复代码 → 验证修复           │
│                                                             │
│  DERIVED 模式:                                              │
│  1. 检测重复模式 → 抽象通用逻辑 → 设计新 Skill → 测试验证   │
│                                                             │
│  CAPTURED 模式:                                             │
│  1. 识别工作流 → 规范化流程 → 生成 Skill 模板 → 归档发布   │
└─────────────────────────────────────────────────────────────┘
```

## 使用方式

```bash
# FIX 模式 - 修复技能缺陷
/openspace-skill-fix --target "skill-name" --analysis "失败分析"
/openspace-skill-fix --target "api-design" --issue "超时问题"

# DERIVED 模式 - 派生新技能
/openspace-skill-derive --from "existing-skill" --pattern "new-pattern"
/openspace-skill-derive --from "claude-api" --pattern "batch-processing"

# CAPTURED 模式 - 捕获工作流
/openspace-skill-capture --workflow "workflow-name" --examples 5
/openspace-skill-capture --workflow "code-review" --examples 10

# 查看演化状态
/openspace-skill status
```

## 核心命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `/openspace-skill-fix` | FIX 模式 | `/openspace-skill-fix --target api-design --issue timeout` |
| `/openspace-skill-derive` | DERIVED 模式 | `/openspace-skill-derive --from claude-api --pattern batch` |
| `/openspace-skill-capture` | CAPTURED 模式 | `/openspace-skill-capture --workflow review --examples 5` |
| `/openspace-skill status` | 查看状态 | 显示演化队列、进行中任务 |

## 与天龙引擎协同点

| 天龙组件 | 协同方式 | 效果 |
|---------|---------|------|
| **03构建师** | 代码修复模式协同 | 自动修复问题 |
| **09-02编排协调师** | 工作流捕获协同 | 自动捕获有效工作流 |
| **10-02 AI研究员** | 技能派生协同 | 提示词模式派生 |
| **claude-mem** | 演化经验存储 | 技能知识持久化 |

## 演化质量标准

```yaml
FIX_quality:
  must_pass: "原有失败的测试"
  should_pass: "回归测试"
  verification: "实际场景验证"

DERIVED_quality:
  must_pass: "基础功能测试"
  should_pass: "边界情况测试"
  verification: "对比原技能和新技能"

CAPTURED_quality:
  must_pass: "工作流重现测试"
  should_pass: "参数化测试"
  verification: "3次以上成功执行"
```

## 技能文件

- [SKILL.md](SKILL.md) - 本文件
- [scripts/skill_fix.py](scripts/skill_fix.py) - FIX 模式脚本
- [scripts/skill_derive.py](scripts/skill_derive.py) - DERIVED 模式脚本
- [scripts/skill_capture.py](scripts/skill_capture.py) - CAPTURED 模式脚本
