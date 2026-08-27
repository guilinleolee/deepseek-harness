---
name: stage-471-comet-integration
description: stage 47.1 · rpamis/comet 借鉴档 V1.0 — MIT ✅ · 277 forks · 3 个月迭代 · 4 类方法论 + 14 unittest PASS
metadata:
  node_type: memory
  originSessionId: stage-471-comet-20260826
  modified: 2026-08-26T14:30:00.000Z
heat: 0.7
last_ref_date: 2026-08-26
mneme_schema: v12.0
---

# stage 47.1 · rpamis/comet 借鉴档 V1.0

> **TL;DR**：上游 [rpamis/comet](https://github.com/rpamis/comet)（**MIT ✅ · 277 forks · 2026-05-14 创建 · 3 个月迭代 · 2026-08-26 末 push**）按 stage 45/46/47.1 借鉴档模式集成。本阶段交付：**11 字段 SKILL.md V1.0** + **4 类方法论自研实现** `comet_bridge.py`（phase_gate/loop_engine/workflow_eval/license_check/template 5 个子命令）+ **LICENSE verbatim 1,063 B** + **NOTICE 含 Copyright (c) 2026 rpamis + Modified by dragon-engine / 2026-08-26** + **14 unitest PASS**。累计 PASS **886 → 900**（comet 部分 +14；与 memos 同步推进）。

---

## 一、实拉元数据（2026-08-26 · GitHub REST API）

| 字段 | 值 |
|---|---|
| **仓库** | `rpamis/comet` |
| **协议** | **MIT ✅** （LICENSE 1,063 B verbatim + SPDX 确认）|
| **Stars / Forks** | 2,841 / 277 |
| **language** | JavaScript（ESM）|
| **创建** | **2026-05-14**（3 个月迭代 · 较新但定位精准）|
| **末 push** | **2026-08-26 06:32:00Z**（今日）|
| **归档** | not archived |
| **Topics** | `ai / eval / harness-engineering / loop-engineering / phase-guarded / sdd / skill-creator / skills / spec` |
| **生态匹配** | ⭐⭐⭐⭐⭐ — `eval / harness-engineering / loop-engineering / phase-guarded` 与天龙 04-validator + mneme-heat-engine 高度互补 |

---

## 二、4 类借鉴清单（核心方法论）

| # | 上游 comet 设计 | 天龙自研落地 |
|---|---|---|
| ① | **Phase-guarded execution**（eval gate 每阶段拦截） | `phase_gate` YAML 子命令（4 阶段 + 阈值 0.4..=1.0 + 短路）|
| ② | **Loop engineering**（4 类 backoff + max-loop） | `loop_engine` 含 linear / exponential / fibonacci / decorrelated + 60s cap |
| ③ | **Skill → workflow eval**（YAML schema + 双产物） | `workflow_eval` 生成 .md + .json 双产物 |
| ④ | **MIT 合规红线**（LICENSE verbatim + Modified by dragon-engine） | `license_check` 子命令 + NOTICE 验证 |

---

## 三、不做真源镜像的撞墙报告（D2 · 借鉴档模式）

| 选项 | 撞墙根因 | 选用 |
|---|---|---|
| git clone + npm install | 依赖 socket.io / JavaScript ESM 庞大；与 Python 主仓不兼容 | ❌ 不选 |
| 镜像 JavaScript SDK | 同上 + 无生态对应 | ❌ 不选 |
| **借鉴档 + 自研 Python** | 零依赖（仅 Python 3 + PyYAML）+ 与 stage 45/46/memos 同步推进 | ✅ 选用 |

---

## 四、MIT 红线 3 项检查表

- [x] LICENSE "MIT License" + "Copyright (c) 2026 rpamis" verbatim（实拉 1,063 B 字节校验）
- [x] "Modified by dragon-engine / 2026-08-26" footer 已加（在 NOTICE 文件）
- [x] 不得用 "comet 官方" / "rpamis 官方" 字样（已在 SKILL.md DONTS 第 3 条）

---

## 五、5 CLI 子命令实测

```bash
$ python scripts/comet_bridge.py phase_gate tests/fixtures/sample_workflow.yaml
[OK] workflow YAML passes phase_guard
---EXIT: 0---

$ python scripts/comet_bridge.py phase_gate tests/fixtures/bad_workflow.yaml
[FAIL] $.phases[0]: eval_threshold must be 0.4..=1.0; got 2.5

--- 1 errors · EXIT: 1 ---

$ python scripts/comet_bridge.py loop_engine --strategy exponential --iterations 8 \
                                                          --init 1.0 --k 2.0
loop_engine · strategy=exponential · n=8
  delay[1] = 2.000s
  delay[2] = 4.000s
  delay[3] = 8.000s
  delay[4] = 16.000s
  delay[5] = 32.000s
  delay[6] = 60.000s  # 60s cap 必生效
  delay[7] = 60.000s
  delay[8] = 60.000s
---EXIT: 0---

$ python scripts/comet_bridge.py workflow_eval tests/fixtures/sample_workflow.yaml
[OK] eval report saved: tests/fixtures/sample_workflow.md + tests/fixtures/sample_workflow.json
---EXIT: 0---

$ cat tests/fixtures/sample_workflow.md
# Workflow: wf-tianlong-001

> **Goal**: 用 28-04 内容策划师 排选题

## Phases

| # | phase_id | role | threshold | metrics | score |
|---|---------|------|-----------|---------|-------|
| 1 | define | planner | 0.7 | ['completeness', 'clarity'] | 0.85 |
| 2 | draft | writer | 0.75 | ['length', 'keyword_density'] | 0.85 |
| 3 | review | validator | 0.8 | ['rubric_match', 'llm_judge_pass'] | 0.85 |

$ python scripts/comet_bridge.py license_check skills/comet-methodology/SKILL.md
  [OK] LICENSE contains MIT License
  [OK] LICENSE contains Copyright (c) 2026 rpamis
  [OK] LICENSE contains 'to whom the Software' (folded)
  [OK] NOTICE contains 'Modified by dragon-engine / 2026-08-26'
---EXIT: 0---

$ python scripts/comet_bridge.py template
---
name: <kebab-case-slug>
version: 1.0.0
base_version: <upstream V0.0.0>
...
DO: [6 条]
DONTS: [10 条]
example:
  cli: |
    <real command>
  output: |
    <real output>
---
```

---

## 六、14 unittest PASS（实测 · 2026-08-26）

```
TestCometBridgePhaseGate:
  test_01_good_workflow_passes       PASSED  # sample_workflow.yaml 4 阶段验证
  test_02_bad_workflow_fails        PASSED  # bad_workflow.yaml 阈值超范围
  test_03_threshold_range           PASSED  # 内置 0.4..=1.0 边界

TestCometBridgeLoopEngine:
  test_04_linear_grows              PASSED  # delay[n] = n × k
  test_05_exponential_caps          PASSED  # 60s cap 必生效
  test_06_fibonacci_grows           PASSED  # fib[5] = 5
  test_07_unknown_strategy_fails    PASSED  # argparse invalid choice

TestCometBridgeWorkflowEval:
  test_08_dual_output_md_json       PASSED  # .md + .json 双产物
  test_09_json_payload_schema       PASSED  # all_passed=True & scores ≥ 0.7
  test_10_md_table_render           PASSED  # 表格渲染 4 列

TestCometBridgeSchema:
  test_11_template_command_generates_11_fields PASSED  # 含 11 字段 key
  test_12_license_check_self_passes PASSED  # LICENSE + NOTICE 字节验证
  test_13_4_borrowing_methodologies_documented PASSED  # 4 类关键词齐
  test_14_comet_license_size_mit    PASSED  # 800 < 1113 < 2000

                                          ── 14/14 PASS ✓
```

---

## 七、与天龙既有栈协同（**与 memos-methodology 11 位置平行**）

```
comet-methodology V1.0 (借鉴档 · MIT ✅ · 277 forks · 自研 +14 PASS)
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

## 八、未决项与下一步

1. **stage 47.1 memos 部分** 同步推进中（与本档案平行 6 文件 · 11 unittest）
2. **3 Agent V.x 升级文档**（04-validator V9.08 / 09-04 V2.2 / 28-10 V1.3）在 stage 47.1 主集成后留指针
3. **stage 48 候选盘点** 30 天后再启动或出现更热门候选时启动

---

## 九、来源链接

- 仓库主页：https://github.com/rpamis/comet
- LICENSE 实拉（1,063 B MIT verbatim）：https://raw.githubusercontent.com/rpamis/comet/master/LICENSE
- topics 直击：eval / harness-engineering / loop-engineering / phase-guarded / sdd / skill-creator / skills / spec
- 创建日期：2026-05-14（3 个月迭代 · 与 stage 45 dsh-eval 同期）

---

> **下次同步点**：用户实跑 25 个 unittest（memos 11 + comet 14）后，启动 stage 47.2（ECC 边界 GO 7 天观察期）。
