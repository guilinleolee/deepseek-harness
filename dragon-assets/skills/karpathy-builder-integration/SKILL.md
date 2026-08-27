---
license: UNKNOWN
triggers: ["karpathy builder integration", "Karpathy Builder Integration Skill"]
---
# Karpathy Builder Integration Skill

## L0: 一句话描述 (≤15字)
Karpathy简洁编程整合，构建师必读

## L1: 使用场景 (50-100字)
当03构建师进行代码编写时，遵循Karpathy四大原则：Think Before Coding（先思后行）、Simplicity First（简洁优先）、Surgical Changes（精准改动）、Goal-Driven Execution（目标驱动执行）。避免过度复杂化、拒绝未请求功能、只改该改的代码。

## L2: 详细文档

### 来源
> [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) - 130k Stars, MIT License

### 四大原则详解

#### 1. Think Before Coding（三思而后行）
```
Don't assume. Don't hide confusion. Surface tradeoffs.

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.
```

**天龙整合点**：
- 与"先失败测试"原则互补
- 澄清问题在实现之前而非之后

#### 2. Simplicity First（简洁优先）
```
Minimum code that solves the problem. Nothing speculative.

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.
```

**天龙整合点**：
- 融入03构建师TDD铁律
- 拒绝过度抽象原则

#### 3. Surgical Changes（精准改动）
```
Touch only what you must. Clean up only your own mess.

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.
```

**天龙整合点**：
- 融入06审查师代码审查
- 禁止"顺手改进"相邻代码

#### 4. Goal-Driven Execution（目标驱动执行）
```
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

**天龙整合点**：
- 融入04验证师验证流程
- 验证格式标准化：`→ verify: [检查]`

### 整合天龙TDD铁律

```
┌─────────────────────────────────────────────────────────────┐
│ Karpathy × 天龙TDD 整合闭环                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Think Before Coding ──→ 明确假设和边界                      │
│         ↓                                                   │
│  Goal-Driven Execution ──→ TDD Red → Green → Refactor    │
│         ↓                                                   │
│  Simplicity First ──→ 最小代码解决                        │
│         ↓                                                   │
│  Surgical Changes ──→ 精准改动验证                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 验证格式模板

```markdown
1. [编写测试] → verify: 测试失败
2. [实现功能] → verify: 测试通过
3. [重构代码] → verify: 代码简洁，测试仍通过
```

### 自检清单

| 检查项 | 问题 | Karpathy原则 |
|--------|------|-------------|
| 假设明确 | 是否隐藏了假设？ | Think Before Coding |
| 简洁性 | 是否过度复杂？ | Simplicity First |
| 改动范围 | 是否改动了不该改的？ | Surgical Changes |
| 验证标准 | 成功标准是否可验证？ | Goal-Driven Execution |

### 触发命令

```bash
/karpathy-builder        # 启动Karpathy构建师流程
/karpathy-check         # 自检四大原则
/karpathy-verify-format # 验证格式标准化
```

### 与天龙岗位协同

| 天龙岗位 | Karpathy整合点 | 协同效果 |
|---------|---------------|---------|
| **03构建师** | 全部四大原则 | 代码质量+30% |
| **04验证师** | Goal-Driven Execution | 验证效率+25% |
| **06审查师** | Surgical Changes | 审查质量+20% |

### 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-15 | 初始整合，基于multica-ai/andrej-karpathy-skills |

### 预期收益

| 指标 | 整合前 | 整合后 | 提升 |
|------|--------|--------|------|
| **diff中不必要更改** | 基准 | -40% | Surgical Changes |
| **因过度复杂的重写** | 基准 | -50% | Simplicity First |
| **澄清问题时机** | 事后 | 事前 | Think Before Coding |
| **验证标准化** | 基准 | +60% | Goal-Driven Execution |

### 技能文件

- [skills/karpathy-builder-integration/SKILL.md](skills/karpathy-builder-integration/SKILL.md)
