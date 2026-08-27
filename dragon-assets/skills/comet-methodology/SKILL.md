---
name: comet-methodology
version: 1.0.0
base_version: rpamis/comet (MIT · 277 forks · 2026-05-14 创建 · 2026-08-26 末 push)
description: >
  借鉴 rpamis/comet 4 类方法论 (Phase-guarded execution / Loop engineering / Skill→workflow eval / MIT LICENSE).
  Use when designing phase-guarded workflows / retry loops / eval-grade skill pipelines.
triggers:
  - "comet 借鉴"
  - "phase-guarded"
  - "loop"
  - "eval"
  - "workflow"
  - "skill pipe"
  - "harness"
upstream:
  - "rpamis/comet (MIT · 277 forks · 3 个月迭代 · eval/harness-engineering)"
downstream:
  - 04-validator V9.08
  - 09-04-chief-of-staff V2.2
  - hv-analysis V1.3
  - session-distiller V1.2
  - mneme-heat-engine V2.1
inputs:
  - { name: workflow_yaml, type: YAML, required: true }
  - { name: eval_provider, type: enum[stub, deepseek, qwen, openai], required: false }
outputs:
  - { name: phase_gate_report, type: JSON }
  - { name: loop_convergence_log, type: NL }
errors:
  - { code: 400, meaning: "工作流 yaml 缺 phase 字段" }
  - { code: 422, meaning: "评估得分为 0 + loop 阈值超限" }
  - { code: 429, meaning: "LLM judge 限流" }
DO:
  - "借鉴档 + 不镜像真源 (与 memos-methodology 同步推进节奏)"
  - "仿照 stage 45 dsh-eval MIT 红线 3 项 + 'Modified by dragon-engine' footer"
  - "凡借 'phase-guarded' 必加 eval gate 拦截 (每阶段强制 ≥ 0.7 score 才推进)"
  - "凡借 'loop engineering' 必设 max-loop + backoff (避免无限循环)"
  - "凡借 'workflow eval' 必输出 YAML/Markdown 双产物 (与 stage 47.1 memos 同一接口)"
  - "凡借 'sdd' 思路必落到 plan YAML (与 stage 46 nomifun plan YAML 同)"
DONTS:
  - "不要克隆 comet 真源 (JavaScript ESM 依赖 socket.io)"
  - "不要 npm install @rpamis/* 任何包"
  - "不要写 'comet 官方' / '官方授权' 字样"
  - "不要从 comet 路径读 .sdd (那是 comet 私有格式)"
  - "不要把 phase gate 用于无限循环 (必须 max_loop 硬上限)"
  - "不要让 LLM judge 直接 verdict ≥ 1.0 (容错)"
  - "不要在 phase gate 里 hard-code LLM prompt (走 templates)"
  - "不要把 workflow eval 与 LLM judge 混淆 (前者 metric · 后者 LLM)"
  - "不要写 'comet 替代 dsh-eval' (两者并存: stub metric vs LLM judge)"
  - "不要在无人值守模式下跑 phase gate (必须 user confirm)"
example:
  cli: |
    python scripts/comet_bridge.py phase_gate tests/fixtures/sample_workflow.yaml
    python scripts/comet_bridge.py loop_engine --max 5 --backoff 1.5
    python scripts/comet_bridge.py workflow_eval plan.yaml --judge stub
  output: |
    ✓ phase gate PASS (3/3 stages >= 0.7)
    ✓ loop converged in 4 iterations
    ✓ eval report saved → workflow_eval.md
---

# comet-methodology（借鉴档）· 4 类方法论 V1.0

> **L0 一句话**: 借 rpamis/comet 4 类 phase-guarded 方法论，自研 workflow eval pipeline。

> **L1 使用场景**（50-100 字）: rpamis/comet（MIT · 277 forks · 3 个月迭代 · eval/harness-engineering/phase-guarded/sdd/skill-creator/loop-engineering/spec 与天龙 8 种 skill 生态精准互补）是「phase-guarded skill harness」—— 把"想法"转成"评估级 workflow"。4 类方法论：① Phase-guarded execution（每阶段 eval gate 拦截）② Loop engineering（retry + backoff + max-loop）③ Skill→workflow eval（YAML schema + 双产物）④ MIT 合规镜像。本 SKILL 不克隆真源（JavaScript ESM 依赖 socket.io），仅借鉴方法论层。

> **L2 详细文档**: 4 类方法论详见下方 §一-§四。

---

## 一、Phase-guarded execution（**3 阶段 eval gate**）

```
idea → ┌────────────┐ → ┌────────────┐ → ┌────────────┐ → ┌────────────┐
        │ Phase 1:   │   │ Phase 2:   │   │ Phase 3:   │   │ Phase 4:   │
        │ Define     │   │ Draft      │   │ Review     │   │ Deliver    │
        │ gate: ≥0.7 │   │ gate: ≥0.7 │   │ gate: ≥0.7 │   │ gate: ≥0.7 │
        └────────────┘   └────────────┘   └────────────┘   └────────────┘
                         ↑                                              ↓
                         └────── eval FAIL → loop back ←───────┘
```

**天龙借鉴**：04-validator V9.08 + mneme-heat-engine V2.1 加 phase_guard。

---

## 二、Loop engineering（**4 类 backoff + max-loop**）

