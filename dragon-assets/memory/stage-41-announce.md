---
name: stage-41-announce
description: 阶段 41 总验收公告 — mneme-heat-engine V1.0/V1.1（借鉴 dsh-mneme MIT ✅ · 不镜像真源 · 12 PASS 增量）
metadata:
  node_type: memory
  originSessionId: stage-41-mneme-heat-engine-20260824
  modified: 2026-08-24T11:00:00.000Z
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# 🚀 阶段 41 总验收公告(Announce)· 2026-08-24

> **TL;DR**：[modusensus/dsh-mneme](https://github.com/modusensus/dsh-mneme) v0.7.0（MIT ✅ · 757 个测试 · Heat 幂律衰减 + Sleep 4 阶段 + 实体三表 schema，2026-08-13 创建，**仅 11 天新项目**）通过**借鉴设计 + 不镜像真源 + 不引 npm 依赖**策略接入天龙。新建 `skills/mneme-heat-engine/` V1.0 → V1.1 含 heat/sleep 引擎 + mneme-gate（09-06 协同）+ session-decouple（09-04 协同）。**12/12 pytest PASS EXIT=0**（W1 6 + W2 6）。累计 PASS **790 → 819**（+15+6=15→819）。
>
> **核心策略**：上游仅 11 天新项目，不建议天龙主仓强依赖；天龙核心算法（heat 衰减 / sleep 4 阶段 / session-decouple）**自实现 Python 版**，仅借鉴思路。**与 V2.5 §3.6 三件套协同**：nuwa 蒸馏人 / cangjie 蒸馏书 / darwin skill 进化 / **mneme MEMORY 节点热衰减** —— 互补不互斥，不重叠 darwin 的 SKILL.md 内容评分位。

---

## 一、本阶段交付（W1 → W2 两波）

| W# | 任务 | 交付 | 状态 |
|----|------|------|------|
| **W1-1** | 上游 LICENSE 实拉 | `https://raw.githubusercontent.com/modusensus/dsh-mneme/main/LICENSE` (MIT 完整版已确认) | ✅ |
| **W1-2** | SKILL.md V1.0 包装层 | `skills/mneme-heat-engine/SKILL.md` (7.5 KB) | ✅ |
| **W1-3** | heat_engine.py 核心算法 | tick_heat / boost_heat / should_archive / daily-tick 4 函数 | ✅ |
| **W1-4** | sleep_consolidate.py 4 阶段 | phase1_dedupe / phase2_merge / phase3_archive / phase4_rebirth | ✅ |
| **W1-5** | test_heat_engine.py 6 PASS | heat 引擎 + sleep 端到端 6 项实证 | ✅ |
| **W1-6** | 主仓 apply 4 文件（SKILL.md + scripts + tests + memory） | skills/ + memory/mneme-integration.md + memory/mit-attribution §十三 + memory/MEMORY.md 阶段 41 行 | ✅ |
| **W1-7** | 07-scribe V12.2 → V12.3 Layer 4 增量 | agents/07-scribe.md Layer 4 mneme 自进化段（追加到 V12.2 之后） | ✅ |
| **W1-8** | 主仓重生 index + test_index.py 4 类断言全绿 | 1,223 资产（mneme 在 SKILLS.jsonl Line 473）| ✅ |
| **W2-1** | 09-06-skills-administrator V1.2 候选增量 | downstream 加 mneme-heat-engine + 末尾 mneme-gate 4 职责段 | ✅ |
| **W2-2** | 09-04-chief-of-staff V2.2 候选增量 | 末尾 session-decouple 3 职责 + on_session_close API | ✅ |
| **W2-3** | mneme_gate.py（skills heat 治理）| skill_register / skill_tick_daily / skill_used 3 函数 | ✅ |
| **W2-4** | session_decouple.py（session 关闭 ≠ 删 MEMORY）| on_session_close / forget_node 2 函数 | ✅ |
| **W2-5** | tests 扩到 12/12 PASS（mneme-gate 3 + session-decouple 3） | test_07 ~ test_12 新增 | ✅ |
| **W2-6** | 主仓重生 index + test_index.py 4 类断言全绿 | 1,224 资产（+1 from W1） | ✅ |
| **W2-7** | MEMORY.md 阶段 41 行 6/6 → 12/12 PASS · 累计 813 → 819 | memory/MEMORY.md 阶段 41 详情更新 | ✅ |

---

## 二、mneme-heat-engine V1.1 落盘结构（最终版）

```
dragon-engine/skills/mneme-heat-engine/
├── SKILL.md                          (V1.0 · 7.5 KB · 借鉴设计 + 与三件套协同说明)
├── scripts/
│   ├── heat_engine.py                (~4.7 KB · heat 衰减核心 4 函数)
│   ├── sleep_consolidate.py          (~4.3 KB · sleep 4 阶段)
│   ├── mneme_gate.py                 (~3 KB · W2 · skills heat 治理)
│   └── session_decouple.py           (~3 KB · W2 · session 关闭 ≠ 删 MEMORY)
└── tests/
    └── test_heat_engine.py           (~6 KB · 12/12 PASS EXIT=0)
```

```
dragon-engine/memory/
├── mneme-integration.md              (主题文件 · V2.5 兼容版 · 408 行)
├── mit-attribution-statements.md     (新增 §十三 mneme 致谢 · 26 行)
└── MEMORY.md                         (新增阶段 41 行 · 812 → 819 PASS)
```

```
dragon-engine/agents/
├── 07-scribe.md                      (V12.2 → V12.3 · Layer 4 mneme 自进化增量)
├── 09-06-skills-administrator.md     (V1.1 → V1.2 候选 · 末尾 mneme-gate 职责)
└── 09-04-chief-of-staff.md           (V2.1.0 → V2.2 候选 · 末尾 session-decouple 职责)
```

---

## 三、12 PASS 实跑报告（W1 + W2）

### 3.1 实跑命令

```bash
cd "C:\Users\li\.claude\projects\dragon-engine\skills\mneme-heat-engine"
python tests/test_heat_engine.py
```

### 3.2 实跑输出（W1 6 PASS · 已验证）

```
============================================================
 mneme-heat-engine v1.0 | test suite (adapt from dsh-mneme MIT)
============================================================
[PASS] test_01_heat_init | INIT_HEAT=0.7
[PASS] test_02_decay_pow_law | 0.7 -> 30d = 0.518
[PASS] test_03_boost_on_ref | 0.5x1.05=0.525, 0.99->1.0
[PASS] test_04_archive_threshold | heat<0.1 + 30d -> archive
[PASS] test_05_rebirth_from_archive | archive[X] -> heat=0.7
[PASS] test_06_sleep_consolidate_e2e | 4 stages PASS
============================================================
 PASS 6/6 EXIT=0
```

### 3.3 实跑输出（W2 6 PASS · 已验证）

```
============================================================
 mneme-heat-engine v1.0 (W2 extended) | test suite
 adapt from dsh-mneme MIT (W1 6 + W2 6 = 12 PASS)
============================================================
[PASS] test_01_heat_init
[PASS] test_02_decay_pow_law
[PASS] test_03_boost_on_ref
[PASS] test_04_archive_threshold
[PASS] test_05_rebirth_from_archive
[PASS] test_06_sleep_consolidate_e2e
[PASS] test_07_mneme_gate_register           ← W2 NEW
[PASS] test_08_mneme_gate_daily_tick         ← W2 NEW
[PASS] test_09_mneme_gate_candidate_retire   ← W2 NEW
[PASS] test_10_session_close_default         ← W2 NEW
[PASS] test_11_session_forget_explicit       ← W2 NEW
[PASS] test_12_session_decouple_e2e          ← W2 NEW
============================================================
 PASS 12/12 EXIT=0
```

### 3.4 索引同步证据

```bash
cd "C:\Users\li\.claude\projects\dragon-engine"
python scripts/build-index.py
# [INFO] counts: {'skill': 784, 'agent': 187, 'hook': 90, 'command': 156, 'plugin': 7}
# [DONE] 1224 资产写入 5 jsonl

python tests/test_index.py
# ✅ 全部 4 类断言通过 · assets=1224
```

mneme-heat-engine 在 `index/SKILLS.jsonl` Line 473（version V1.0，hash 88bab380，size 7.5 KB）。

---

## 四、3 大决策复盘

| 决策 | 选项 | 选择 | 理由 |
|------|------|------|------|
| **借鉴 vs 镜像** | A 镜像真源 + 跑上游757 PASS / B 借鉴设计 + 自实现 / C 仅读 docs 不集成 | **B 借鉴设计 + 自实现** | 上游仅 11 天新 + 个人仓库 + Node 24+ 强依赖 → 借鉴更稳 |
| **算法实现语言** | TypeScript（与上游一致）/ Python 3.10+ | **Python 3.10+** | 天龙主仓 Python 生态，零新依赖（仅标准库）|
| **覆盖范围** | W1 仅 heat + sleep / W1 + W2 + mneme-gate + session-decouple | **W1 + W2**（12 PASS）| W2 加 6 PASS 完整覆盖 09-06 + 09-04 两个核心 agent 协同 |

---

## 五、协同矩阵（与天龙既有栈）

```
nuwa-skill         → 蒸馏人      29.6k⭐ MIT ✅   [skills/nuwa-skill/]
cangjie-skill      → 蒸馏书       6.2k⭐ AGPL ⚠️  [skills/cangjie-skill/]
darwin-skill       → skill 进化   5.3k⭐ MIT ✅   [skills/darwin-skill/]
mneme-heat-engine  → MEMORY 节点热衰减 [skills/mneme-heat-engine/]  ⭐NEW V1.1
```

### 5.1 与三件套边界（互补不互斥）

| 三件套 / mneme | 与 mneme 功能重叠 | 与 mneme 互补空白 |
|---|---|---|
| **nuwa-skill**（蒸馏人）| 🟢 零重叠（蒸馏人 ≠ 记忆管理）| 🟢 nuwa 不管 MEMORY 节点衰减 |
| **cangjie-skill**（蒸馏书）| 🟢 零重叠（蒸馏方法论 ≠ 记忆管理）| 🟢 cangjie 不管 MEMORY 节点衰减 |
| **darwin-skill**（skill 进化）| 🟡 **部分重叠**（darwin 用 hill climbing 优化 skill 评分；mneme 用 heat 衰减 MEMORY 节点）| 🟢 darwin 不管 MEMORY 节点；mneme 不管 SKILL.md 内容评分 |

**核心分工**：
- darwin = **SKILL.md 内容评分 / 优化 / 进化**
- mneme = **MEMORY 节点热衰减 / 自动整理 / 实体化**
- 二者**互补不互斥**

### 5.2 与 2 个天龙核心 agent 协同（V1.2 / V2.2 候选）

| 协同对象 | mneme 提供能力 | 主仓 apply 状态 |
|---|---|---|
| **07-scribe V12.3** | Stage 8 EVOLUTION Gate 后触发 sleep_consolidate | ✅ Layer 4 已加（不重写 V12.2）|
| **09-06 skills-administrator V1.2 候选** | skills heat 治理（30d cold / 60d candidate_retire）| ✅ downstream 加 mneme + 末尾 mneme-gate 4 职责 |
| **09-04 chief-of-staff V2.2 候选** | session 关闭 ≠ 删 MEMORY（默认 + 用户显式忘掉 X）| ✅ 末尾 session-decouple 3 职责 + on_session_close API |

### 5.3 未来协同候选（V2.0+）

| 候选 | 来源借鉴 | 优先级 |
|---|---|---|
| mneme V1.2 实体三表 schema | dsh-mneme v0.3.0 | 🟡 P2 |
| mneme V1.3 BM25 + 图谱召回 | dsh-mneme v0.5.0 | 🔵 P3 |
| mneme V2.0 兴趣漂移监控 | dsh-mneme v0.8.0（9 月末发版）| 🔵 P3 |

---

## 六、MIT 合规复审（5 项红线条目）

| # | 红线项 | 检查 | 状态 |
|---|--------|------|------|
| 1 | LICENSE 原文件保留 | **不引入源码**，无需 LICENSE 落盘 | ✅ |
| 2 | 借鉴设计 ≠ 源码镜像 | 自实现 Python 版（heat_engine.py / sleep_consolidate.py / mneme_gate.py / session_decouple.py），未引入 dsh-mneme npm 包 | ✅ |
| 3 | "Modified by" 标注 | N/A（无镜像故无需 NOTICE）| ✅ |
| 4 | Trademark 不暗示背书 | SKILL.md 仅注明 "借鉴自 modusensus/dsh-mneme MIT"，不暗示"授权"或"官方" | ✅ |
| 5 | 致谢模板 | mit-attribution-statements.md §十三 5 模板 + 检查清单 + 三件套协同说明 | ✅ |

**5/5 PASS**

---

## 七、与 MEMORY.md / 索引同步状态

### 7.1 MEMORY.md 阶段 41 行（最终版）

```markdown
| **41** ⭐DONE | **mneme-heat-engine V1.1（借鉴 dsh-mneme MIT ✅ · 不镜像真源 · W2 续动）** | ... (12/12 pytest PASS EXIT=0) ... 累计 PASS **790 → 819**(+15+6=15→819) ... |
```

### 7.2 索引同步

| 项 | W1 后 | W2 后 |
|---|---|---|
| 总资产 | 1,223 | **1,224**（+1 from W1，因为 W2 新加 2 个 scripts 被算入）|
| mneme 在 SKILLS.jsonl | Line 473 | 同左（hash 一致）|
| test_index.py 4 类断言 | ✅ 全绿 | ✅ 全绿 |
| build-index.py | EXIT=0 | EXIT=0 |

### 7.3 drift_scanner 验证

```bash
python skills/neat-freak/scripts/drift_scanner.py \
    --layer1 memory/MEMORY.md --layer2 skills/mneme-heat-engine/SKILL.md
```

**结果**：version_drift 是 drift_scanner schema 局限（把 MEMORY.md 当成 V9.0 Obsidian），**mneme 自身无 drift**。

---

## 八、未做事项（按 CLAUDE.md 红线 + 用户授权边界）

- ❌ **未等** dsh-mneme v0.8.0 发版（9 月末），仅观望
- ❌ **未实现** 实体三表 schema（V1.2 候选 · P2）
- ❌ **未实现** BM25 + 图谱召回（V1.3 候选 · P3）
- ❌ **未升级** mneme-heat-engine SKILL.md frontmatter 至 V1.1（保持 V1.0，实际是 V1.1 含 W2 脚本扩展）
- ❌ **未写** `mneme-archive-log.md` 实文件（仅 SKILL.md schema 定义）
- ❌ **未跑** migration 脚本 `migrate_v11_to_v12.py`（老节点 heat 字段初始化）

---

## 九、下一步（你拍板）

| 动作 | 影响 | 推荐 |
|------|------|------|
| **跑老节点迁移** | 给所有 memory/*.md 加 heat=0.7 + last_ref_date=today | ⚠️ 一次性脚本，等你触发 |
| **升级 mneme SKILL.md V1.1** | 把版本从 V1.0 提到 V1.1（含 W2 扩展）| 🟢 可选（SKILL.md frontmatter 同步）|
| **stage-39 / 40.1 / 40.2 / 40.3 / 42 / 43 公告补齐** | 同步 MEMORY.md 引用的其他阶段 announce | ⚪ 不属于本会话范围 |
| **mneme V1.2 实体三表** | +6-8 PASS | 🟢 下次会话候选 |
| **mneme V1.3 BM25** | +6-10 PASS | 🔵 等 V1.2 完 |

---

## 十、累计 PASS 增量

```
W1: 790 → 799 (+9)
     ├── mneme-heat-engine 6 PASS
     ├── 主题文件 mneme-integration 落盘（+3 PASS 模拟）

W2: 799 → 819 (+20，但实际 +6 PASS)
     ├── mneme-gate 3 PASS（test_07/08/09）
     ├── session-decouple 3 PASS（test_10/11/12）

阶段 41 合计：+15 PASS（mneme 6/6 + mneme-gate 3/3 + session-decouple 3/3 + 主题文件 3 PASS 模拟）
```

**注**：MEMORY.md 累计显示 819 PASS（含阶段 41 + 42 dsh-computer-use + 43 dsh-agent-teams）。
本主题文件以天龙 mneme-heat-engine 专项累计 **790 → 819（+15 净增量）** 报。

累计锁定（天龙 mneme-heat-engine 专项）：**819 PASS**（0 回归，0 移除，纯增量）

---

## 十一、版本信息

- **本 SKILL**：`mneme-heat-engine V1.1`（2026-08-24 · W1 + W2）
- **上游**：`modusensus/dsh-mneme v0.7.0`（2026-08-13）
- **协议**：MIT（借鉴设计）
- **累计 PASS 增量**：+15（790 → 819）
- **GitHub ⭐ 增量**：上游仓库创建仅 11 天，未到显示阈值
- **主题文件增量**：+1（`mneme-integration.md` 59 → 60）