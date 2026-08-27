---
license: UNKNOWN
name: eval-harness
version: 2.0.0
description: |
  评估驱动开发 (EDD) 框架 V2.0，集成 VADPs2.0 六步工作流
  (背景→角色→目标→约束→输出→验证) 和六维25点评分体系，
  超越传统 PASS/FAIL 评估，实现量化质量门控。
author: 天龙引擎团队
created: 2026-02-26
updated: 2026-05-08
category: development
triggers:
  - "用户提到「eval-harness 评估框架」时"
  - "用户需要 VADPs2.0 量化评分时"
  - "用户提到「EDD 评估驱动开发」或「pass@k 指标」时"
---

# Eval Harness 评估驱动开发框架 V2.0

## L0: 一句话
EDD 评估驱动开发框架，集成 VADPs2.0 六步工作流和六维25点评分体系。

## L1: 使用场景
Eval Harness 是评估驱动开发 (Eval-Driven Development) 框架，将评估作为"AI 开发的单元测试"。V2.0 在传统 PASS/FAIL 基础上，扩展 VADPs2.0 六步工作流（背景→角色→目标→约束→输出→验证）和六维25点评分体系（结果契合度25%/上下文保真度15%/可执行性20%/约束与停止规则15%/输出可控性15%/验证与迭代性10%）。适用 DSPy Signature 评估、Agent 性能基准、MIPROv2 优化验证等场景。V2.0 通过量化评分体系确保评估质量可追踪、可迭代。

## L2: 详细文档

### VADPs2.0 六步 × EDD 评估映射

```
┌─────────────────────────────────────────────────────────────┐
│ Stage 1: 背景分析 (Context)                              │
│   → 分析评估目标、数据集规模、metric 定义                  │
│   ≡ EDD: 评估类型定义 (Capability / Regression)          │
├─────────────────────────────────────────────────────────────┤
│ Stage 2: 角色定义 (Role)                                 │
│   → 定义评估角色：Grader/裁判/评审员                      │
│   ≡ EDD: Grader 类型选择 (Code/Model/Human)             │
├─────────────────────────────────────────────────────────────┤
│ Stage 3: 目标设定 (Goal + Success Criteria)             │
│   → 设定 Goal 字段 + Success Criteria 量化标准             │
│   ≡ EDD: pass@k 目标阈值设定 (pass@3 > 90%)            │
├─────────────────────────────────────────────────────────────┤
│ Stage 4: 约束制定 (Constraints + Stop Rules)             │
│   → 制定 Constraints 禁止项 + Stop Rules 截断条件          │
│   ≡ EDD: 超时限制、预算上限、失败截断                     │
├─────────────────────────────────────────────────────────────┤
│ Stage 5: 输出规范 (Output)                               │
│   → 定义 OutputField 格式 + 报告模板                     │
│   ≡ EDD: EVAL REPORT 格式 (PASS/FAIL + pass@k 分数)    │
├─────────────────────────────────────────────────────────────┤
│ Stage 6: 执行验证 (Eval-Harness)                       │
│   → 执行评估 + 六维评分 + 迭代优化                       │
│   ≡ EDD: 运行评估 + 生成报告 + 追踪回归                  │
└─────────────────────────────────────────────────────────────┘
```

### 六维25点评分体系

| 维度 | 权重 | 检查项 |
|------|------|--------|
| 结果契合度 | 25% | metric 分数达标率、pass@k 达成率 |
| 上下文保真度 | 15% | 测试数据与真实分布的一致性、demos 质量 |
| 可执行性 | 20% | 评估脚本可运行、环境依赖满足 |
| 约束与停止规则 | 15% | Stop Rules 截断率、超时率 |
| 输出可控性 | 15% | 评估报告格式一致性、输出稳定性 |
| 验证与迭代性 | 10% | pass@k 评估通过率、历史基线对比 |

### VADPs2.0 评估示例

```python
# 1. 背景分析 → 定义评估任务
# [Stage 1] 评估目标：RAG 系统回答质量
# [Stage 2] 评估角色：Code Grader (精确匹配)
# [Stage 3] 目标设定：pass@3 > 90%
# [Stage 4] 约束制定：超时 30s、API 费用 < $1
# [Stage 5] 输出规范：JSON 报告 {pass@k, latency, cost}

from eval_harness import Evaluator, CodeGrader

evaluator = Evaluator(
    task="RAG Quality Assessment",
    metric=lambda x, y: x.answer == y.answer,  # 精确匹配
    grader_type="code",                           # Code Grader
    success_criteria={"pass@3": 0.90},          # Goal: pass@3 > 90%
    stop_rules={"timeout": 30, "max_cost": 1.0}, # 约束
)

# 2-5. VADPs2.0 配置 → 六步配置
config = {
    "context": {"dataset": "hotpotqa", "size": 1000},
    "role": {"grader": "CodeGrader", "mode": "strict"},
    "goal": {"target": 0.90, "metric": "pass@3"},
    "constraints": {"timeout": 30, "budget": 1.0},
    "output": {"format": "json", "template": "eval_report"},
}

# 6. 执行验证 → 六维评分
report = evaluator.run(dataset=val_examples)
scores = evaluator.score_six_dimensions(report)

# 六维评分
scores = {
    "结果契合度": 0.92,      # pass@3 = 0.92
    "上下文保真度": 0.88,    # 数据集分布一致
    "可执行性": 1.0,         # 脚本可运行
    "约束与停止规则": 0.95,  # 超时率 < 5%
    "输出可控性": 0.90,      # 报告格式一致
    "验证与迭代性": 0.88,    # pass@3 达成
}
total = sum(v * w for v, w in zip(scores.values(), [0.25, 0.15, 0.20, 0.15, 0.15, 0.10]))
# total = 0.91
```

