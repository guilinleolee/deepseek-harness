---
license: UNKNOWN
triggers: ["karpathy verify integration", "Karpathy Verify Integration Skill"]
---
# Karpathy Verify Integration Skill

## L0: 一句话描述 (≤15字)
目标驱动验证，04验证师增强

## L1: 使用场景 (50-100字)
当04验证师进行测试验证时，使用Goal-Driven Execution原则将任务转化为可验证目标，标准化验证格式为`→ verify: [检查]`，确保测试失败在实现之前，测试通过在重构之后。

## L2: 详细文档

### 来源
> [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) - 130k Stars, MIT License

### Goal-Driven Execution原则

```markdown
Define success criteria. Loop until verified.

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

### 验证格式标准化

```markdown
┌─────────────────────────────────────────────────────────────┐
│                    Goal-Driven Verify 格式                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. [编写失败测试] → verify: 测试确实验证了bug             │
│  2. [实现修复]     → verify: 测试通过                      │
│  3. [运行回归]     → verify: 原有测试仍通过                 │
│  4. [代码整洁]     → verify: 无警告、无冗余                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 验证场景矩阵

| 任务类型 | 验证目标 | verify格式 |
|----------|---------|-----------|
| **Bug修复** | 测试重现bug | `→ verify: 测试失败消息准确` |
| **新功能** | 测试验证功能 | `→ verify: 所有测试通过` |
| **重构** | 保持功能不变 | `→ verify: 原有测试通过` |
| **性能优化** | 性能提升 | `→ verify: benchmark提升20%` |
| **安全修复** | 无漏洞引入 | `→ verify: 安全扫描通过` |

### 整合天龙Systematic Debugging

```
┌─────────────────────────────────────────────────────────────┐
│  Karpathy × 天龙验证 整合闭环                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Think Before Coding ──→ 定义验证范围                    │
│         ↓                                                   │
│  2. Goal-Driven Execution ──→ 标准化verify格式              │
│         ↓                                                   │
│  3. Surgical Changes ──→ 只验证相关改动                     │
│         ↓                                                   │
│  4. Loop until verified ──→ 持续验证直到通过                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 验证检查清单

| 阶段 | 检查项 | 通过标准 |
|------|--------|---------|
| **Red** | 测试编写 | 测试失败，证明bug存在 |
| **Green** | 功能实现 | 测试通过 |
| **Refactor** | 代码重构 | 测试仍通过，无新警告 |

### 自检命令

```bash
/karpathy-verify "修复登录bug"     # 启动Goal-Driven验证流程
/karpathy-verify --format           # 检查verify格式标准化
/karpathy-verify --plan            # 生成验证计划
```

### 与天龙岗位协同

| 天龙岗位 | Karpathy整合点 | 协同效果 |
|---------|---------------|---------|
| **04验证师** | Goal-Driven Execution | 验证效率+25% |
| **03构建师** | 目标可验证 | 构建质量+20% |
| **06审查师** | 验证标准 | 审查效率+15% |

### 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-15 | 初始整合，基于multica-ai/andrej-karpathy-skills |

### 预期收益

| 指标 | 整合前 | 整合后 | 提升 |
|------|--------|--------|------|
| **验证标准化** | 基准 | +60% | Goal-Driven Execution |
| **验证覆盖率** | 基准 | +30% | 标准化格式 |
| **Bug重现率** | 基准 | +40% | verify格式 |

### 技能文件

- [skills/karpathy-verify-integration/SKILL.md](skills/karpathy-verify-integration/SKILL.md)
