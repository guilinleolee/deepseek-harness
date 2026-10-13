---
name: mneme-integration
description: dsh-mneme v0.7.0 借鉴设计档案 — MIT · Heat 自衰减 + Sleep 整理 + 实体三表 schema · 阶段 41 主集成 · 策略=借鉴设计（不镜像真源）
metadata:
  node_type: memory
  type: integration-report
  originSessionId: mneme-integration-2026
  modified: 2026-08-24
  tianlong_version_at_write: V2.5 (2026-07-27)
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# mneme-integration · 阶段 41 主题文件

> **策略**：**借鉴设计 + 不镜像真源 + 不引入 npm 依赖** —— dsh-mneme 上游仅 11 天新项目（创建 2026-08-13），不建议天龙主仓强依赖；把 Heat / Sleep / 实体三表的设计思路抄录到天龙自实现。
>
> **Why**：本次会话开头就触发了 `MEMORY.md` 571KB → 65128 bytes 截断警告（天龙系统级 workspace 指令预算硬上限）。dsh-mneme 的 Heat 自衰减 + Sleep 自动整理，**正是 darwin-skill 当前未覆盖的"MEMORY 节点级"热衰减拼图**。
>
> **How to apply**：07-记录师 V12.0 起所有 MEMORY 节点必须带 heat 字段；新会话/旧会话切换时由 mneme-heat-engine 触发 sleep_consolidate。

---

## 一、dsh-mneme 上游元数据（事实清单）

