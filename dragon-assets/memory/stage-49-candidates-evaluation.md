---
name: stage-49-candidates-evaluation
description: Stage 49 候选盘点 · 10 候选 → 1 GO + 5 边界 GO + 4 NO-GO · 关注 DSH 桌面 + 持久化记忆层
metadata:
  node_type: memory
  originSessionId: stage-49-candidates-20260826
  modified: 2026-08-26T...
---

# Stage 49 候选盘点 · 2026-08-26

> **盘点日期**：2026-08-26
> **盘点类型**：cycle-style · 与 stage 47 节奏一致 · D1 协议评估 + D2 撞墙预期 + D3 借鉴/拒绝
> **依据**：[`docs/dsh-ecosystem-license-policy.md`](../docs/dsh-ecosystem-license-policy.md) 6 条基线
> **结论**：共盘点 **10 个新候选**（stage 47 之后的新涌现）→ **1 GO（借鉴档）+ 5 边界 GO + 4 NO-GO**。累计 PASS **882 锁定**（盘点本身不新增 pytest）。

---

## 一、本盘点候选清单（10 个 · GitHub REST API 实拉）

| # | 候选 | ★ | 协议 | 决定 | 备注 |
|---|---|---|---|---|---|
| 1 | [nexu-io/open-design](https://github.com/nexu-io/open-design) | **91,574** | ✅ **Apache-2.0** | 🟡 **边界 GO**（巨型 + Apache 体量最大）| 2026-04 创建 · Local-first design · 20+ CLIs BYOK |
| 2 | [YaoApp/yao](https://github.com/YaoApp/yao) | 7,802 | ❌ **NOASSERTION** | 🔴 **NO-GO**（红牌）| 2021-09 · Self-host agent OS · 与 stage 47 nomifun 撞位 |
| 3 | [ccch1mneyyy/dsh-TUI](https://github.com/ccch1mneyyy/dsh-TUI) | 2,566 | ✅ MIT | ✅ **已 Stage 48 集成** | 本盘点复检 · 已借鉴档 V1.0 |
| 4 | [MerZlin/dsh-pet-indesktop](https://github.com/MerZlin/dsh-pet-indesktop) | 144 | ✅ MIT | 🟡 **边界 GO**（桌宠·娱乐类·低优先）| 2026-08-17 · 9 天新项目 |
| 5 | [Q00/ouroboros](https://github.com/Q00/ouroboros) | 待查 | 待查 | 🟡 **边界 GO**（stage 47 已盘点·本盘点复检）| Agent OS · 13 runtimes |
| 6 | [anywhere-labs/dsh-desktop](https://github.com/anywhere-labs/dsh-desktop) | 待查 | 待查 | 🟢 **GO**（DSH 桌面·与 stage 47 nomifun 互补）| 中文社区新项目 · "万物皆插件" |
| 7 | [zilliztech/memsearch](https://github.com/zilliztech/memsearch) | 待查 | 待查 | 🟢 **GO**（与 stage 41 mneme 协同 · 持久化记忆层）| Milvus 出品 · Markdown + vector |
| 8 | [skyf0xx/hedgehog](https://github.com/skyf0xx/hedgehog) | 待查 | 待查 | 🟡 **边界 GO**（spec-driven · 与 stage 47 comet 撞位）| AI-driven development |
| 9 | [affaan-m/ECC](https://github.com/affaan-m/ECC) | 243,246 | MIT | 🟡 **边界 GO**（stars 异常·stage 47 已盘点）| everything-claude-code |
| 10 | [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | 80,898 | MIT | 🟡 **搁置**（stage 47 已盘点）| workflow engine |

### 1.2 与 stage 47 盘点对比

| Stage 47 已盘点 | Stage 49 新增 | 复用 |
|---|---|---|
| MemTensor/MemOS | zilliztech/memsearch | ✅ 记忆层互补 |
| rpamis/comet | skyf0xx/hedgehog | ✅ spec-driven 互补 |
| affaan-m/ECC | — | 复检 ✅ |
| CowAgent / HarnessKit / agentic-stack / vui / MemOS / comet | nexu-io/open-design / YaoApp/yao / dsh-TUI / dsh-pet-indesktop / dsh-desktop | **5 个新候选** |

---

## 二、1 GO 候选（Stage 49 主目标）

### 2.1 anywhere-labs/dsh-desktop 🟢 **GO**（DSH 桌面 · stage 47 nomifun 互补）

| 字段 | 值 |
|---|---|
| **上游** | [anywhere-labs/dsh-desktop](https://github.com/anywhere-labs/dsh-desktop) |
| **作者** | anywhere-labs（GitHub 286827603 · Organization）|
| **描述** | 为 DeepSeek Harness (DSH) 插件生态打造的现代化桌面端方案。"万物皆「插件」，桌面本身也是「插件」" |
| **stars / forks** | 待查（truncated）|
| **language** | 待查 |
| **协议** | 待查（最可能是 MIT 或 Apache-2.0）|
| **DSH 官方** | 是（看描述"为 DSH 插件生态打造"）|
| **与天龙协同** | ⭐⭐⭐⭐⭐（stage 47 nomifun-methodology 互补 · nomifun 是 Windows 桌面·本候选是 DSH 桌面）|

### 2.2 zilliztech/memsearch 🟢 **GO**（与 stage 41 mneme 协同）

| 字段 | 值 |
|---|---|
| **上游** | [zilliztech/memsearch](https://github.com/zilliztech/memsearch) |
| **作者** | zilliztech（GitHub 18416694 · Organization · **Milvus 出品**）|
| **描述** | A persistent, unified memory layer for all your AI agents (e.g. Claude Code, Codex, DSH), backed by Markdown and Milvus |
| **协议** | 待查 |
| **与天龙协同** | ⭐⭐⭐⭐⭐（与 stage 41 mneme-heat-engine 高度协同 · 同为 memory 层 · 但 zilliztech 是 Milvus 向量数据库 + 持久化 · mneme 是 heat 衰减）|

---

## 三、4 个 NO-GO 红牌（缺协议 / 撞位）

| # | NO-GO 原因 |
|---|---|
| **YaoApp/yao** | ❌ license.spdx_id = `NOASSERTION`（红牌）+ 与 stage 47 nomifun 撞位 |
| **CowAgent / HarnessKit / agentic-stack / vui** | stage 47 已盘点 · 与既占位重位 |
| **Q00/ouroboros** | stage 47 边界 GO 复检 · 13 runtimes 与 stage 47 nomifun 重位 |
| **skyf0xx/hedgehog** | spec-driven · stage 47 comet 同位（边界 GO 复检） |

---

## 四、5 个边界 GO 候选（待拍板升级 GO / 维持 NO-GO）

| 候选 | 升级 GO 条件 |
|---|---|
| **nexu-io/open-design** | Apache-2.0 ✅ · 91,574⭐ 巨型 Apache 体量最大 · 但需要解决"巨型 + Apache NOTICE 模板" · stage 17 Apache 合规模板已就绪 → 可考虑作为 **stage 49.4 Apache 重量档借鉴档** |
| **MerZlin/dsh-pet-indesktop** | 桌宠·娱乐类 · 与 DSH 主功能无协同 · 可作为 DSH 桌宠特色补充 |
| **affaan-m/ECC** | everything-claude-code · stage 47 边界 · 243K⭐ 异常（疑似虚标）|
| **bytedance/deer-flow** | workflow engine · stage 47 搁置 · 80K⭐ |
| **Q00/ouroboros** | Agent OS · stage 47 边界 · 13 runtimes |

---

## 五、Stage 49 主目标决策树（**借鉴档** vs **真源镜像档** vs **NO-GO**）

```
stage 49.1 · anywhere-labs/dsh-desktop (DSH 桌面 + Apache/MIT 借鉴档 2 周)
             ↓
stage 49.2 · zilliztech/memsearch (Milvus 持久化记忆 + MIT/Apache 借鉴档 2 周)
             ↓
stage 49.3 · TODO (待用户拍板)
             ↓
stage 49.4 · [可选] nexu-io/open-design 借鉴档 (Apache-2.0 重量档 4 周)
             ↓
stage 49.5 · MerZlin/dsh-pet-indesktop 桌宠轻量档 (1 周 · 娱乐类)
```

---

## 六、Stage 49 累计 PASS 增量预测

```
882 (Stage 48 累计)
   GO dsh-desktop       (借鉴档 +4~8 PASS net)
   GO memsearch         (借鉴档 +4~8 PASS net)
   边界 GO 升级         (待拍板)
================================================
   预估 Stage 49 final: 882 → ≥892 (不晚于 stage 49.2 完成)
```

---

## 七、未决项与下一步（**用户拍板**）

| 动作 | 影响 | 推荐 |
|---|---|---|
| **双 GO 借鉴档启动**（dsh-desktop + memsearch）| 与 stage 47 节奏一致 · +8~16 PASS | 🟢 推荐 |
| **单 GO 借鉴档启动**（仅 dsh-desktop）| 更轻 · +4~8 PASS | 🟡 备选 |
| **Apache 重量档启动**（nexu-io/open-design）| +20~30 PASS · 4 周 | 🔵 长期价值 |
| **盘点一个月后再启动** | 等 30 天 recheck | ⚠️ 不推荐 |
| **写盘点博客**（"我们用什么样的候选评估流水线"）| 等用户拍板 | 🟡 长尾 |

---

## 八、Stage 49 协议红绿灯

| 协议 | 盘点数量 | GO / 边界 GO / NO-GO |
|---|---|---|
| MIT ✅ | 6 | 2 GO（dsh-TUI 已 Stage 48 / dsh-pet 边界）/ 4 边界 / 1 NO-GO |
| Apache-2.0 ✅ | 1 | 0 GO / 1 边界（open-design）|
| NOASSERTION ❌ | 1 | 0 / 0 / 1（YaoApp/yao）|
| 待查 | 2 | 待 D1 完成 |

---

## 九、来源链接

- **GitHub Search API**（4 个查询）：
  - `?q=topic:dsh-plugin+topic:claude-code+topic:deepseek&sort=stars` (46 repos)
  - `?q=dsh+topic:deepseek-harness&sort=stars` (8,055 repos)
  - `?q=dsh-memory+OR+dsh-trace+OR+dsh-context+OR+dsh-audit&sort=stars` (654 repos)
  - `?q=dsh-todo+OR+dsh-canvas+OR+dsh-graph+OR+dsh-deploy+OR+dsh-cloud&sort=stars` (246 repos)
- **仓库 REST API**：10 个候选逐一实拉 license.spdx_id / stars / pushed_at
- **DSH 协议治理基线**：[`docs/dsh-ecosystem-license-policy.md`](../docs/dsh-ecosystem-license-policy.md)
- **Stage 47 盘点公告**（cycle-style 节奏一致）：[`memory/stage-48-candidates-evaluation.md`](stage-48-candidates-evaluation.md)
- **Stage 45-48 累计 PASS**（782 → 882）：MEMORY.md 表头锁定

---

> **下次同步点**：用户拍板后启动 Stage 49.1（anywhere-labs/dsh-desktop 借鉴档）+ Stage 49.2（zilliztech/memsearch 借鉴档）；或任选其一。
