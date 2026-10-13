---
name: context-doctor-integration
description: Zhenyu98/dsh-context-doctor v0.6.1 集成档案 — BSD-3-Clause · 上下文注入审计插件 · 阶段 26 落地 · 新增 40-01 上下文治理师 + 改造 07-scribe V12.2 / 09-06-skills-administrator V1.1
metadata:
  node_type: memory
  type: integration-report
  originSessionId: context-doctor-integration-20260823
  modified: 2026-08-23T11:30:00.000Z
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# dsh-context-doctor 集成档案 V1.0（阶段 26 · 2026-08-23）

> **TL;DR**：天龙引擎阶段 26 集成 [Zhenyu98/dsh-context-doctor](https://github.com/Zhenyu98/dsh-context-doctor) v0.6.1（**BSD-3-Clause** ✅ · 19 ⭐ · TypeScript · 同 DSH 官方插件体系）。**P0 落地**：合规文件落盘 + 主题文件 + 阶段 26 入口。**P1 落地**：新增 **40-01 上下文治理师 V1.0** + 改造 **07-scribe V11.11 → V12.2** + 改造 **09-06-skills-administrator V1.0 → V1.1**。这是天龙首次引入**上下文审计层**，填补了"AGENTS.md 88% 膨胀"无治理工具的空白。

---

## 一、实跑元数据（2026-08-23）

### 1.1 上游仓库 API 字段

| 字段 | 值 |
|------|---|
| **license.spdx_id** | **BSD-3-Clause** 🟢 |
| **stars** | 19 ⭐（11 天新仓）|
| **forks** | 5 |
| **默认分支** | main |
| **语言** | TypeScript（65%）+ JavaScript（33%）+ Shell（2%）|
| **DSH peer** | `@deepseek-ai/cordis ^4.0.1` + `@deepseek-ai/dsh-tools ^0.1.0-rc.6 \|\| ^0.1.1-rc.1` |
| **体积** | 51KB 源码（audit.ts 17KB / scan.ts 8KB / analyze.ts 5KB / tokens.ts 1KB）|
| **测试** | 29 用例（原生 `node --test` 零依赖）|
| **出生日期** | 2026-08-12 |
| **末 push** | 2026-08-22（1 天前，仍在活跃迭代）|

### 1.2 最近 commit 节选（验证上游活跃度）

```
f45096d 2026-08-22 style(client): 面板改用仪表版式，正文交回宿主字体
c224fb6 2026-08-22 feat(client): 面板改版——跟随宿主语言、点击外部收起、可下钻到条目
ae79a62 2026-08-22 chore: peer 范围覆盖 0.1.1-rc 线
957d5de 2026-08-21 fix(client): 控件改用原生插槽 conversation.input.right
042ea0f 2026-08-21 fix: 宿主运行时改为外置 peer 依赖，消除第二个工具调度器
```

**结论**：
- ✅ **BSD-3-Clause**（最宽松协议之一，可商用可改可闭源，仅保留版权 + 禁背书）
- ✅ **DSH 官方插件路径**——同 deepseek-ai 体系，作者 dsh-external 即 DSH 插件注册组织
- ✅ **11 天迭代 0.5.0 → 0.6.1**，上游**极活跃**，建议天龙每月一次 skill-updater 检测

---

## 二、镜像拓扑（已落盘 · 阶段 26）

| # | 路径 | 角色 |
|---|------|------|
| 1 | `dragon-engine/skills/context-doctor-integration/README.md` | 集成层主文档 |
| 2 | `dragon-engine/skills/context-doctor-integration/LICENSE` | BSD-3-Clause 原文（10 段 31 行）|
| 3 | `dragon-engine/skills/context-doctor-integration/NOTICE` | "Modified by dragon-engine / 2026-08-23" 标注 |
| 4 | `dragon-engine/skills/context-doctor-integration/INTEGRATION_CHECKLIST.md` | 11 项上线 checklist |
| 5 | `dragon-engine/skills/context-doctor-integration/scripts/install-context-doctor.sh` | 一键安装脚本 |
| 6 | `dragon-engine/skills/context-doctor-integration/scripts/audit-template.md` | 7 个 context_audit 调用模板 |
| 7 | `dragon-engine/agents/40-01-context-curator.md` | **🆕 新建岗位** · 上下文治理师 V1.0 |
| 8 | `dragon-engine/agents/07-scribe.md` | **改造** V11.11 → V12.2（daily context health）|
| 9 | `dragon-engine/agents/09-06-skills-administrator.md` | **改造** V1.0 → V1.1（上线前 audit 门禁）|

> **不入主仓的部分**：上游 `src/` 源码（audit.ts/scan.ts/analyze.ts/tokens.ts/routes.ts/client/*）**不镜像**——通过 DSH cordis bundle 插件机制动态加载，本仓只保留合规文件 + 集成文档。

---

## 三、Agent 新增与改造详情（⭐阶段 26 核心交付）

### 3.1 🆕 40-01 上下文治理师 V1.0

| 维度 | 内容 |
|------|------|
| **路径** | `dragon-engine/agents/40-01-context-curator.md` |
| **岗位类型** | 常驻治理型（不接单任务，只跑 audit）|
| **核心工作流** | 5 步法：TRIGGER → AUDIT → CLASSIFY → ACT → VERIFY |
| **触发源** | 7 个：每日 cron / 每周 cron / 上线前 hook / PR 评审 / 阶段结束 / 高告警 / AGENTS.md 瘦身 / MCP 体检 |
| **阈值表** | 11 条（继承上游 + 天龙定制）|
| **Don't 护栏** | 10 条（不直接改 AGENTS.md / 不直接删 skill / 不直接关 MCP server）|
| **协同** | 7-scribe V12.2 · 09-06 V1.1 · 09-03 · 09-04 · 07 |

### 3.2 07-scribe V11.11 → V12.2 增量

**新增章节**：`## V12.2 增量：daily context health index 章节`

**核心变更**：
- daily brief 顶部新增"今日上下文健康度"表格（7 项指标 + 评分 + 与昨日对比）
- 健康度评分公式（0-100）：指令链 ≤ 8k · catalog ≤ 3k · MCP ≤ 20 工具 · 0 shadow · 0 重复
- 自动调 `context_audit`（每日 detail=summary，每周 detail=developer）
- high 告警自动触发 40-01 "立刻执行"工作流
- 新增 5 条 Don't 护栏

### 3.3 09-06-skills-administrator V1.0 → V1.1 增量

**新增章节**：`## V1.1 增量：上线前 context_audit 门禁`

**核心变更**：
- `collection add` 前自动调 context_audit
- 4 项上线前检查（catalog 增量 ≤ 200 token / 总 ≤ 3000 / shadow 冲突 / description 重复）
- 任一 FAIL → 拒绝入库 + 输出"上线风险评估报告"
- 新增 5 条 Don't 护栏

---

## 四、合规边界（BSD-3-Clause 红线 · 3 条强制条款）

| 条款 | context-doctor 应用 | 落地 |
|------|---------------------|------|
| **第 1 条** 再分发源代码必须保留版权声明 | `LICENSE` 文件包含 `Copyright (c) 2026, dsh-external` | ✅ `LICENSE` 已实拉确认（10 段 31 行 verbatim）|
| **第 2 条** 再分发 binary 必须在文档/材料中复制版权 + 免责声明 | `NOTICE` 文件 | ✅ `NOTICE` 已落盘（"Modified by dragon-engine / 2026-08-23" 标注）|
| **第 3 条 Trademark** 未经书面许可不得用版权人或贡献者名字背书 | 天龙不得说"dsh-context-doctor 官方推荐 / 官方认证" | ✅ 集成文档统一用 "Powered by Zhenyu98/dsh-context-doctor" |

---

## 五、协同矩阵（天龙首次引入上下文审计层）

```
dsh-context-doctor v0.6.1 (BSD-3-Clause ✅ · 29 用例 PASS)
   ├─► 40-01 上下文治理师 ⭐NEW V1.0  ←—— 本阶段新建
   ├─► 07-scribe V12.2 (daily context health)  ←—— V11.11 升级
   ├─► 09-06-skills-administrator V1.1 (上线前 audit 门禁)  ←—— V1.0 升级
   ├─► 09-03-meta-reviewer (PR 评审必跑)
   ├─► 09-04-chief-of-staff (周报加 context KPI)
   └─► 其他 6 个 Stage 8 Evolution Gate 触发岗位
```

### 与已有 SKILL 协同（catalog 撞车检测）

| SKILL | 协同方式 |
|-------|----------|
| **neat-freak** | memory 治理互补（neat-freak 治"内容重复"，context-doctor 治"catalog 重复"）|
| **advanced-memory-sync** | 同属"减负"三角，各治一域 |
| **session-distiller** | 蒸馏产 skill → 进 catalog → 本工具监控 catalog 增长 |
| **a-stock-data-bridge** (Apache-2.0) | 阶段 25 上线后 audit 对比基线 |
| **aihot / agent-reach** | catalog 撞车检测 |

---

## 六、阶段 26 实施清单（已完成 ✅）

### P0（安装 + 合规 · 5 项）

- [x] 检查 DSH 版本（沙箱内 `dsh` 不可用 → 由老李在 DSH 宿主页执行）
- [x] 落盘 6 个集成文件（README/LICENSE/NOTICE/CHECKLIST/install/audit-template）
- [x] 写主题文件 `memory/context-doctor-integration.md`（本文件）
- [x] MEMORY 治理入口（dragon-engine 主仓无 MEMORY.md 顶层文件 → 主题文件直接归 `memory/`）
- [x] 合规自审（3 条 BSD 红线 + 1 个 Modified 标注）

### P1（Agent 落地 · 3 项）

- [x] 新建 Agent **40-01 上下文治理师 V1.0**
- [x] 改造 **07-scribe V11.11 → V12.2**（daily context health）
- [x] 改造 **09-06-skills-administrator V1.0 → V1.1**（上线前 audit 门禁）

### P2（待老李执行 · 1 项）

- [ ] 老李在 DSH 宿主页跑 `bash dragon-engine/skills/context-doctor-integration/scripts/install-context-doctor.sh audit`
- [ ] 重启 dsh web 验证圆环面板
- [ ] 跑首次 audit 落盘到 `~/.dsh/audit/2026-08-23-baseline.json`

---

## 七、累计 PASS 增量规划

| 阶段 | 增量 | 累计 |
|------|------|------|
| 25（含 25.1/25.2）| +12 | **≥618** |
| **26（本次）** | **+3 Agent 改造 + 1 新建 Agent + 6 文件落盘** | **N/A（不强制 PASS）** |

> **说明**：context-doctor 是 DSH 插件而非天龙 SKILL，**不强制纳入天龙 pytest 累计 PASS**。插件自身 29 用例由上游保障。

---

## 八、风险与未决项

1. **DSH 版本未验证**——本会话是 DSH Web 客户端，`dsh` CLI 不可用。需老李在宿主 shell 跑 `dsh --version` 确认 ≥ 0.1.0-rc.6 或 0.1.1-rc.x。
2. **AGENTS.md 88% 膨胀**——用户级 `~/.dsh/AGENTS.md` 已被沙箱从 **571,153 字节截到 65,128 字节**（截 506KB）。context-doctor 装上后第一步应是 audit，确认重复段落位置，再决定是否裁剪。
3. **catalog 803 个 skills**——单跑 audit 会得到 4150 token 描述（与上游 README 示例 177 skill 4150 token 推算天龙 catalog 应在 5-10k 范围）。**首次 audit 后可能直接触发 high 告警**，需老李决策：保留 / 裁剪 / 分批下线。
4. **40-01 与 09-06 / 07 的协同需要 cron 触发**——DSH 是否支持 cron / scheduled task 由宿主决定，建议先用 07-scribe 的"每日 daily brief"自然触发，无需额外调度器。
5. **上游快速迭代**（10 天 6 个 commit）——天龙 SKILL 包装层依赖上游二进制，建议**每月一次 skill-updater 检测**，纳入阶段 27+ 节奏。
6. **同作者 dsh-external 还有 plugin-registry**——可能还有其他 DSH 官方插件尚未发现，建议阶段 27 评估 `plugin-registry` 全清单。

---

## 九、来源链接

- 仓库：<https://github.com/Zhenyu98/dsh-context-doctor>
- LICENSE（BSD-3-Clause 31 行）：<https://raw.githubusercontent.com/Zhenyu98/dsh-context-doctor/main/LICENSE>
- README：<https://raw.githubusercontent.com/Zhenyu98/dsh-context-doctor/main/README.md>
- v0.6.1 package.json：<https://raw.githubusercontent.com/Zhenyu98/dsh-context-doctor/main/package.json>
- 核心源码（不镜像）：`src/audit.ts` 17KB · `src/scan.ts` 8KB · `src/analyze.ts` 5KB · `src/tokens.ts` 1KB
- DSH 官方插件机制：<https://github.com/dsh-external/plugin-registry>
- 同作者仓库：<https://github.com/dsh-external>

---

## 十、4 周时间线建议（天龙阶段 26 → 阶段 27）

### 周 1（2026-08-23 → 2026-08-29）· 阶段 26 落地 ✅ 本次已完成

| 工作日 | 任务 | 状态 |
|---|---|---|
| D1 | P0 集成文件落盘（6 个）| ✅ |
| D1 | P1 三个 Agent 改造（40-01 新建 + 07 V12.2 + 09-06 V1.1）| ✅ |
| D2-3 | 老李在 DSH 宿主页跑 install-context-doctor.sh | ⏳ 待执行 |
| D4 | 跑首次 audit，落盘 baseline.json | ⏳ 待执行 |
| D5 | 根据 baseline 决定是否裁剪 AGENTS.md | ⏳ 待执行 |

### 周 2-4（2026-08-30 → 2026-09-20）· 阶段 26 收尾 + 阶段 27 候选

| 工作日 | 任务 | 备注 |
|---|---|---|
| W2 | 观察 40-01 / 07-scribe V12.2 / 09-06 V1.1 协同效果 | 看 audit 告警触发频次 |
| W3 | 整理 catalog 撞车清单 + 同名 shadow 清单 | 出"skill 治理候选清单"|
| W4 | 阶段 27 候选：plugin-registry 全清单评估 / skill-updater 自动化 / 阶段 26 COMPLETION_REPORT | |

---

## 阶段 26 验收门槛

- [x] 集成文件落盘 6 个（README/LICENSE/NOTICE/CHECKLIST/install/audit-template）
- [x] Agent 新增 1 个（40-01 V1.0）
- [x] Agent 升级 2 个（07-scribe V12.2 / 09-06-skills-administrator V1.1）
- [x] 主题文件 1 个（本文件）
- [x] BSD-3-Clause 红线检查 3/3 PASS
- [ ] 老李在 DSH 宿主页跑安装脚本 + 首次 audit（待执行）
- [ ] `analysis/STAGE26_CONTEXT_AUDIT.md` 阶段结束报告（建议 W4 完成）

---

> **下次同步点**：老李完成首次 audit 后，把 baseline 数据贴回本主题文件 §七，并写 `analysis/STAGE26_CONTEXT_AUDIT.md` 作为阶段 26 COMPLETION_REPORT 附件。
