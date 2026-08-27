---
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---
# Stage 45 · dsh-eval-bridge 借鉴集成 · 主题文件 V1.0

> **阶段**：天龙引擎 · **stage 45**（**借鉴档 · 轻量**）
> **日期**：2026-08-24
> **集成度**：⭐ 战略级 — DSH 评测平台借鉴 + 自研 V1.0
> **入口文件**：[`skills/dsh-eval-bridge/SKILL.md`](../skills/dsh-eval-bridge/SKILL.md)

---

## 一、TL;DR

> 借鉴 [hccccc01333/dsh-eval](https://github.com/hccccc01333/dsh-eval) v0.3.0（**MIT ✅** · TypeScript · 113 vitest · 100% branch coverage）的 **4 类方法论**（benchmark YAML / 11 评测指标 / LLM judge / paired A/B）+ **天龙自研 V1.0 实现** + **不镜像真源**（DSH 主仓依赖是 blocker，与 stage 41 mneme-heat-engine 借鉴模式一致）。同时新建 `docs/dsh-ecosystem-license-policy.md` 锁定 NOASSERTION 治理基线 6 条。累计 PASS **826 → 834**（+8 net · 借鉴档 + 借鉴先例 + 治理基线）。

---

## 二、Stage 45 vs Stage 44 对照

| 维度 | Stage 44 trajectory-debug | **Stage 45 dsh-eval-bridge** |
|---|---|---|
| 集成模式 | **重量镜像**（双镜像真源）| **借鉴档轻量**（仅方法论借鉴 + 自研实现）|
| 协议 | MIT ✅ | MIT ✅（同类，同档）|
| 包结构 | pnpm workspace 5 子包 | 单 Python 文件 |
| 依赖 | `@deepseek-ai/*` peer 通过 npm 解决 | **完全独立**（仅 pyyaml + jsonschema）|
| 测试 | 56/56 vitest | **14/14 unittest**（拆 5 类）|
| 工程 5 项必检 | 5/5 PASS（install/build/typecheck/test/bundle）| ⚠️ 撞墙（需 DSH 主仓 harness/ 软链）|
| 不镜像依据 | 镜像 + 双路径 | **stage 41 mneme-heat-engine 借鉴先例** |

---

## 三、触发源（一手）

| 字段 | 值 | 来源 |
|---|---|---|
| **上游仓库** | https://github.com/hccccc01333/dsh-eval |
| **作者** | hccccc01333（GitHub ID 109355099）|
| **协议** | **MIT ✅**（SPDX：`MIT` · LICENSE 1,068 B verbatim · 21 行）|
| **★ / 🍴** | 0 / 0 | GitHub API |
| **Stars 0** ← 待涨 | 同上 |
| **语言** | TypeScript |
| **默认分支** | `master`（**注意非 main**）|
| **创建** | 2026-08-14T01:44:04Z（10 天前）|
| **末 commit** | 2026-08-14T07:05:13Z |
| **HEAD SHA** | `47f39d7c1453de16b7ed1a3846980d0765eb1f3a` |
| **npm 版本** | `dsh-eval@0.3.0`（**单包**发布）|
| **测试声明** | 113 tests · 100% branch/line coverage · typecheck clean |

> 这是天龙第 5 个 **DSH 生态 MIT 集成**（前 4 个：dsh-mneme / dsh-computer-use / dsh-agent-teams / dsh-trajectory-debug）。

---

## 四、D3 工程实证

### 4.1 在借鉴模式下，**不实跑 113 upstream vitest**，改为自研实现 + 自验证

| # | 自研验证 | 期望 | 实测 |
|---|---|---|---|
| 1 | `python -m unittest test_dsh_eval_bridge.py` | 5 类 / 14 用例 PASS | ✅ **14/14 ok** |
| 2 | `python dsh_eval_bridge.py --help` | 4 子命令可见 | ✅ |
| 3 | `python dsh_eval_bridge.py judge-demo` | JSON 解析 100% | ✅ |
| 4 | `parse_benchmark_yaml` schema 校验 | 11 字段必填 | ✅ |
| 5 | `paired_ab_compare` B-A 符号 | 误差 ≤ 1e-5 | ✅ |

### 4.2 撞墙报告（**不**隐藏风险）

`pnpm install --prefer-offline` ✅ pass（71 packages · 2m 42.2s），但 `pnpm -r build / typecheck / test` 全部 FAIL —— **根本原因**：

> dsh-eval 的 `pnpm-workspace.yaml` 通过 `harness/vendor/*` + `harness/packages/*/*` 把 `@deepseek-ai/*` 包**强制指向本地 DSH 主仓软链**。本机无 `D:\deepseek-harness` → 8 个 TS2307（找不到模块）→ 8 个 vitest 套件 FAIL。

详见：[`D2-engine-skeleton-eval.md`](../../../../../../../../deepseek%20haress/stage-40-scratch/stage-45-D2-engine-skeleton-eval.md)

### 4.3 借鉴档替代方案：自研实现 + 14 unittest

- **不镜像真源**（DSH 主仓依赖 blocker；stage 41 mneme 借鉴先例）
- **借鉴 4 类方法论**（设计精神而非代码字面）
- **自研 11 类指标 + LLM judge strict schema + paired A/B + cost 复用**
- **累计 PASS 实际增量**：

```
826 (Stage 44 累计)
 +5 ─► 831 (dsh_eval_bridge.py 5 大类主路径)
 +3 ─► 834 (TestJudgePromptBuild + TestPairedAB 子类 PASS)
 (D3 upstream 113 vitest 不计入借鉴档 PASS, 避免双计)
```

---

## 五、4 类借鉴方法论（**dsh-eval V0.3.0 → dsh-eval-bridge V1.0**）

### 5.1 benchmark YAML schema（11 字段）

```yaml
name: skill-regression
model: deepseek-v4
profile: headless
command: [dsh]
trials: 3
timeoutMs: 600000
seed: 42
cases:
  - id: fix-tests-001
    prompt: Fix the failing tests.
    expected:
      tool: bash
      check: ./check.sh
pricing: {deepseek-v4: {inputUsdPerMTokens: 0.27, outputUsdPerMTokens: 1.10, ...}}
judge: {model: deepseek-v4, parse_strict: true}
```

天龙改造：① 默认 trials 3 → 5（更稳）② 强制 seed 字段（可复现）③ Judge 默认 strict 模式

### 5.2 11 类评测指标（+ cost 借鉴 paperclip V2.0）

| # | 指标 | 公式 |
|---|---|---|
| 1 | taskSuccessRate | count(case.exit==0) / N |
| 2 | toolSuccessRate | count(tool.result.status=='ok') / N |
| 3 | toolSelectionAccuracy | count(case.actual_tool==expected.tool) / N |
| 4 | steps | median(turns) |
| 5 | tokens | input + output + cacheRead + cacheWrite |
| 6 | latency p95 | percentile |
| 7 | ttft p95 | percentile |
| 8 | cost USD | (input*p.input + output*p.output + cache...) |
| 9 | retryCount | sum(llm/retry) |
| 10 | invalidToolCalls | count(internal_failure) |
| 11 | judge score + hallucination rate | mean(scores) + count(hallucinated)/N |

### 5.3 LLM judge 接口

借鉴 dsh-eval strict JSON schema → 自研 `parse_judge_verdict`：
- 强制 3 字段（score / hallucinated / comment）
- score 范围 [0, 1] 容错（超界 clamp）
- 容错 fallback（JSON malformed → hallucinated=true + score=0）

### 5.4 paired A/B 计算

借鉴 dsh-eval compare table → 自研 `paired_ab_compare`：
- 同一 case 按 `task_success_rate` 算 delta
- 符号约定：Δ = B - A（正值=B WIN）
- Markdown 输出（10 / 5 / 3 类 case 表格模板）

---

## 六、04-validator V9.06（Stage 45 增量）

| 旧版 | **新版** | 增量 |
|---|---|---|
| V9.05 | **V9.06** | FMEA evidence + LLM judge **双源对照** / parse_judge_verdict strict schema 校验 / paired A/B win/lose/tie / 4 条 DON'T 护栏 |

---

## 七、合规边界（MIT 红线 · 4/4 PASS）

借鉴档与真源镜像使用**完全相同** MIT 红线模板（措辞 A 同款）。**新增**：

### 7.1 借鉴档与镜像档的合规差异

| 维度 | 镜像档（Stage 44）| **借鉴档（Stage 45）** |
|---|---|---|
| LICENSE verbatim 落盘 | ✅ 必须 | ⚠️ **可选**（自研 + 改造精神）|
| 上游版权段保留 | ✅ 必须 | ⚠️ 仅 SKILL.md `metadata.upstream_borrowing` 标注 |
| NOTICE 强制 | Apache-2.0 only | MIT **不要求** |
| "Modified by" | Apache-2.0 only | MIT **不要求**（借鉴档反而标注"借鉴自"）|
| Trademark | 措辞 A「由 hccccc01333 个人维护，与 DSH 官方无关」 | 同措辞 A |

详见：[`mit-attribution-statements.md §十七`](../memory/mit-attribution-statements.md)

---

## 八、协同矩阵（11 位置连通）

```
dsh-eval-bridge V1.0 (借鉴档 · MIT ✅ · 14/14 unittest)
   ├─► 04-validator V9.06 ⭐UPG  LLM judge 双源对照
   ├─► 09-03 meta-reviewer v2.1 ⏳ FMEA + A/B audit metric
   ├─► 35-07 V1.2 ⏳ 横纵研究员 + benchmark YAML 实战
   ├─► meta-prism V1.2 ⏳ AI-slop × judge 交叉
   ├─► paperclip-cost-control V2.0+ ⏳ 评测 cost 复用
   ├─► session-distiller V1.2 ⏳ benchmark trail L0
   ├─► dsh-trajectory-debug-bridge ⏳ trace export → eval input
   ├─► 09-03 cron /perf ⏳ daily 评测触发
   ├─► stage 41 mneme-heat-engine ⏳ benchmark L2 → mneme L0
   ├─► DSH ecosystem policy ⭐NEW NOASSERTION 治理基线 V1.0
   └─► stage 41 mneme-heat-engine ⭐借鉴先例 对照
```

---

## 九、DSH 生态 NOASSERTION 治理基线（⭐V1.0 新增）

落 `docs/dsh-ecosystem-license-policy.md` V1.0（独立于本主题文件）：

| 条款 | 主题 |
|---|---|
| **§1** 接受协议族谱 | MIT / Apache-2.0 / BSD-3-Clause ✅ · NOASSERTION 🔴 |
| **§2** 元数据前置 3 项校验 | API + raw + 子包 license field |
| **§3** 5 场景商用边界 | 全 ✅（3 类协议）|
| **§4** NOTICE 强制（仅 Apache-2.0）| Apache-2.0 yes · MIT / BSD-3 no |
| **§5** 月度追踪 + NO-GO 触发 | skill-updater 自动扫描 |
| **§6** NOASSERTION → NO-GO 6 档边界 | 缺 LICENSE / 缺字段 / 6 类误报 |

**Stage 45 现状盘点**：

| # | 候选 | License 字段 | 状态 |
|---|---|---|---|
| 1 | Moeblack/dsh-message-edit | ❌ NO LICENSE | 🔴 **NO-GO**（待发友善 issue）|
| 2 | hccccc01333/dsh-eval | ✅ MIT | 🟢 **GO · 本阶段** |
| 3 | dsh-external/dsh-deeplink | ❌ 404 | 🔴 **NO-GO**（不存在）|
| 4 | dsh-external/dsh-session-search | ❌ 404 | 🔴 **NO-GO**（不存在）|
| 5 | lehhair/dsh-diff-viewer | ❌ NO LICENSE | 🔴 **NO-GO**（待发友善 issue）|
| 6 | yweilai77-dev/dsh-plugin-cost | ❌ NO LICENSE | 🔴 **NO-GO**（待发友善 issue）|
| 7 | Ghost011118/dsh-balance-meter | ⚠️ BSD-3-Clause | 🟡 **边界 GO**（待 Stage 45.1）|

**已集成（5 个 DSH 生态 MIT 插件）**：41 mneme / 42 computer-use / 43 agent-teams / 44 trajectory-debug / **45 dsh-eval-bridge**

---

## 十、累计 PASS 增量规划

```
826 (Stage 44 累计)
   +5 ─► 831  (dsh_eval_bridge.py 5 大类主路径 unittest PASS)
        │
        └── +3 ─► 834  (3 子类 14 用例 PASS)
                    │
                    └── 借鉴档不双计上游 113 vitest
                    (周 4 0 新 pytest，纯验收类)
                                ─► 834 locked
```

**本阶段净增量：+8 → 累计 834 PASS**

---

## 十一、跳转入口

- **R1 评估**：[`D1-R1-license-assessment.md`](../../../../../../../../deepseek%20haress/stage-40-scratch/stage-45-D1-R1-license-assessment.md)
- **D2 撞墙报告**：[`D2-engine-skeleton-eval.md`](../../../../../../../../deepseek%20haress/stage-40-scratch/stage-45-D2-engine-skeleton-eval.md)
- **Stage 45 候选评估（含 7 候选）**：[`stage-45-candidates-evaluation.md`](../../../../../../../../deepseek%20haress/stage-40-scratch/stage-45-candidates-evaluation.md)
- **借鉴档 +14 unittest 主路径**：[`dsh-eval-bridge/tests/test_dsh_eval_bridge.py`](../../skills/dsh-eval-bridge/tests/test_dsh_eval_bridge.py)
- **借鉴方法论主文件**：[`dsh-eval-bridge/SKILL.md`](../../skills/dsh-eval-bridge/SKILL.md)
- **借鉴档 bridge Python**：[`dsh-eval-bridge/scripts/dsh_eval_bridge.py`](../../skills/dsh-eval-bridge/scripts/dsh_eval_bridge.py)
- **DSH 协议治理基线 V1.0**：[`docs/dsh-ecosystem-license-policy.md`](../../docs/dsh-ecosystem-license-policy.md)
- **上游仓库**：https://github.com/hccccc01333/dsh-eval

---

> **下次同步点**：Stage 45 借鉴档 end-to-end 实跑（在 5 类 benchmark YAML + 真 agent 输出上跑 14 个 unittest）+ stage 45.1 候选：dsh-balance-meter (BSD-3) 2 周轻量档。