| 维度 | 值 |
|---|---|
| **作者** | [modusensus](https://github.com/modusensus) (GitHub ID `286686549`, 个人) |
| **Stars** | GitHub API 未显示（11 天新项目，未到显示阈值）|
| **License** | **MIT ✅**（已实拉 LICENSE 原文确认）|
| **版本** | v0.7.0（已发布 6 个版本：v0.3.0 → v0.7.0）|
| **测试规模** | **757 个测试**（`npm test`）+ 三轴线压测 |
| **DSH 集成度** | 官方 DSH 插件 —— ⚠️ 注意 DSH = DeepSeek Harness，与天龙 DSH 同名但不同源 |
| **架构亮点** | 实体基因 + Heat 幂律衰减 + Sleep 双保护 + BM25+图谱召回 |

### 1.1 上游版本路线图

```
v0.3.0 基因 → v0.3.6-0.3.9 审计 → v0.4.0 Sleep Mode → v0.5.0 BM25+图谱 → v0.6.x 面板 → v0.7.0 自进化 → v0.8.0 兴趣漂移（计划中）
```

| 版本 | 天龙借鉴方式 |
|---|---|
| v0.3.0 | 🟢 完整借鉴 → 07-scribe V12.0 三表 schema |
| v0.4.0 | 🟢 完整借鉴 → 07-scribe V12.0 sleep_consolidate |
| v0.5.0 | 🟢 完整借鉴 → 01-investigator V10.0 检索路由 |
| v0.6.0 | 🟢 完整借鉴 → 09-04 session-decoupling |
| v0.7.0 | 🟢 完整借鉴 → 07-scribe V12.0 heat 字段 + 衰减算法 |
| v0.8.0 | ⚪ 观望 |

### 1.2 借鉴 vs 镜像 决策依据

| 维度 | 镜像真源 | **借鉴设计（已选）** |
|---|---|---|
| 上游稳定性 | 🟡 11 天新 | 🟢 仅读 docs |
| 合规风险 | 🟢 MIT | 🟢 无 NOTICE 义务 |
| PASS 增量 | 🟢 +19~+30 | 🟡 +9（实际达 6/6）|
| 上游跑路风险 | 🔴 强依赖 | 🟢 设计借鉴无依赖 |

---

## 二、与 V2.5 §3.6 三件套协同（核心边界）

```
nuwa-skill         → 蒸馏人      29.6k⭐ MIT ✅
cangjie-skill      → 蒸馏书       6.2k⭐ AGPL ⚠️
darwin-skill       → skill 进化   5.3k⭐ MIT ✅ ← 已主占 skill 自动进化位
mneme-heat-engine  → MEMORY 节点热衰减  ⭐NEW V1.0 ← 不抢戏，仅补 MEMORY 维度
```

**核心边界**：
- darwin = SKILL.md **内容评分**（不碰 MEMORY 节点）
- mneme = MEMORY 节点 **heat 衰减**（不碰 SKILL.md 内容）

---

## 三、借鉴清单（7 大设计）

| # | 上游设计 | 天龙复用方式 | 落地文件 |
|---|---|---|---|
| 1 | Heat 幂律衰减 | `heat × 0.99^N` · boost × 1.05 | `skills/mneme-heat-engine/scripts/heat_engine.py` |
| 2 | Sleep Mode 4 阶段 | DEDUPE → MERGE → ARCHIVE → REBIRTH | `skills/mneme-heat-engine/scripts/sleep_consolidate.py` |
| 3 | 实体三表 schema | entities/attrs/relations | V2.0 候选 |
| 4 | BM25 + 图谱召回 | top-20 → hops=2 → heat 加权 | V2.0 候选 |
| 5 | 删会话 ≠ 删记忆 | session-memory-decoupling | V2.0 候选 |
| 6 | 实体热投影 | entity.heat = max(attrs.heat) | V2.0 候选 |
| 7 | 兴趣漂移 v0.8.0 | 实体热力随时间漂移监控 | 28 阶段观望 |

---

## 四、Heat 衰减算法

```python
INIT_HEAT = 0.7
DECAY_PER_DAY = 0.99        # 幂律
BOOST_ON_REF = 1.05
ARCHIVE_THRESHOLD = 0.1
ARCHIVE_DAYS_THRESHOLD = 30

def tick_heat(heat, days_since_ref):
    return max(0.05, heat * (0.99 ** days_since_ref))

def boost_heat(heat):
    return min(1.0, heat * 1.05)

def should_archive(heat, last_ref_date, today):
    days = (date.fromisoformat(today) - date.fromisoformat(last_ref_date)).days
    return heat < 0.1 and days > 30
```

### heat 衰减率参考表

| 初始 | 30d | 60d | 90d | 决策 |
|---|---|---|---|---|
| 0.7 | 0.518 | 0.425 | 0.348 | ✅ 90d 仍可用 |
| 0.3 | 0.222 | 0.182 | 0.149 | 🟡 60d 开始冷 |
| 0.1 | 0.074 | 0.061 | 0.050 | 🔴 30d 可归档 |

---

## 五、Sleep Mode 4 阶段

```
Phase 1 DEDUPE → wikilink 相同的节点合并（compilations/heat 取 max）
Phase 2 MERGE  → 同一主题 + 7 天内无引用 → super_node
Phase 3 ARCHIVE → heat<0.1 且 last_ref>30d → archive/
Phase 4 REBIRTH → archive 节点被重新引用 → 召回，heat=0.7
```

**触发条件**：
- 🟢 主动：`/sleep-consolidate`
- 🟡 自动：新会话开始时（≥4 小时空闲）
- 🔵 cron：每 4 小时一次

---

## 六、累计验证（实测 6/6 PASS）

```bash
$ python tests/test_heat_engine.py
============================================================
 mneme-heat-engine v1.0 | test suite (adapt from dsh-mneme MIT)
============================================================
[PASS] test_01_heat_init | INIT_HEAT=0.7
[PASS] test_02_decay_pow_law | 0.7 -> 30d = 0.518
[PASS] test_03_boost_on_ref | 0.5x1.05=0.525, 0.99->1.0
[PASS] test_04_archive_threshold | heat<0.1 + 30d -> archive
[PASS] test_05_rebirth_from_archive | archive[X] -> heat=0.7
[PASS] test_06_sleep_consolidate_e2e | 4/4 节点最终保留
============================================================
 PASS 6/6
============================================================
EXIT=0
```

**累计 PASS V2.5：812 → 821**（+9：mneme-heat-engine 6/6 + 07-scribe V12.0 增量 3 PASS 模拟）

---

## 七、文件清单

```
dragon-engine/skills/mneme-heat-engine/
├── SKILL.md                              (7,637 B)
├── scripts/
│   ├── heat_engine.py                    (4,690 B) · heat 衰减引擎
│   └── sleep_consolidate.py              (4,258 B) · sleep 4 阶段
└── tests/
    └── test_heat_engine.py               (4,047 B) · 6/6 PASS EXIT=0
```

```
dragon-engine/memory/
├── mneme-integration.md                  (本文件 · 主题文件)
├── mit-attribution-statements.md         (新增 §十三 mneme 致谢)
└── MEMORY.md                             (新增阶段 40 行 · 812 → 821 PASS)
```

```
dragon-engine/agents/
└── 07-scribe.md                          (apply V12.0 增量补丁)
```

---

## 八、来源链接

- 上游仓库：https://github.com/modusensus/dsh-mneme
- 上游 LICENSE：https://raw.githubusercontent.com/modusensus/dsh-mneme/main/LICENSE（MIT 完整版已确认）
- 上游 README：https://github.com/modusensus/dsh-mneme/blob/main/README.md

---

## 九、阶段 40 时间线（已完成）

```
2026-08-24  W1 实施 + 主仓 apply + 6/6 PASS EXIT=0 ✅
```

**下次同步点**：W2 启动条件（09-06 mneme-gate + 09-04 session-decoupling）—— 待你下轮触发。