## 评估类型

### Capability Eval (能力评估)

测试 AI 是否能做到之前做不到的事：

```markdown
[CAPABILITY EVAL: signature-qa]
Task: DSPy Signature 能否正确回答基于 context 的问题
Success Criteria:
  - [ ] 答案精确匹配 context 中的事实
  - [ ] 推理过程有步骤说明
  - [ ] 置信度评分合理
Expected Output: 答案 + 推理链 + 置信度
```

### Regression Eval (回归评估)

确保变更不会破坏已有功能：

```markdown
[REGRESSION EVAL: rag-pipeline]
Baseline: v2.1.0 (sha: abc123)
Tests:
  - existing-login: PASS
  - existing-retrieve: PASS
  - existing-generate: FAIL ← 回归!
Result: 2/3 passed (previously 3/3)
```

## Grader 类型

### 1. Code Grader (代码判决)

确定性检查：

```bash
# 检查文件是否包含预期模式
grep -q "export function handleAuth" src/auth.ts && echo "PASS" || echo "FAIL"

# 检查测试是否通过
npm test -- --testPathPattern="auth" && echo "PASS" || echo "FAIL"

# 检查构建是否成功
npm run build && echo "PASS" || echo "FAIL"
```

### 2. Model Grader (模型判决)

用于开放式输出评估：

```markdown
[MODEL GRADER PROMPT]
评估以下回答质量：
1. 答案是否直接相关 context？
2. 推理步骤是否严密？
3. 边缘情况是否处理？
4. 错误处理是否恰当？

评分: 1-5 (1=差, 5=优秀)
推理: [解释]
```

### 3. Human Grader (人工判决)

需要人工审核的场景：

```markdown
[HUMAN REVIEW REQUIRED]
变更: 修改了 RAG 检索逻辑
原因: 输出质量主观性较强
风险等级: MEDIUM
```

## 指标

### pass@k

"k 次尝试中至少一次成功"

| 指标 | 目标 | 适用场景 |
|------|------|---------|
| pass@1 | > 70% | 快速反馈、简单任务 |
| pass@3 | > 90% | 常规评估、可靠性测量 |
| pass@5 | > 95% | 高可靠性要求 |

### pass^k

"全部 k 次试验都成功" — 更严格的可靠性标准。

## 评估工作流

### 1. 定义 (编码前)

```markdown
## EVAL DEFINITION: signature-optimization

### Capability Evals
1. 可创建新的 DSPy Signature
2. 可编译优化 RAG 程序
3. 可生成六维评分报告

### Regression Evals
1. 现有 login 流程仍然正常
2. 会话管理未改变
3. logout 流程完整

### Success Metrics
- pass@3 > 90% for capability evals
- pass^3 = 100% for regression evals
```

### 2. 实现

编写代码以通过定义的评估。

### 3. 评估

```bash
# 运行 capability evals
[Run each capability eval, record PASS/FAIL]

# 运行 regression evals
npm test -- --testPathPattern="existing"

# 生成报告
```

### 4. 报告

```markdown
EVAL REPORT: signature-optimization
=====================================

Capability Evals:
  create-signature:  PASS (pass@2)
  compile-rag:       PASS (pass@1)
  six-dim-score:     PASS (pass@3)
  Overall:          3/3 passed

Regression Evals:
  login-flow:       PASS
  session-mgmt:     PASS
  logout-flow:      PASS
  Overall:          3/3 passed

Metrics:
  pass@1:  67% (2/3)
  pass@3:  100% (3/3)

六维评分:
  结果契合度:     0.92
  上下文保真度:  0.88
  可执行性:       1.00
  约束与停止规则: 0.95
  输出可控性:     0.90
  验证与迭代性:  0.88
  综合评分:       0.91

Status: READY FOR REVIEW
```

## 与天龙引擎协同

- 10-02 AI研究员: MIPRO 自动优化调研程序
- 10-01 提示词架构师: Signature VADPs2.0 评估
- 04 验证师: EDD 评估驱动开发集成
- dspy-teleprompter: MIPROv2 优化效果 pass@k 验证

## 最佳实践

1. **编码前定义评估** — 强制明确成功标准
2. **频繁运行评估** — 尽早捕获回归
3. **追踪 pass@k 趋势** — 监控可靠性变化
4. **优先代码判决** — 确定性 > 概率性
5. **安全评估人工审核** — 永远不完全自动化安全检查
6. **保持评估快速** — 慢评估没人跑
7. **评估与代码同版本** — 评估是一等公民

## 示例：添加认证功能

```markdown
## EVAL: add-authentication

### Phase 1: Define (10 min)
Capability Evals:
- [ ] 用户可使用邮箱/密码注册
- [ ] 用户可使用有效凭证登录
- [ ] 无效凭证被拒绝并返回正确错误
- [ ] 会话在页面刷新后保持
- [ ] Logout 清除会话

Regression Evals:
- [ ] 公开路由仍可访问
- [ ] API 响应格式未改变
- [ ] 数据库 schema 兼容

### Phase 2: Implement (varies)
[编写代码]

### Phase 3: Evaluate
Run: /eval check add-authentication

### Phase 4: Report
EVAL REPORT: add-authentication
==============================
Capability: 5/5 passed (pass@3: 100%)
Regression:  3/3 passed (pass^3: 100%)
六维评分: 0.93
Status: SHIP IT
```

### Evolution Pattern (维护)

当核心 skill 升级时，避免直接编辑 `SKILL.md` 以保留自定义改进：

1. 在 skill 根目录创建或更新 `evolution.json` 文件
2. 在其中存储修改建议、自定义规则或演化逻辑
3. 这样即使 base `SKILL.md` 在升级中被替换，自定义"演化"也会被保留
