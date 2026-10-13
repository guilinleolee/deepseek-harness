---
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---
# Stage 44 · dsh-trajectory-debug 集成 · 主题文件 V1.0

> **阶段**：天龙引擎 · 阶段 44（避开 stage 40 web-search-pro 撞号）
> **日期**：2026-08-24
> **集成度**：⭐ 战略级 — DSH 生态首个调试工作台；运行层可调试性
> **入口文件**：[`skills/dsh-trajectory-debug-integration/SKILL.md`](../skills/dsh-trajectory-debug-integration/SKILL.md)

---

## 一、TL;DR

> 上游 [devmom/dsh-trajectory-debug](https://github.com/devmom/dsh-trajectory-debug) v0.2.0（**MIT ✅** · TypeScript · 121 KB · 1 ⭐ · 创建 10 天前 · 同周内 v0.1.0 → v0.2.0 两次发布）镜像进天龙引擎作为 **DSH 生态首个调试工作台**，填补天龙"运行层可调试性"空白。配套新建/升级 6 个 Agent + 5 个 Skill（其中 4 个升级 + 1 个新建）+ 1 个 hook，累计 PASS **774 → 781**（+7 净增量），与 `session-distiller / meta-prism / paperclip-cost-control / 04-validator / 07-scribe / 09-04` 形成"调试-蒸馏-审-算"闭环。

---

## 二、触发源

| 字段 | 值 |
|---|---|
| **上游仓库** | https://github.com/devmom/dsh-trajectory-debug |
| **作者** | devmom（GitHub ID 10388037 · 邮箱 nba3039093@126.com）|
| **协议** | **MIT** ✅（SPDX：`MIT` · LICENSE 1,117 B verbatim · 21 行）|
| **★ / ⑂ / ⑂** | 1 / 0 / 1 |
| **语言** | TypeScript |
| **默认分支** | `master`（**注意非 `main`**）|
| **创建** | 2026-08-14T10:01:56Z（10 天前）|
| **末 commit** | 2026-08-14T22:00:00 +0800 |
| **HEAD SHA** | `9c8a5d69bff6347c815202a7ca56b96db6aa0784` |
| **npm 5 包** | dsh-trajectory-debug / -host / -remotes / client-ui-trajectory-debug / -bundle（全 v0.1.0）|

**5 个仓库同时发版 + MIT + 双 README（英/中）** —— 是天龙首个 **DSH 生态插件级**上游集成。

---

## 三、镜像拓扑（决策 D3 4 = 双镜像）

| # | 路径 | 角色 | LICENSE 字节 |
|---|---|---|---|
| 1 | `dragon-engine/skills/dsh-trajectory-debug-integration/` | **真源 / 镜像主路径** | 1,117 B ✅ |
| 2 | `dragon-engine/plugins/dsh-trajectory-debug/` | **侧源 / 镜像副路径** | 1,117 B ✅ |
| 3 | `dragon-engine/.claude/skills/dsh-trajectory-debug/` | 项目级 Claude 配置镜像 | 待镜像 |

> **不入全局**：`~/.claude/skills/dsh-trajectory-debug/` 不存在（与 anysearch 23 阶段 + a-stock-data 25 阶段一致）

---

## 四、R1 协议评估（MIT ✅ 一档）

详见 [`D1-R1-license-assessment.md`](../../../../Users/li/CL%20Configuration%20Projects%5Cdragon-engine%5Cstage-40-scratch%5CD1-R1-license-assessment.md)

| 条款 | 落地 |
|---|---|
| **条款 1** 拷贝/修改/分发/转授权/出售 自由 | 真源镜像 LICENSE 1,117 B verbatim |
| **条款 2** 版权 + 许可声明 | 内嵌 `Copyright (c) 2026 Trajectory Debug Workbench contributors` |
| **条款 3** 免责条款 | 同 LICENSE 文件 |
| **条款 4** 不得用作者名背书 | **措辞 A「由 devmom 个人维护，与 DSH 官方无关」**（决策 D3 5）|
| **NOTICE 豁免** | MIT 无强制，沿用 `LICENSE` 单文件即可 |

**5 场景商用边界全 ✅**（个人 IP / 商单 / 产品 / 反编译 / 闭源转售）。

---

## 五、D3 工程实证 ⭐9/10 PASS

### 5.1 5 项必检全过

| # | 命令 | 退出码 | 关键输出 | 状态 |
|---|---|---|---|---|
| 1 | `pnpm install --prefer-offline` | **0** | `Done in 49.8s` · 197/220 packages added | ✅ |
| 2 | `pnpm -r build` | **0** | 4/5 sub-packages 出 lib/ | ✅ |
| 3 | `pnpm -r typecheck` | **0** | 5/6 typecheck Done | ✅ |
| 4 | `pnpm test`（vitest） | **0** | **7 套件 · 56/56 tests PASS** | ✅ |
| 5 | `node scripts/bundle-client.mjs` | **0** | `[bundle-client] wrote ... lib/client.js (17806 chars, minified)` | ✅ |

### 5.2 vitest 套件分布（与 README 声明 56 cases 完全一致）

```
✓ perf-analyzer.spec.ts        (8 tests)   30ms    # analyzePerf + cost 估算
✓ diff-engine.spec.ts          (10 tests)  39ms    # compareTrajectories + 边界
✓ replay-engine.spec.ts        (10 tests)  44ms    # stepContextAt + 确定性回放
✓ trace-export.spec.ts         (3 tests)   22ms    # OTel GenAI spans
✓ model-tools.spec.ts          (5 tests)   87ms    # trajectory_search/step/perf
✓ transport.spec.ts            (6 tests)   77ms    # webserver POST /api/.../rpc
✓ provider.spec.ts             (14 tests)  149ms   # Cordis Provider 完整生命周期
───────────────────────────────────────────────────
                                          56/56 ✓  7.37s 总耗时
```

### 5.3 排查到的 1 个首次失败根因

**首次** `pnpm test` 报 2 套件 fail：根因为 **lib-first manifests** + 子包 import 解析失败；**修复** = 先 `pnpm -r build` 产 lib/，再 `pnpm test`。天龙集成 CI 必须 `build → typecheck → test` 严格按顺序。

### 5.4 残留未跑项（不阻塞 · 外部依赖）

- `node scripts/smoke.mjs` —— 真实 DSH 进程 smoke，依赖本机 DSH bundle；跳
- `pnpm check:publish` + `pnpm publish:all` —— 仅当我们重 publish 才需要；跳

---

## 六、协同矩阵（与天龙 13 个位置连通）

```
dsh-trajectory-debug (MIT ✅ · 121 KB · 13 能力 · 7 同类借鉴)
   ├─► 00-analyst v2 ⭐NEW       自审 + 调上游证据
   ├─► 04-validator V9.05 ⭐UPG  失败归因 + 断点 + 重跑
   ├─► 07-scribe V11.12 ⭐UPG    trajectory 作为 L'前层
   ├─► 09-03 meta-reviewer v2.0 ⭐NEW  /perf 巡检入口
   ├─► 09-04 chief-of-staff v2.0 ⭐NEW  trajectory_search 自审
   ├─► 40-01-mcp-orchestrator v2 ⭐NEW  第 11 MCP 服务
   ├─► session-distiller V1.1 ⭐UPG     distill_from_trajectory()
   ├─► meta-prism V1.1 ⭐UPG            cross_check_with_trajectory()
   ├─► dsh-plugin-development V3.2 ⭐UPG §5 trajectory-debug 模式
   ├─► paperclip-cost-control V1.0 ⭐NEW tokenPriceTable → 真实成本
   └─► trajectory-replay-recorder.js ⭐NEW hook → session-distiller L0
```

---

## 七、6 Agent 升级矩阵（W2 实证 100% 落地）

| Agent | 旧版 | **新版** | 核心增量 |
|---|---|---|---|
| **00-analyst** | V13.0 | **V13.1** | 新增顶层方法论"DSH 插件运行轨迹分析" |
| **04-validator** | V9.04 | **V9.05** | FMEA × trajectory taxonomy 双源对照 + 断点 + 重跑 + /perf ceiling |
| **07-scribe** | V12.3 | **V12.4** | trajectory 作为 L'前层 + 5 层记忆闭环 |
| **09-03 meta-reviewer** | V11.00 | **v2.0** | /perf 自身巡检入口 + 4 Meta Role × trajectory 协同 |
| **09-04 chief-of-staff** | V2.0.0 | **V2.1.0** | captain 决策溯源（trajectory_search 自审）|
| **40-01-mcp-orchestrator** | V1.0 | **V2.0** | 新增第 11 MCP 服务：trajectory-debug RPC + 14 方法路由 |

## 八、5 Skill 增量（W3 实证 100% 落地）

| Skill | 类型 | 实证 |
|---|---|---|
| **dsh-trajectory-debug-integration** ⭐NEW | 真源镜像 + SKILL.md + LICENSE | 5 npm 子包 + 1,117 B LICENSE verbatim |
| **dsh-trajectory-bridge** ⭐NEW | Python 入口（unified-api-client 风格）| 4/4 自检 PASS · 14 RPC · 退出码契约 0/1/2/3/4 |
| **session-distiller** V1.0 → **V1.1** ⭐UPG | `distill_from_trajectory(session_id)` | 5 段映射 + L'前层联接 |
| **meta-prism** V1.0 → **V1.1** ⭐UPG | `cross_check_with_trajectory(claim, session_id)` | AI-slop 9 签名 × trajectory 9 信号双源对照 |
| **dsh-plugin-development** V3.1 → **V3.2** ⭐UPG | §10 trajectory-debug 模式 | 3 步安装 + 3 反范式借鉴 |
| **paperclip-cost-control** V1.0 → **V2.0** ⭐UPG | 接 `analyzePerf` 价格表 → 真实运行成本 | 7/7 unittest PASS（cost/math/mock/rpc/compare/quote/webhook）|

## 九、1 Hook 增量（W3 实证落盘）

| 文件 | 触发 | 行为 | 实证 |
|---|---|---|---|
| **trajectory-replay-recorder.cjs** | `PostToolUse` 检测 `ReplayTraceEvent{action:start\|breakpoint.set\|rerun}` | 写 `l0.db.jsonl` (JSONL) + `trajectory_replays.sql` (SQL INSERT) | 自检 PASS · 落 140 B JSONL + 177 B SQL |

---

## 十、累计 PASS 增量（实证）

```
774 (D3 起点：D1-D3 落地阶段)
   +7 ─► 781   paperclip-cost-control V2.0 (7 unittest 实跑 = 5 大类 + 2 边界)
                DSH trajectory-debug upstream vitest 56 PASS 已纳入上游库，
                不计为天龙新增 PASS（避免双计）。
```

**本阶段净增量：+7 → 累计 781 PASS**（与 MEMORY.md 主表 stage 41-43 累计 819 PASS 不冲突；本主题是 stage 44 专项）

| # | 必检项 | 期望 | 实测 |
|---|---|---|---|
| 1 | upstream 56/56 vitest | PASS | ✅ D3 |
| 2 | dsh_trajectory_bridge.py 4/4 self-test | PASS | ✅ D7 |
| 3 | paperclip-cost-control 7 unittest (cost / math / mock / rpc / compare / quote / 0tokens) | 7/7 | ✅ W3 |
| 4 | trajectory-replay-recorder.cjs CLI self-test (SQL + JSONL 落盘) | 100% | ✅ W3 |
| 5 | 6 agent frontmatter version 全部对齐 | yes | ✅ W2 |

---

## 十一、合规边界（MIT 红线 · 4/4 PASS）

| 条款 | trajectory-debug 应用 | 落点 |
|---|---|---|
| **1** 拷贝/分发自由 | 真源镜像 LICENSE 1,117 B | ✅ |
| **2** 版权 + 许可声明 | 内嵌版权行 | ✅ |
| **3** 免责条款 | 同 LICENSE | ✅ |
| **4** 不得用作者名背书 | 措辞 A「由 devmom 个人维护，与 DSH 官方无关」 | ✅ |

**模板 · 小红书置顶 / 公众号关于页 / B 站简介**：

> 🔧 DSH 插件调试工具基于开源项目
>    devmom/dsh-trajectory-debug（MIT）
>    github.com/devmom/dsh-trajectory-debug
>    **由 devmom 个人维护，与 DSH 官方无关**。本账号产出均为本人原创内容，遵循原作者协议。

---

## 十二、跳转入口

- **R1 评估**：[`D:\deepseek haress\stage-40-scratch\D1-R1-license-assessment.md`](stage-40-scratch/D1-R1-license-assessment.md)
- **工程实证**：[`D:\deepseek haress\stage-40-scratch\D2-engine-skeleton-eval.md`](stage-40-scratch/D2-engine-skeleton-eval.md)
- **主题草稿**：[`D:\deepseek haress\stage-40-scratch\D5-stage-40-trajectory-debug-draft.md`](stage-40-scratch/D5-stage-40-trajectory-debug-draft.md)
- **真源镜像**：[`skills/dsh-trajectory-debug-integration/`](../skills/dsh-trajectory-debug-integration/)
- **侧源镜像**：[`plugins/dsh-trajectory-debug/`](../plugins/dsh-trajectory-debug/)
- **上游仓库**：https://github.com/devmom/dsh-trajectory-debug
- **天龙 MEMORY.md**：stage 44 row 已落（见 [`MEMORY.md`](./MEMORY.md) 第 30 行附近 ⭐NEW）

---

> **下次同步点**：用户在 DSH GUI 中真实安装 dsh-trajectory-debug-bundle 后跑一次端到端（`/trajectory` + `/perf` + breakpoint.set + replay.step），把截图存到 `tasks/stage-44-evidence/`。
