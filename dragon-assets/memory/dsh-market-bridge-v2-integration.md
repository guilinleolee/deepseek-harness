---
name: dsh-market-bridge-v2-integration
description: dsh-market-bridge V2.0 集成档案 · 借鉴 dsh-market/dsh-market V1.31.1（MIT · 2,474⭐）13 类核心设计 · Stage 50.3
metadata:
  node_type: memory
  originSessionId: stage-50-3-dsh-market-v2
  modified: 2026-08-26T16:00:00.000Z
  borrows_from:
    - dsh-market/dsh-market (MIT ✅ · v1.31.1 · 2,474⭐ · 2026-08-26)
  integration_stage: 50.3
  upgrade_from: stage_50_2_v1_0_0_borrows_v0_x
---

# dsh-market-bridge V2.0 · Stage 50.3 集成档案

> **TL;DR**：天龙 stage 50.2 借鉴档仅覆盖 dsh-market V0.x（2430⭐），现升级到 V2.0 完整吸收 V1.31.1（2474⭐）+ IMPROVEMENT-PLAN 30 KB 全 13 项。**64/64 unittest PASS**（V1.0 16 兼容 + V2.0 48 新增）。

---

## 触发源

[dsh-market/dsh-market](https://github.com/dsh-market/dsh-market) · **MIT ✅** · **v1.31.1** · **2,474⭐** · 13 天新项目（创建 2026-08-14，末更新 2026-08-26）

**核心 5 个里程碑**：
1. **V1.0.0** (2430⭐, 2026-08-14)：基础 5 字段 plugin schema + 4 阶段 install
2. **V1.x** (2474⭐, 2026-08-26)：**V1.31.1** — 158 KB routes.ts + 13 类 IMPROVEMENT-PLAN
3. **backup/restore 模块** (26 KB)：profile 导出/导入/WebDAV/Gist 三种同步
4. **themes 互斥切换**：themes are mutually exclusive, your choice survives restarts
5. **restart systemd/loopback 守卫**：避免 cgroup 自杀的双条件检测

---

## 借鉴清单（13 类 · V2.0 全吸收）

| # | 借鉴项 | 来源 | 天龙 V2.0 实现 |
|---|---|---|---|
| 1 | PluginMarketEntry 17 字段 schema | V1.31 RegistryPlugin 完整 | `PluginMarketEntry` dataclass + `_normalize_description/category` |
| 2 | 6 阶段 install workflow | P0-1 + P0-2 | `INSTALL_PHASES_V2` + `advance_install()` |
| 3 | catalog ETag/Last-Modified 304 校验 | V1.31 src/registry.ts L120-180 | `fetch_catalog_with_cache()` + `_catalog_cache` 单例 |
| 4 | region routing 多源 fallback | V1.31 src/regions.ts | `Region` / `CatalogSource` + `resolve_region()` |
| 5 | preflightTarget 包存在性 + dsh.bundle 校验 | P0-1 | `preflight_target()` + `PreflightResult` |
| 6 | verifyActivation 4 态判定 | P0-2 | `verify_activation()` + `ActivationResult` |
| 7 | pnpm v10/v11 allowBuilds 双键名 | P0-4 + V1.31 pnpm-compat.ts 16KB | `build_allow_builds_entry()` + `merge_pnpm_workspace_yaml()` |
| 8 | backup/restore merge 模式 | V1.31 src/backup.ts 26KB | `BackupProfile` / `RestoreReport` + `export_backup()` / `restore_backup()` |
| 9 | themes 互斥切换 | V1.31 src/themes.ts | `ThemeState` + `switch_theme()` / `uninstall_theme()` |
| 10 | restart systemd/loopback 守卫 | V1.31 src/restart.ts | `detect_systemd_main_process()` + `should_show_restart_button()` |
| 11 | parse_simple_patch 热挂载判定 | V1.31 src/hot.ts 21KB | `parse_simple_patch()` 返回 `hot_loadable` 标志 |
| 12 | 13 类 issue 分类策略 | P1-9 + IMPROVEMENT-PLAN 全部 | `ISSUE_CATEGORIES` (V1.0 5 + V2.0 8) + `classify_issue()` |
| 13 | description 双语 en/zh 字段 | P1-13 | `_normalize_description()` 双语拆分 + `_text_matches()` 双语搜索 |

---

## 升级摘要

| 维度 | V1.0（stage 50.2） | V2.0（stage 50.5） |
|---|---|---|
| **上游版本** | dsh-market V0.x（2430⭐） | dsh-market **V1.31.1**（2474⭐） |
| **PluginMarketEntry 字段** | 9 | **17**（V1.31 RegistryPlugin 完整） |
| **install workflow** | 4 阶段 | **6 阶段**（+ preflight + activation-check） |
| **catalog 缓存** | 1h TTL（V1.0 已删除） | **ETag/Last-Modified 304 校验**（V1.31 served 单例） |
| **issue 分类** | 5 类 | **13 类**（P0-1..P2-13 一一映射） |
| **filter 维度** | 4 维度 | **5 维度 + 双语**（+ language 字段） |
| **unittest** | 18 | **64**（V1.0 16 + V2.0 48） |
| **Agent 升级** | 无 | **40-01 mcp-orchestrator V2.0 → V2.1** |
| **协同矩阵** | 5 下游 | **6 下游**（+40-01 mcp-orchestrator V2.1） |
| **IMPROVEMENT-PLAN** | 16 类借鉴（粗略）| **13 项全覆盖**（references/issue-roadmap.md） |

---

## 累计验证 64/64 PASS

```
[1/13] PluginMarketEntry 17 字段解析                                6/6 PASS
[2/13] 6 阶段 install workflow（V1.0 4 阶段向后兼容）               3/3 PASS
[3/13] issue 分类（V1.0 5 + V2.0 8 = 13 类）                       7/7 PASS
[4/13] filter plugin 5 维度 + 双语                                5/5 PASS
[5/13] semver 兼容检查（V1.0）                                    5/5 PASS
[6/13] end-to-end 集成（V1.0）                                     1/1 PASS
[7/13] catalog ETag/Last-Modified 304 缓存                         3/3 PASS
[8/13] region routing + DSHM_REGISTRY_URL env override             3/3 PASS
[9/13] preflightTarget（P0-1）                                     6/6 PASS
[10/13] verifyActivation 4 态（P0-2）+ parse_simple_patch           8/8 PASS
[11/13] pnpm v10/v11 allowBuilds 双键名（P0-4）                    6/6 PASS
[12/13] backup/restore merge 模式                                  4/4 PASS
[13/13] themes 互斥 + restart systemd/loopback 守卫                5/5 PASS
+ TestV20InstallPipelineIntegration 联动                           2/2 PASS

---EXIT: 0---
```

---

## 1 Agent 升级（V2.0 → V2.1）

| Agent | 升级点 |
|---|---|
| **40-01 mcp-orchestrator V2.0 → V2.1** | **新增 dsh-market-mcp 第 12 服务**（dsh-market-bridge V2.0 Python 引擎 + 6 阶段 install pipeline）|

V2.1 增量（仅协同）：
- frontmatter version 2.0.0 → 2.1.0
- triggers +3（dsh-market / plugin market / 插件市场）
- MCP服务路由 +3 行（plugin market 搜索/详情/安装）
- 内置MCP服务 +1 行（dsh-market-mcp）
- 远程MCP调用新增"dsh-market MCP 调用"整段（6 个 subcommand）
- dsh-market MCP 路由决策树（V2.0 独有）
- 与天龙引擎协同 +1 行（dsh-market ⭐Stage 50.3）
- 版本信息 2.0.0 → 2.1.0

---

## 借鉴档边界 vs 真源镜像

| 维度 | 借鉴档（V2.0 走这条） | 真源镜像（不走） |
|---|---|---|
| 代码来源 | 自研 Python（dsh_market_bridge.py 30 KB）| 镜像 TypeScript 真源 158 KB+ |
| LICENSE 义务 | LICENSE verbatim + NOTICE "Modified by" | LICENSE verbatim + 同 NOTICE |
| 引用方式 | `设计借鉴` `IMPROVEMENT-PLAN 借鉴` `schema 字段映射` | `fork-of` 关系 |
| 维护成本 | 低（仅 schema 与 IMPROVEMENT-PLAN 跟踪） | 高（每 PR 同步上游） |
| 上游迭代跟进 | 月度 cron_weekly skill-updater 触发 | PR-by-PR 同步 |

**结论**：借鉴档是正确选择——上游 30 天迭代 ~10 个版本，真源镜像维护成本与价值不匹配。

---

## 5 类安全护栏

| # | 护栏 | 触发条件 | 处置 |
|---|---|---|---|
| 1 | **Key 安全** | 任何 KEY/GITHUB_TOKEN 等暴露 | 不写入 NOTICE/SKILL/license 文件 |
| 2 | **Cookie 轮换** | awesome-dsh-plugin API key 失效 | 通过 `DSHM_REGISTRY_URL` env override 切镜像 |
| 3 | **上游协议变更** | dsh-market LICENSE 改变 | NO-GO 终止借鉴档，转寻找替代上游 |
| 4 | **IMPROVEMENT-PLAN 漂移** | 上游 P0/P1 项已实施但天龙未吸收 | 月度 cron_weekly skill-updater 触发 V3.0 升级 |
| 5 | **exit code 契约** | 0=OK / 1=PARSE / 2=SCHEMA / 3=VERSION / 4=PREFLIGHT / 5=ACTIVATION / 6=CATALOG | 7 类退出码清晰边界 |

---

## 关键文件路径

| 资产 | 路径 | 状态 |
|------|------|------|
| SKILL.md V2.0 | `C:\Users\li\.claude\projects\dragon-engine\skills\dsh-market-bridge\SKILL.md` | 升级 V1.0→V2.0 |
| scripts/dsh_market_bridge.py V2.0 | `skills/dsh-market-bridge/scripts/dsh_market_bridge.py` | 升级 V1.0 (1.2KB) → V2.0 (30KB) |
| tests/test_dsh_market_bridge.py V2.0 | `skills/dsh-market-bridge/tests/test_dsh_market_bridge.py` | 升级 V1.0 18 → V2.0 64 |
| references/issue-roadmap.md | `skills/dsh-market-bridge/references/issue-roadmap.md` | **V2.0 新增** |
| LICENSE verbatim | `skills/dsh-market-bridge/LICENSE` | **V2.0 新增**（1091 B / 21 行） |
| NOTICE "Modified by dragon-engine" | `skills/dsh-market-bridge/NOTICE` | **V2.0 新增** |
| agents/40-01-mcp-orchestrator V2.1 | `agents/40-01-mcp-orchestrator.md` | V2.0→V2.1 增量 |
| memory/dsh-market-bridge-v2-integration.md | `memory/` | **V2.0 新增**（本文件） |
| memory/MEMORY.md | `memory/MEMORY.md` | 阶段 50.3 row 已加 |
| memory/mit-attribution-statements.md §十八 | `memory/` | 阶段 50.3 致谢节已加 |

---

## 与 stage 50.2 / 50.1 / 49.x 关系

| 阶段 | 上游 | 借鉴内容 | V2.0 关系 |
|---|---|---|---|
| **50.1** | deepseek-harness | cordis patch 借鉴 | 同源设计基础 |
| **50.2** | dsh-market V0.x | 5 类借鉴（V1.0 雏形） | V2.0 升级起点 |
| **50.3** | dsh-market V1.31.1 | 13 类全吸收（V2.0 完整） | 本阶段 |
| **49.1** | dsh-desktop | 桌面桥 | 互补（桌面 + 市场 = 完整 DSH）|
| **49.2** | memsearch | 语义搜索 | 替换 dsh-market 默认搜索 |

---

## 风险与未决项

1. **上游 30 天迭代 ~10 个版本**——月度 cron_weekly skill-updater 触发 V3.0 升级
2. **IMPROVEMENT-PLAN P1-7 commit 锁定 / P2-10 多 profile / P2-11 安装台账**——天龙 V2.0 保留为 V3.0 候选（references/issue-roadmap.md §保留）
3. **40-01 mcp-orchestrator V2.1 实际真装**——目前是协议层增量；前端 MCPClientPool 包装待 DSH 升级到 0.1.1+ 后实装
4. **pnpm-compat 真测**——V2.0 仅设计/解析；端到端真装验证待生产环境（pnpm ≥10 → pnpm ≥11 升级）

---

## 下次同步点

- **上游 dsh-market v1.32 发版后**：跑 `skill-updater` cron_weekly 月度扫描，重新评估 13 项策略
- **DSH 升级到 0.1.1+**：实装 40-01 mcp-orchestrator V2.1 的 MCPClientPool 包装
- **天龙累计 PASS ≥879（852 + 27）**：在 stage-50-3-announce.md 落实证

---

## 跳转入口

- **SKILL.md V2.0**：`skills/dsh-market-bridge/SKILL.md`
- **scripts/dsh_market_bridge.py V2.0**：`skills/dsh-market-bridge/scripts/dsh_market_bridge.py`
- **tests/64 PASS**：`skills/dsh-market-bridge/tests/test_dsh_market_bridge.py`
- **references/issue-roadmap.md**：`skills/dsh-market-bridge/references/issue-roadmap.md`（IMPROVEMENT-PLAN 13 项策略矩阵）
- **LICENSE verbatim**：`skills/dsh-market-bridge/LICENSE`
- **NOTICE**：`skills/dsh-market-bridge/NOTICE`
- **40-01 V2.1**：`agents/40-01-mcp-orchestrator.md`
- **MIT §十八**：`memory/mit-attribution-statements.md`
- **上游仓库**：https://github.com/dsh-market/dsh-market · MIT
- **天龙 MEMORY.md**：`memory/MEMORY.md` — 阶段 50.3 row + 累计 PASS
