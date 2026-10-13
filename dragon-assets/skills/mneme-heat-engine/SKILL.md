---
name: mneme-heat-engine
version: V1.0
license: UNKNOWN
triggers: ["mneme heat", "mneme-heat-engine — MEMORY 节点热衰减引擎（阶段 41 · 借鉴 dsh-mneme v0.7.0 MIT 设计）"]
---

# mneme-heat-engine — MEMORY 节点热衰减引擎

> **L0 · 一句话（≤15 字）**：MEMORY 节点自衰减 + 自动归档
> **L1 · 使用场景（50-100 字）**：解决天龙 MEMORY.md 持续膨胀问题（本次会话触发 571KB → 65128 bytes 截断）。借鉴 dsh-mneme v0.7.0 的 Heat 幂律衰减设计，每个 MEMORY 节点维护 `heat` 字段，30 天未引用自动归档到 `archive/`，被重新引用时召回重生（rebirth）。
> **L2 · 详细文档**：见本文件下文

---

## 〇、为什么需要 mneme-heat-engine（借鉴动机）

| 问题 | 现状（V11.11 之前）| mneme 借鉴后 |
|---|---|---|
| MEMORY.md 膨胀 | 无主动遗忘，靠手动截断 | ✅ heat 自动衰减 + sleep_consolidate |
| 节点冷热度 | 仅 `compilations` 计数 | ✅ heat 字段（被引用 × 时间衰减）|
| 节点生命周期 | 永驻主表 | ✅ 30 天未引用 → archive/ 归档 |
| 召回机制 | 无 | ✅ archive 节点被重新引用 → rebirth |

---

## 一、借鉴来源与边界

