---
license: UNKNOWN
name: ai-first-engineering
description: Engineering operating model for teams where AI agents generate a large share of implementation output.
github_repo: affaan-m/everything-claude-code
github_hash: 4e66b2882da9afb9747468b08a253ca2f09c85f3
last_updated: 2026-04-25
source_type: derived
origin: ECC (everything-claude-code)
triggers: ["ai first engineering", "AI-First Engineering"]
---

# AI-First Engineering

> 来源: [affaan-m/everything-claude-code/skills/ai-first-engineering](https://github.com/affaan-m/everything-claude-code)

## 功能概述

AI优先工程操作系统模型，为AI代理生成大部分实现代码的团队提供流程、审查和架构规范。

## 核心转变

| 传统开发 | AI优先开发 |
|---------|-----------|
| 打字速度重要 | **规划质量更重要** |
| 覆盖率主观自信 | **评估覆盖率更重要** |
| 语法审查 | **系统行为审查** |

## 架构要求

**优先选择AI友好的架构:**

- 明确的边界 (explicit boundaries)
- 稳定的契约 (stable contracts)
- 类型化接口 (typed interfaces)
- 确定性测试 (deterministic tests)

**避免:** 分散在隐藏约定中的隐式行为。

## AI优先代码审查

### 审查重点

- 行为回归 (behavior regressions)
- 安全假设 (security assumptions)
- 数据完整性 (data integrity)
- 失败处理 (failure handling)
- 发布安全 (rollout safety)

### 最小化审查项

- 已由自动化覆盖的风格问题
- 格式化问题（已有工具处理）
- 明显不相关的建议

## AI优先团队招聘信号

**强大的AI优先工程师:**

- 清晰分解模糊工作
- 定义可衡量的验收标准
- 生成高信号提示词和评估
- 在交付压力下执行风险控制

## 测试标准

**为AI生成代码提高测试标准:**

- 必须对触及领域的回归覆盖
- 显式的边缘情况断言
- 接口边界集成检查

## 天龙引擎集成

### 适用岗位

| 岗位 | 集成方式 | 增强能力 |
|------|---------|---------|
| **02架构师** | AI友好架构设计 | 明确边界 + 类型化接口 |
| **06审查师** | AI优先代码审查 | 行为回归 + 安全假设 |
| **04验证师** | AI生成代码测试 | 提高测试标准 + 边缘断言 |

### 天龙引擎增强

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎 AI-First 工程体系                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   传统开发流程:                                             │
│   规划 → 编码 → 语法审查 → 测试 → 发布                       │
│                                                             │
│   AI-First开发流程:                                         │
│   规划质量优先 → 评估覆盖率优先 → 系统行为审查                │
│                                                             │
│   天龙引擎协同:                                              │
│   ├── 02架构师  → AI友好架构设计                            │
│   ├── 03构建师  → 明确契约 + 类型化接口                      │
│   ├── 04验证师  → 评估驱动测试 + 边缘断言                    │
│   ├── 05安全师  → 安全假设审查                              │
│   └── 06审查师  → 行为回归审查                              │
│                                                             │
│   核心原则:                                                 │
│   ├── 规划质量 > 打字速度                                    │
│   ├── 评估覆盖率 > 主观自信                                 │
│   └── 行为审查 > 语法审查                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 架构检查清单

```markdown
## AI友好架构检查

- [ ] 明确的模块边界
- [ ] 稳定的API契约
- [ ] 类型化接口（TypeScript/Python类型）
- [ ] 确定性测试（无flaky tests）
- [ ] 显式错误处理
- [ ] 最小化隐式依赖
- [ ] 可测试的函数设计
```

### 审查触发条件

```markdown
## AI优先代码审查触发

**必须审查:**
- API路由修改
- 数据模型变更
- 认证/授权逻辑
- 支付/财务逻辑
- 外部依赖变更

**可选审查:**
- 样式/格式化变更
- 注释/文档更新
- 小型bug修复（有测试覆盖）
```

## 与其他技能协同

| 技能 | 协同方式 |
|------|---------|
| **eval-harness** | pass@k量化评估 |
| **ai-regression-testing** | AI盲点回归检测 |
| **benchmark** | 性能基准回归检测 |

## 最佳实践

1. **规划质量优先**: AI代理规划阶段是质量的关键
2. **评估覆盖率**: 用量化指标代替主观信心
3. **行为审查**: 从语法转向系统行为
4. **风险控制**: 在交付压力下保持安全边界

## 参考资料

- [Everything Claude Code](https://github.com/affaan-m/everything-claude-code)
- [ECC ai-first-engineering](https://github.com/affaan-m/everything-claude-code/tree/main/skills/ai-first-engineering)

---

**版本**: V1.0 | **兼容性**: 天龙引擎 V8.67+ | **来源**: ECC
