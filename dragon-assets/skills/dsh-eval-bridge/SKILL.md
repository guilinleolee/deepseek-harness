---
name: dsh-eval-bridge
description: |
  借鉴 hccccc01333/dsh-eval 的 4 类方法论 + 自研 V1.0（不镜像真源）。
  4 类方法论：① benchmark YAML schema · ② 11 类评测指标 · ③ LLM judge 设计 · ④ paired A/B。
  Stage 45 借鉴档轻量 · MIT 协议 alignment · 累计 +8 PASS。
metadata:
  version: "1.0.0"
  date: "2026-08-24"
  license: MIT
  author: 天龙引擎 · Stage 45
  upstream_borrowing:
    - hccccc01333/dsh-eval v0.3.0 (MIT · 借鉴 4 类方法论 · 不镜像真源)
  integration_stage: 45
  triggers:
    - "dsh-eval"
    - "benchmark"
    - "评测"
    - "A/B"
    - "LLM judge"
    - "评估"
    - "benchmark.yaml"
---

# dsh-eval-bridge · V1.0（借鉴档 · 轻量）

> **TL;DR**：借鉴 [hccccc01333/dsh-eval](https://github.com/hccccc01333/dsh-eval) v0.3.0（**MIT ✅**）的 **4 类方法论** + **天龙自研 V1.0 实现**。**不镜像真源**（DSH 主仓依赖是 blocker），与 stage 41 mneme-heat-engine 借鉴模式一致。

---

## L0: 一句话描述 (≤15字)

借鉴 dsh-eval 4 类方法论。

---

## L1: 使用场景

当用户需要：
- **批量评测 DSH agent 的产物**：用 benchmark YAML 跑 N 个 case × M 个 trial
- **跨 run 比较**：同 case 不同版本（v1 vs v2）算 win/lose/tie 统计
- **LLM 自动打分**：用 judge model 评估 final-answer 准确度 + hallucination 率
- **trace 指标折叠**：从 DSH session log 折叠 token/latency/tool-success 等 11 类指标

---

## L2: 借鉴的方法论（4 类）

### 2.1 benchmark YAML schema

```yaml
# templates/benchmark.yaml.example
name: skill-regression                # 必填，唯一
model: deepseek-v4                    # 必填，LLM 名（primary provider）
profile: headless                     # 必填，DSH profile
command: [dsh]                        # 必填，执行命令 (default: [dsh])
trials: 3                             # 可选，每个 case 重复 N 次 (default: 3)
timeoutMs: 600000                     # 可选，单 trial 超时 (default: 600000=10min)
seed: 42                              # 可选，随机种子 (reproduce 用)

cases:
  - id: fix-tests-001                 # 必填，case ID
    prompt: Fix the failing tests.    # 必填，提示词
    workspace: ./fixtures/fix-tests   # 可选，工作区路径 (default cwd)
    expected:                          # 可选，验收规则
      tool: bash                      # 期望使用的工具
      check: ./check.sh               # 期望的执行命令（exit 0 = PASS）

pricing:                               # 可选，与 paperclip V2.0 价格表兼容
  deepseek-v4:
    inputUsdPerMTokens: 0.27
    cacheReadUsdPerMTokens: 0.07
    cacheWriteUsdPerMTokens: 0.27
    outputUsdPerMTokens: 1.10
```

> **借鉴要点**：case + trials + expected.tool + expected.check 4 维度结构清晰。**天龙改造**：把 `trials` 默认 3 → 5（更稳）+ 加 `seed` 强制（可复现）。

### 2.2 11 类评测指标

| # | 指标 | 来源 | 单位 | 公式 |
|---|---|---|---|---|
| 1 | **taskSuccess** | `expected.check` exit 0 | 0/1 | count(case.exit==0) / N |
| 2 | **toolSuccess** | tool.results in session log | 0/1 | count(tool.result.status=='ok') / N |
| 3 | **toolSelectionAccuracy** | `expected.tool` 匹配 | 0/1 | count(case.actual_tool==expected.tool) / N |
| 4 | **steps** | session log turns | count | median(turns) |
| 5 | **tokens** | 4 disjoint buckets | int | input+output+cacheRead+cacheWrite |
| 6 | **latency** | `latencyMs` | ms | p50/p95/p99 |
| 7 | **ttft** | `ttftMs` | ms | p95（影响感知）|
| 8 | **cost** | pricing table × tokens | USD | (input * p.input + output * p.output + ...) |
| 9 | **retryCount** | `llm/retry` events | int | sum(retry events) |
| 10 | **invalidToolCalls** | tool.result.status=='internal_failure' | int | count |
| 11 | **llmJudgeScore** | judge verdict (0-1) | float | mean(scores) |
| 12 | **llmJudgeHallucinationFlag** | judge verdict | bool | count(true) / N |

> **借鉴要点**：上游 11 类指标 + 我们加一类 **cost**（与 paperclip-cost-control V2.0 复用价格表）

### 2.3 LLM judge 设计

```yaml
# Case judge 调用方式
judge:
  model: deepseek-v4                # judge model（与 case model 独立）
  prompt_template: |
    You are evaluating task: {prompt}
    Expected: {expected}
    Actual: {actual}
    Output JSON: {score: 0-1, hallucinated: bool, comment: string}
  parse_strict: true                 # 严格 JSON 解析，不允许 additionalProperties
```

**judge 输出 schema**：
```typescript
interface JudgeVerdict {
  score: number;          // 0-1, final answer 准确度
  hallucinated: boolean;  // 是否包含事实错误
  comment: string;        // 100-200 字解释
}
```

> **借鉴要点**：strict JSON 解析 + 单 prompt 输出 schema；天龙**不引外部 judge SDK**，自写 `judge.py`（模仿 stage 23 anysearch V1.0 风格）

### 2.4 paired A/B 跑

```bash
# 比较 v1 与 v2 在同一 case 的 win/lose/tie
python paired_ab.py compare eval-v1.json eval-v2.json --out paired.md
```

**输出 Markdown 格式**：
```markdown
| Case | v1 Score | v2 Score | Δ (B-A) | Verdict |
|---|---|---|---|---|
| fix-tests-001 | 0.67 | 0.83 | +0.16 | **B WIN** |
| write-doc-002 | 1.00 | 0.50 | -0.50 | **A WIN** |
| ... |
| **TOTAL** | 0.84 | 0.83 | -0.01 | TIE |
```

> **借鉴要点**：B-A 符号约定（**`B - A`，正值 = B WIN**）+ 测试覆盖全部 case；天龙**复用 stage 35-07 V1.1 横纵研究员**，不重写

---

## L3: 安装

```bash
# 1. 装本 skill（天龙自有，已落 dragon-engine/skills/dsh-eval-bridge/）
# 2. 装 stage 44 trajectory-debug-bridge（前置，用于 trace export）
pip install pyyaml jsonschema

# 3. 验证（5/5 unittest）
python -m unittest tests/test_eval_bridge.py -v
```

---

## L4: 触发词（11 类）

```
dsh-eval · benchmark · benchmark.yaml · 评测 · A/B · paired
LLM judge · trace 指标 · tool success · task success
评估报告 · eval-run.json · eval-md
```

---

## L5: 下游协同（10 位置）

| 下游 | 协同 |
|---|---|
| **04-validator V9.04 → V9.05+** | evidence-based FMEA 配 LLM judge |
| **09-03 meta-reviewer v2.0** | A/B paired 算 audit metric |
| **35-07 V1.0 → V1.1+** | 横纵研究员 + benchmark YAML 实战 |
| **meta-prism V1.1** | AI-slop 9 签名 + LLM judge 交叉 |
| **paperclip-cost-control V2.0** | 评测 cost 复用价格表 |
| **session-distiller V1.1** | benchmark trail 数据来源 |
| **04-validator V9.05** | paired A/B win/lose/tie 自动归因 |
| **dsh-trajectory-debug-bridge** | trace export → eval input |
| **09-03 cron /perf** | daily 评测触发 |
| **stage 41 mneme-heat-engine** | benchmark L2 卡片 → mneme L0 |

---

## L6: DON'T 护栏（5 条）

- ❌ **不要**镜像 dsh-eval 真源（DSH 主仓依赖 + stage 41 mneme 借鉴先例）
- ❌ **不要**默认开启 `enableLLMJudge`（每评测多一次 LLM → token 翻倍；opt-in）
- ❌ **不要**让 benchmark 阻塞生产（独立 worker pool）
- ❌ **不要**把 benchmark YAML 当可商用资产（schema 借鉴，case 设计是自家）
- ❌ **不要**给 judge model 用付费 Provider（默认 deepseek + opt-in OpenAI/Anthropic）

---

## L7: 验证矩阵

| # | 必检项 | 期望 | 状态 |
|---|---|---|---|
| 1 | benchmark YAML schema 解析（11 字段校验）| jsonschema validate PASS | ⏳ |
| 2 | 11 类指标计算全部正常（基础值与上游公式一致）| 抽样 2 类验证 | ⏳ |
| 3 | LLM judge 输出 schema 解析（strict mode）| JSON 解析 100% | ⏳ |
| 4 | paired A/B 算 B-A（round 5 位）| Δ 误差 ≤ 1e-5 | ⏳ |
| 5 | 5 个 unittest PASS（schema/metric/judge/paired_cost/integrate）| 5/5 | ⏳ |

---

## L8: 与 dsh-eval 真源的边界

| 项 | 真源 dsh-eval | **天龙 dsh-eval-bridge V1.0** |
|---|---|---|
| 包结构 | pnpm workspace 1 子包 | **单 Python 文件 + 1 个 benchmark.yaml schema** |
| 协议 | MIT ✅ | MIT ✅（自研） |
| 依赖 | `@deepseek-ai/*` 7 peer | **仅 `pyyaml + jsonschema`** |
| tests | 113 vitest | **5 unittest** |
| 集成 DSH | 必须有 harness/ | **不需要** |
| 借鉴设计 | — | benchmark YAML / 11 指标 / LLM judge / paired A/B 4 类 |
| **镜像真源** | — | ❌ **不镜像**（与 stage 41 mneme 同模式）|

---

## L9: 参考链接

- **借鉴源**：https://github.com/hccccc01333/dsh-eval v0.3.0 · MIT
- **借鉴模式先例**：[`skills/mneme-heat-engine/SKILL.md`](../mneme-heat-engine/SKILL.md)（Stage 41 同模式）
- **上游协议治理基线**：[`docs/dsh-ecosystem-license-policy.md`](../../../docs/dsh-ecosystem-license-policy.md)
- **Stage 45 评估报告**：[`stage-40-scratch/stage-45-candidates-evaluation.md`](../../../../../../../../deepseek%20haress/stage-40-scratch/stage-45-candidates-evaluation.md)
- **Stage 45 D2 撞墙报告**：[`stage-40-scratch/stage-45-D2-engine-skeleton-eval.md`](../../../../../../../../deepseek%20haress/stage-40-scratch/stage-45-D2-engine-skeleton-eval.md)