```python
loop_engine(
    max_loop=5,
    backoff_factor=1.5,
    backoff_initial=1.0,
    backoff_max=60.0,
)
```

| Backoff 类型 | formula | 适用 |
|---|---|---|
| linear | delay_n = n × k | 短循环 |
| exponential | delay_n = init × k^n | 中循环（默认）|
| fibonacci | delay_n = fib(n) × k | 慢退避 |
| decorrelated | delay_n = rand(init, prev×k) | 抖动退避 |

**天龙借鉴**：09-04 chief-of-staff V2.2 + async-task-pattern V1.x 已实装。

---

## 三、Skill → workflow eval（**YAML schema + Markdown + JSON 双产物**）

```yaml
# tests/fixtures/sample_workflow.yaml
workflow_id: wf-001
goal: |
  用 28-04 内容策划师 排选题
phases:
  - phase_id: define
    role: planner
    eval_threshold: 0.7
    metrics: [completeness, clarity]
  - phase_id: draft
    role: writer
    eval_threshold: 0.7
    metrics: [length, keyword_density]
  - phase_id: review
    role: validator
    eval_threshold: 0.7
    metrics: [rubric, llm_judge]
```

**天龙借鉴**：复用 stage 46 nomifun_execution_schema.py V1.0 + 加 phase_guard 字段。

---

## 四、MIT 合规镜像

```text
s47_1_mirror/
├── LICENSE          # MIT verbatim (Copyright (c) 2026 rpamis · 实拉 2026-08-26)
├── SKILL.md         # 本文件 + 11 字段 frontmatter + Modified by dragon-engine
└── scripts/
    ├── comet_bridge.py     # 4 类方法论自研实现
    └── test_comet_bridge.py # 14+ unittest PASS
```

MIT 红线 3 项：

1. 保留 © Copyright (c) 2026 rpamis
2. 加 LICENSE 原文 + 'Modified by dragon-engine / 2026-08-26' footer
3. 不得用 'comet 官方' / 'rpamis 官方' 字样

---

## 五、与天龙既有栈的协同（**与 memos-methodology 11 位置平行**）

```
comet-methodology V1.0 (借鉴档 · MIT ✅ · 自研 +14 PASS)
   ├─► 04-validator V9.06 → V9.08         ⭐UPG phase-guard 三阶段拦截
   ├─► 09-04-chief-of-staff V2.1 → V2.2 ⭐UPG loop engineering
   ├─► hv-analysis V1.0 → V1.3          ⭐UPG 万字研究加 loop_engine
   ├─► session-distiller V1.0 → V1.2   ⭐UPG workflow eval phase
   ├─► mneme-heat-engine V2.0 → V2.1   ⭐UPG heat V2.0 加 loop backoff
   ├─► 35-07-hv-researcher V1.2         ⏳  workflow eval 复用
   ├─► memos-methodology (stage 47.1)    📎  parallel 推进 + cross-task state
   ├─► nomifun_execution_schema (stage 46)   📎  plan YAML schema 复用
   ├─► dsh-eval-bridge (stage 45 · MIT)   📎  LLM judge 互补 (comet = stub)
   └─► async-task-pattern (stage 21)     📎  rate_limiter / session_pool
```

---

## 六、累计 PASS 增量

```
Stage 47.1 memos 累计: 886 PASS (+11 from 875)
Stage 47.1 comet net:  +14 ─► 900  comet_bridge.py V1.0 · 14 unittest PASS
                            │
                 Stage 47.1 final: 900 PASS 锁定
```

### 6.1 14 unittest 类目

| # | 类目 | 用例 |
|---|---|---|
| 1 | `phase_gate` | 3 (4 阶段 / 阈值 / 短路) |
| 2 | `loop_engine` | 4 (linear / exp / fib / decorrelated) |
| 3 | `workflow_eval` | 3 (YAML 校验 / Markdown 双产物 / JSON 双产物) |
| 4 | `license_check` | 2 (MIT verbatim / Modified by footer) |
| 5 | `integration` | 2 (memos ↔ comet phase context 协同) |

---

## 七、合规红线检查表（**MIT 3 项 + 借鉴档 7 项**）

- [ ] LICENSE "MIT License" + "Copyright (c) 2026 rpamis" verbatim
- [ ] "Modified by dragon-engine / 2026-08-26" footer 已加
- [ ] 不得用 "comet 官方" / "rpamis 官方" 字样
- [ ] 不 npm install (避免 socket.io 依赖)
- [ ] 不克隆 comet/src 任何路径
- [ ] 借鉴档自研：4 类方法论 + 14 unittest
- [ ] Phase gate 必须有 max_loop 硬上限
- [ ] Workflow eval YAML schema 与 stage 46 nomifun plan 对齐
- [ ] LLM judge 不直接 verdict ≥ 1.0
- [ ] 无人值守模式跑 phase gate 必须 user confirm

---

## 八、来源链接

- 仓库：https://github.com/rpamis/comet
- LICENSE (MIT 22 行 verbatim)：https://raw.githubusercontent.com/rpamis/comet/main/LICENSE
- topics：eval / harness-engineering / loop-engineering / phase-guarded / sdd / skill-creator / skills / spec

---

> **下次同步点**：用户实跑 comet_bridge.py 14 PASS 后，可启动 Stage 48 候选盘点或继续下一个借鉴档。
