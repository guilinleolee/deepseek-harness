---
license: UNKNOWN
name: caveman-eval-harness
description: |
github_repo: JuliusBrussee/caveman
github_hash: 84cc3c14fa1e10182adaced856e003406ccd250d
last_updated: 2026-04-25
source_type: derived
version: 1.0.0
触发词: caveman eval, 技能评估, 评估框架, 三臂测试。
来源: JuliusBrussee/caveman (13,252 ⭐), MIT License。
author: github/JuliusBrussee
adapted-by: Claude Code (天龙引擎 V8.90)
date: 2026-04-11
allowed-tools: 
triggers: ["caveman eval harness", "Caveman Eval Harness — 三臂评估框架"]
---

# Caveman Eval Harness — 三臂评估框架

## 描述

三臂评估框架，用于隔离caveman技能的真实贡献。比较 `__baseline__` vs `__terse__` vs `<skill>` 三种模式的输出质量和token消耗。

## 评估设计

### 三臂定义

```
┌─────────────────────────────────────────────────────────────┐
│                     三臂评估架构                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Arm 1: __baseline__                                      │
│   ├── 模型: 原始提示词，无caveman干预                       │
│   ├── 作用: 测量模型基准能力                               │
│   └── 预期: 正常详细输出 (~800-1200 tokens)               │
│                                                             │
│   Arm 2: __terse__                                        │
│   ├── 模型: caveman-terse:full 强制压缩                   │
│   ├── 作用: 测量压缩率贡献                                 │
│   └── 预期: ~294 tokens (节省 ~65%)                        │
│                                                             │
│   Arm 3: <skill>                                          │
│   ├── 模型: 具体caveman技能 (commit/review/terse)         │
│   ├── 作用: 测量技能贡献                                   │
│   └── 预期: 依技能而异                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 评估任务类型

| 任务类型 | 示例 Prompt | 评估指标 |
|---------|-----------|---------|
| **commit** | "用一句话总结这个变更" | 简洁性、准确性、why覆盖 |
| **review** | "审查这段代码" | Bug检出率、修复建议质量 |
| **terse** | "解释这个React重渲染问题" | 压缩率、技术准确性 |

### 评估指标

| 指标 | __baseline__ | __terse__ | <skill> | 计算方式 |
|------|-------------|-----------|---------|---------|
| **Token消耗** | T_baseline | T_terse | T_skill | 实际计数 |
| **Token节省** | 0% | (T_b-T_t)/T_b | (T_b-T_s)/T_b | 相对节省 |
| **质量评分** | Q_baseline | Q_terse | Q_skill | LLM或人工 |
| **质量保持率** | 100% | Q_terse/Q_b | Q_skill/Q_b | 相对质量 |
| **效率比** | Q_b/T_b | Q_t/T_t | Q_s/T_s | 质量/Token |

### 判定标准

```
推荐条件:
  1. Token节省 > 30%
  2. 质量保持率 > 85%
  3. 效率比 > 1.2

强烈推荐:
  Token节省 > 50%
  质量保持率 > 90%
  效率比 > 1.5
```

## 评估执行

### 评估命令

```bash
# 运行三臂评估
python3 ~/.claude/skills/caveman-eval-harness/scripts/run_eval.py \
  --task-type commit \
  --prompts ./eval_prompts/commit_test.jsonl

# 查看结果
python3 ~/.claude/skills/caveman-eval-harness/scripts/report.py \
  --eval-id eval-20260411

# 批量评估
python3 ~/.claude/skills/caveman-eval-harness/scripts/batch_eval.py \
  --tasks commit,review,terse \
  --iterations 5
```

### 评估报告格式

```markdown
# Caveman Eval Report: caveman-commit

## 测试概览
- 日期: 2026-04-11
- 任务类型: commit
- 迭代次数: 10

## 三臂结果

| 臂 | Token平均 | Token节省 | 质量平均 | 质量保持率 | 效率比 |
|----|----------|----------|----------|-----------|--------|
| __baseline__ | 847 | 0% | 4.2/5 | 100% | 0.005 |
| __terse__ | 294 | 65% | 4.0/5 | 95% | 0.014 |
| <commit> | 156 | 82% | 4.3/5 | 102% | 0.028 |

## 判定
✅ __terse__ 强烈推荐 (节省65%, 质量保持95%)
✅ <commit> 强烈推荐 (节省82%, 质量提升2%)

## 详细结果
[...详细数据表格...]
```

## 天龙引擎集成

### 岗位升级

| 岗位 | 集成方式 |
|------|---------|
| **04验证师** | 评估框架核心，测量caveman技能贡献 |
| **10-02 AI研究员** | MIPROv2优化评估，算法化自动优化 |

### 评估触发条件

| 触发条件 | 描述 |
|---------|------|
| 新技能安装 | 评估新caveman技能是否值得使用 |
| 技能更新 | 评估更新后的技能是否改进了性能 |
| 定期审计 | 每30天自动评估所有caveman技能 |
| 用户反馈 | 用户报告质量下降时触发评估 |

### 评估工具

```bash
# 评估caveman-commit
/eval-harness skill=caveman-commit task=commit

# 评估caveman-review
/eval-harness skill=caveman-review task=review

# 评估caveman-terse
/eval-harness skill=caveman-terse task=explanation
```

## 来源与许可

- 项目: [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)
- Stars: 13,252 | License: MIT
- 天龙引擎 V8.90 集成

## 参考资料

- [benchmarks/README.md](benchmarks/README.md) - 基准测试设计
- [evals/README.md](evals/README.md) - 评估协议