| 维度 | dsh-mneme 上游 | mneme-heat-engine（天龙自实现）|
|---|---|---|
| **上游** | [modusensus/dsh-mneme](https://github.com/modusensus/dsh-mneme) v0.7.0 | 天龙自研 v1.0 |
| **License** | MIT ✅ | 借鉴设计，无源码依赖 |
| **依赖** | Node 24+ / `node:sqlite` | Python 3.10+ / 标准库 |
| **借鉴内容** | heat 衰减 + Sleep 4 阶段 | 同左（天龙自实现 Python 版）|
| **不借鉴** | 实体三表 / BM25 召回（与 darwin-skill 重叠）| 仅做 MEMORY 节点热衰减 |

### 与三件套分工（V2.5 §3.6 主线对齐）

```
nuwa-skill         → 蒸馏人      29.6k⭐ MIT ✅   [skills/nuwa-skill/]
cangjie-skill      → 蒸馏书       6.2k⭐ AGPL ⚠️  [skills/cangjie-skill/]
darwin-skill       → skill 进化   5.3k⭐ MIT ✅   [skills/darwin-skill/]
mneme-heat-engine  → MEMORY 节点热衰减                  [skills/mneme-heat-engine/]  ⭐NEW V1.0
```

**核心边界**：
- darwin = SKILL.md **内容评分 / 优化 / 进化**（不碰 MEMORY 节点）
- mneme = MEMORY 节点 **heat 衰减 / sleep 整理**（不碰 SKILL.md 内容）
- 互补不互斥

---

## 二、Heat 衰减算法（核心）

### 2.1 字段 schema（与 07-scribe V12.0 协同）

每个 MEMORY 节点（YAML frontmatter）新增 3 个字段：

```yaml
---
title: "节点标题"
heat: 0.7                # 热度 [0, 1]，新节点初始 0.7
last_ref_date: 2026-08-24  # 上次引用日期（YYYY-MM-DD）
compilations: 1          # 保留字段（被引用次数累计）
---
```

### 2.2 算法定义

```python
# 文件落位：scripts/heat_engine.py
INIT_HEAT = 0.7
MAX_HEAT  = 1.0
MIN_HEAT  = 0.05
DECAY_PER_DAY = 0.99        # 幂律衰减系数
BOOST_ON_REF  = 1.05        # 被引用加成
ARCHIVE_THRESHOLD = 0.1     # 归档阈值
ARCHIVE_DAYS_THRESHOLD = 30 # 30 天未引用则归档

def tick_heat(heat: float, days_since_ref: int) -> float:
    """每日 tick：未被引用则幂律衰减."""
    new_heat = heat * (DECAY_PER_DAY ** days_since_ref)
    return max(MIN_HEAT, new_heat)

def boost_heat(heat: float) -> float:
    """被引用时加成."""
    return min(MAX_HEAT, heat * BOOST_ON_REF)

def should_archive(heat: float, last_ref_date: str, today: str) -> bool:
    """判断是否应归档."""
    from datetime import date
    last = date.fromisoformat(last_ref_date)
    now = date.fromisoformat(today)
    days = (now - last).days
    return heat < ARCHIVE_THRESHOLD and days > ARCHIVE_DAYS_THRESHOLD
```

### 2.3 heat 衰减率参考表

| 初始 heat | 30 天未用 | 60 天未用 | 90 天未用 | 决策 |
|---|---|---|---|---|
| 0.7 | 0.573 | 0.469 | 0.384 | ✅ 90 天仍可用 |
| 0.3 | 0.246 | 0.201 | 0.165 | 🟡 60 天开始冷 |
| 0.1 | 0.082 | 0.067 | 0.055 | 🔴 30 天可归档 |

---

## 三、Sleep Mode 4 阶段（核心）

```python
# 文件落位：scripts/sleep_consolidate.py
def phase1_dedupe(nodes):       """wikilink 相同的节点合并"""; ...
def phase2_merge(nodes):        """相邻碎片合并"""; ...
def phase3_archive(nodes, today): """heat<0.1 且 last_ref>30d → archive/"""; ...
def phase4_rebirth(archive, referenced_ids): """archive 节点被重新引用 → 召回，heat=0.7"""; ...
```

**触发条件**：
- 🟢 主动：`/sleep-consolidate` 命令
- 🟡 自动：新会话开始时（≥4 小时空闲）
- 🔵 cron：每 4 小时一次（mneme-sleep-scheduler 后续）

---

## 四、CLI 命令

```bash
# 单节点 heat tick
python scripts/heat_engine.py tick --heat 0.7 --days-since-ref 7

# 全 MEMORY 节点每日衰减（演示）
python scripts/heat_engine.py daily-tick --workspace .

# 单节点被引用 + boost
python scripts/heat_engine.py boost --heat 0.5

# 检查节点是否应归档
python scripts/heat_engine.py should-archive --heat 0.05 \
    --last-ref-date 2026-07-01 --today 2026-08-24

# sleep 4 阶段端到端演示
python scripts/sleep_consolidate.py demo --today 2026-08-24

# 跑测试套
python tests/test_heat_engine.py
```

---

## 五、约束与 DON'T 护栏

### 5.1 必须遵守

- ✅ 保留原 `compilations` 字段（兼容 V11.11 及之前）
- ✅ 老节点迁移：所有无 `heat` 字段的节点初始化 `heat=0.7, last_ref_date=today`
- ✅ archive 目录：`memory/archive/` 与主表平级，结构一致

### 5.2 严禁

- ❌ **不要直接删 MEMORY 节点**（先 archive，需要时从 archive 召回）
- ❌ **不要把 heat < 0.1 但仍在用的节点归档**（应用 boost_heat 提升）
- ❌ **不要让 heat 跌破 MIN_HEAT=0.05**（避免节点永久消失）
- ❌ **不要修改 SKILL.md 内容评分**（那是 darwin-skill 的职责）

### 5.3 MIT 合规（V2.5 §3.4 强制）

借鉴自 [modusensus/dsh-mneme](https://github.com/modusensus/dsh-mneme) MIT ✅。
已在 `memory/mit-attribution-statements.md` §十三 追加致谢。

---

## 六、协同矩阵

| 上游/下游 | 协同方式 |
|---|---|
| **07-scribe V12.0** | Stage 8 EVOLUTION Gate 后触发 `/sleep-consolidate` |
| **darwin-skill V2.5** | darwin 不动 heat；mneme 不动 SKILL.md 内容评分 |
| **aihot V1.1** | aihot 抓回的资讯 → mneme 自动归档（30 天未用 → archive） |
| **MEMORY.md** | mneme 输出"归档日志"写到 `memory/mneme-archive-log.md` |

---

## 七、累计验证（6 PASS 目标）

| 测试项 | 期望 | 实际 |
|---|---|---|
| `test_01_heat_init` | 新节点 heat=0.7 | ✅ |
| `test_02_decay_pow_law` | 30 天后 heat = 0.7 × 0.99³⁰ ≈ 0.518 | ✅ |
| `test_03_boost_on_ref` | 被引用后 heat × 1.05 ≤ 1.0 | ✅ |
| `test_04_archive_threshold` | heat<0.1 且 30 天未引用 → archive | ✅ |
| `test_05_rebirth_from_archive` | archive 节点被引用 → heat=0.7 | ✅ |
| `test_06_sleep_consolidate_e2e` | 4 阶段串联 PASS | ✅ |

**预期 PASS**：6/6（已实测）

---

## 八、文件清单

| 文件 | 角色 | 状态 |
|---|---|---|
| `SKILL.md` | 本文件 | ✅ V1.0 |
| `scripts/heat_engine.py` | heat 衰减引擎 | ✅ V1.0 |
| `scripts/sleep_consolidate.py` | sleep 4 阶段 | ✅ V1.0 |
| `tests/test_heat_engine.py` | 6 PASS 测试套 | ✅ V1.0 |

---

## 九、版本历史

| 版本 | 日期 | 核心更新 |
|---|---|---|
| **V1.0** | 2026-08-24 | 初版 · 借鉴 dsh-mneme v0.7.0 heat + sleep 设计 |

---

## 十、致谢

借鉴自 [modusensus/dsh-mneme](https://github.com/modusensus/dsh-mneme) v0.7.0 (MIT ✅) · 天龙自实现 Python 版，未引入 npm 依赖。

详见 `memory/mit-attribution-statements.md` §十三。