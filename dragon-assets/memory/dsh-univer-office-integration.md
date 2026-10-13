---
name: dsh-univer-office-integration
description: dsh-univer-office v0.2.9 (Apache-2.0) 集成档案 — DSH 一等公民 plugin · 5 种 Unit + 13 个 DSH 工具 + 浏览器预览 + worktree 隔离 · 阶段 47 累计 PASS +8
metadata:
  node_type: memory
  type: integration
  originSessionId: dsh-univer-office-stage47
  modified: 2026-08-26T10:30:00.000Z
---

# dsh-univer-office 集成档案 V1.0（阶段 47 / 47.0）

> **TL;DR**：上游 [dream-num/dsh-univer-office](https://github.com/dream-num/dsh-univer-office) v0.2.9（Apache-2.0 ✅ · DreamNum/Univer 母公司出品 · 2026-08-15 创建 · 2026-08-25 末 push）是 DSH **一等公民 plugin**，**不是普通 skill**。通过 `dsh plugin add dsh-univer-office` 安装到 DSH web GUI 内，带 5 种 Office Unit（Sheet/Doc/Slide/Base/Board）+ 13 个 `univer_*` DSH 工具 + 浏览器实时预览 + worktree 隔离多轮修订 + 内置 lint + SVG 资源库 + 截图自检。天龙镜像 7 个 SKILL.md + Apache-2.0 LICENSE/NOTICE；新建 `28-11-univer-workbench-operator` 路由层；改造 3 个高 ROI Agent（28-data-analyst / 17-data-analyst / 89-financial-analyst → V11.0）。累计 PASS **866 → 874（+8）**。
>
> **Stage 编号说明**：天龙历史 stage 26 = aihot/neat-freak/tickflow（占位）· 本集成使用 **stage 47 dsh-univer-office**（顺位不撞号）。

---

## 一、实跑元数据（2026-08-26 实拉）

| 字段 | 值 | 来源 |
|---|---|---|
| 上游仓库 | https://github.com/dream-num/dsh-univer-office | gh API |
| 作者 | DreamNum Co., Ltd. <developer@univer.ai> | package.json |
| license.spdx_id | **Apache-2.0** ✅ | LICENSE 全文验证 |
| 当前版本 | **v0.2.9** | package.json |
| 创建日期 | 2026-08-15 | gh API created_at |
| 末 push | 2026-08-25（昨天） | gh API pushed_at |
| Node 要求 | `>=22.19.0` · pnpm 11.23 | package.json engines |
| 默认 Gateway 端口 | 9080（占用逐次+1） | README §Configuration |
| 默认 timeout | read 3s · mutation 60s · import/export 120s · screenshot 120s | README §Configuration |
| 屏幕渲染依赖 | 本地 Chrome/Chromium（`UNIVER_RENDER_BROWSER`） | README §Requirements |
| **5 种 Unit** | Sheet / Doc / Slide / Base / Board | README + SKILL.md |
| **13 个 DSH 工具** | univer_new/status/worktree/unit/import/inspect/execute/export/lint/compile_svg/screenshot/api/resources | README §Built-in tools |
| 上游 SKILL.md 数 | **7 个** + 1 主 = 8 个 | GitHub `skills/` |
| **DSH peer deps** | `@deepseek-ai/cordis@^4.0.1` + `@deepseek-ai/dsh-*@0.1.0-rc.8` | package.json peerDependencies |

---

## 二、镜像拓扑（阶段 26 实装）

| # | 路径 | 角色 | 状态 |
|---|---|---|---|
| 1 | `dragon-engine/skills/univer/SKILL.md` | 上游主 skill 镜像 | ✅ 已落 |
| 2 | `dragon-engine/skills/univer-sheet/SKILL.md` | Sheet Unit 镜像 | ✅ 已落 |
| 3 | `dragon-engine/skills/univer-doc/SKILL.md` | Doc Unit 镜像 | ✅ 已落 |
| 4 | `dragon-engine/skills/univer-slide/SKILL.md` | Slide Unit 镜像 | ✅ 已落 |
| 5 | `dragon-engine/skills/univer-base/SKILL.md` | Base Unit 镜像 | ✅ 已落 |
| 6 | `dragon-engine/skills/univer-board/SKILL.md` | Board Unit 镜像 | ✅ 已落 |
| 7 | `dragon-engine/skills/univer-embed/SKILL.md` | Embed Unit 镜像 | ✅ 已落 |
| 8 | `dragon-engine/skills/univer-cross-unit-formula/SKILL.md` | 跨 Unit 公式镜像 | ✅ 已落 |
| 9 | `dragon-engine/skills/dsh-univer-office-bridge/SKILL.md` | **天龙本地化包装层**（新增） | ✅ 已落 |
| 10 | `dragon-engine/skills/dsh-univer-office-bridge/LICENSE` | **Apache-2.0 完整版 + Mirror Provenance** | ✅ 已落 |
| 11 | `dragon-engine/skills/dsh-univer-office-bridge/NOTICE` | **Apache-2.0 NOTICE 含 Modified by dragon-engine / 2026-08-26** | ✅ 已落 |
| 12 | `dragon-engine/skills/dsh-univer-office-bridge/scripts/check.py` | 5 PASS 健康检查 | ✅ 已跑（5/5 PASS） |
| 13 | `dragon-engine/skills/dsh-univer-office-bridge/tests/test_*.py` | 5 个 unittest | ✅ 已跑（5/5 PASS） |
| 14 | `dragon-engine/skills/dsh-univer-office-bridge/references/triggers.md` | 130 个触发词 + 5 类 Unit 路由 | ✅ 已落 |
| 15 | `dragon-engine/agents/28-11-univer-workbench-operator.md` | **新建岗位 V1.0** | ✅ 已落 |
| 16 | `dragon-engine/agents/28-data-analyst.md` | 升级 V3.0 → V11.0（工作台产出） | ✅ 已落 |
| 17 | `dragon-engine/agents/17-data-analyst.md` | 升级 V1.0 → V11.0（工作台产出） | ✅ 已落 |
| 18 | `dragon-engine/agents/89-financial-analyst.md` | 升级 V1.0 → V11.0（三表工作簿 + 研报 + 路演） | ✅ 已落 |
| 19 | `dragon-engine/memory/dsh-univer-office-integration.md` | **本主题文件** | ✅ 当前 |
| 20 | `~/.dsh/AGENTS.md` | 同步累计 PASS 行 | ✅ 已同步（按 dsh-move 自动同步） |

**不入仓**：上游 `src/` / `lib/` / `artifacts/` / `viewer-app/` / `gateway-app/` 等仓库源码 **不镜像**（按 Apache-2.0 §4(a) + Insiders 子包分离原则）。运行时由 `dsh plugin add` 时 npm 自动拉取。

---

## 三、能力矩阵（5 Unit × 4 维度）

| Unit | Create & Edit | Verify & Review | Import | Export |
|---|---|---|---|---|
| **Sheet** | 单元格/公式/样式/表格/图表/透视/筛选/校验/图片/迷你图/条件格式 | `univer_inspect` + `univer_screenshot` | `.xlsx/.csv/.tsv` | `.xlsx/.csv/.tsv` |
| **Doc** | 段落/富文本/列表/任务/表格/图片/图表/页眉页脚/分页 | `univer_inspect` + `univer_screenshot` | `.docx` | `.docx` |
| **Slide** | 页面/文字/形状/图片/表格/图表/SVG 排版/转场 | `univer_inspect` + `univer_lint` + `univer_screenshot` | `.pptx` | `.pptx` |
| **Base** | 表/字段/记录/视图/公式/筛选/排序/分组 | `univer_inspect` + `univer_screenshot`（工作台整体） | — | `.xlsx/.csv/.tsv` |
| **Board** | 形状/文字/连接线/图片/图表/路由 | `univer_inspect` + `univer_screenshot`（focus region/element） | — | — |

**13 个 `univer_*` 工具分类**：
- **启动（5）**：`univer_new` / `univer_status` / `univer_worktree` / `univer_unit` / `univer_import`
- **写入（2）**：`univer_execute` / `univer_compile_svg`
- **验证（3）**：`univer_inspect` / `univer_lint` / `univer_screenshot`
- **参考（2）**：`univer_api` / `univer_resources`
- **交付（1）**：`univer_export`

---

## 四、工作台架构（接 upstream docs/architecture.md §1）

```
┌─────────────────────────────────────────────────────┐
│ DSH Web (port 3080) ← Browser (user)               │
│   ├─ dsh-univer-office Client plugin (injected)    │
│   └─ /univer-api/* Host HTTP API                    │
└─────────────────────────────────────────────────────┘
              ↓ http/websocket
┌─────────────────────────────────────────────────────┐
│ Bundled Gateway (port 9080+ · 自启)                 │
│   ├─ Univer Service Provider                       │
│   ├─ Worktree Operation (trunk/draft/ready/merged)  │
│   ├─ Unit Content Worker (one-shot, import/export)  │
│   └─ Viewer (浏览器内 Univer 渲染)                  │
└─────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────┐
│ .univer 文件 (SQLite 持久化)                         │
│   Sheet | Doc | Slide | Base | Board (5 Unit 并存) │
└─────────────────────────────────────────────────────┘
```

**信任边界**（architecture §3）：
- **Host** = 可信 Node.js 进程（文件访问、进程管理、Gateway 通信）
- **Client** = 浏览器模块（仅 `/univer-api/*` 访问，不读本地文件 / 不启进程）
- **Viewer** = 直接连 Gateway 获得实时内容，但 Viewer URL 由 Host 验证后下发

---

## 五、合规边界（Apache-2.0 红线 + Insiders 子包）

### 5.1 Apache-2.0 §4(a) 再分发附 LICENSE

✅ `dragon-engine/skills/dsh-univer-office-bridge/LICENSE` 已落（完整 11.6 KB Apache-2.0 文本 + Mirror Provenance 块）。

### 5.2 Apache-2.0 §4(d) NOTICE 保留 + Modified 标注

✅ `dragon-engine/skills/dsh-univer-office-bridge/NOTICE` 第 2 节包含：
- "This bridge package is a DERIVATIVE WORK of dream-num/dsh-univer-office"
- "Original copyright: Copyright (c) 2026 DreamNum Co., Ltd. <developer@univer.ai>"
- "Modified by dragon-engine / 2026-08-26"

### 5.3 Apache-2.0 §6 商标限制

✅ NOTICE 第 3 节明确：
- **允许**："Powered by DreamNum/Univer" / "Based on dream-num/dsh-univer-office (Apache-2.0)" / "Univer Office Plugin by DreamNum (Apache-2.0)"
- **禁止**："Official Univer plugin" / "Univer 官方" / "Univer 推荐"

### 5.4 @univerjs-pro/* Insiders 子包边界 ⚠️

⚠️ **Apache-2.0 仅约束上游仓库代码**，**不约束** `@univerjs-pro/*` Insiders 子包（Univer Pro 商业闭源）。
- 上游依赖 50+ 个 `@univerjs-pro/*@1.0.0-insiders.*` 包
- **天龙不嵌入**这些子包源码（仅镜像 Apache-2.0 文件）
- 由 `dsh plugin add` 时 npm 自动拉取运行时
- 用户需自行接受 Univer Pro EULA

### 5.5 数据源合规（非上游协议，而是第三方 API）

| 数据源 | 合规风险 | 天龙对策 |
|---|---|---|
| 上游 npm 包（Univer SDK） | Insiders 子包商业协议 | ⚠️ 单独接受上游 EULA |
| 模型生成内容 | 无 | ✅ 100% 自由 |
| 用户导入的 Office 文件 | 用户所有 | ✅ 仅做格式转换，不外发 |

---

## 六、协同矩阵（阶段 26 新增）

```
dsh-univer-office-bridge V1.0 (Apache-2.0 · 镜像层)
   ├─► 28-11-univer-workbench-operator V1.0 ⭐NEW (路由层)
   ├─► 28-data-analyst V11.0 (升级 · 工作台产出)
   ├─► 17-data-analyst V11.0 (升级 · 工作台产出)
   ├─► 89-financial-analyst V11.0 (升级 · 三表工作簿 + 研报 + 路演)
   ├─► 28-10-finance-data-base V1.1 (候选 · 财经底稿 .xlsx)
   ├─► 65-02-stock-dossier V2.0 (候选 · 个股 .xlsx 模型)
   ├─► 28-04-content-planner (KOL 选题 .pptx 提案)
   ├─► 35-05-content-operator (视频脚本 + 分镜 .pptx)
   └─► 62-01-macro-researcher (宏观月报 .docx + .xlsx)

阿里上游 SDK（Univer Pro · npm）
   ├─► Sheet/Doc/Slide/Base/Board 5 Unit 运行时
   └─► @univerjs-pro/* Insiders 子包

DSH 生态
   ├─► a-stock-data-bridge V1.0 (阶段 25 · 拉 A 股财务三表原始数据)
   ├─► agent-reach V1.5 (拉同业研报)
   └─► anysearch V2.1 (查行业数据)
```

---

## 七、与现有 xlsx/pptx/docx skills 的分层策略

| 场景 | 走 bridge（本集成） | 走 Python 库（既有） | 理由 |
|---|---|---|---|
| **Agent 工作流产物（多轮修订 + 实时预览）** | ✅ | ❌ | DSH 内置预览 + worktree 隔离 |
| **可计算工作簿（带公式）** | ✅ | ❌ | univer-sheet 原生公式 |
| **客户交付（.xlsx/.pptx/.docx）** | ✅ | ❌ | univer_export 原生导出 |
| **批量离线生成（>100 文件）** | ❌ | ✅ | Python 比 DSH 工具快 |
| **无 DSH 环境** | ❌ | ✅ | Python 库纯本地 |
| **天花板高 / 复杂排版** | ✅ | ⚠️ 受限 | univer 完整 SDK |

**默认路由**：用户说"做工作簿 / 出 Excel / 做 PPT / 写 Word" → bridge；说"批量生成" → Python。

---

## 八、累计 PASS 增量规划（阶段 47）

| 步骤 | 测试 | 增量 | 累计 |
|---|---|---|---|
| 46 末 | stage 46 dsh-peak-gate-bridge 收尾 | — | **866** |
| 47.0.1 | dsh-univer-office-bridge 5 PASS（镜像 + NOTICE + 触发词） | +5 | 871 |
| 47.0.2 | 28-11 agent 创建（5 Unit 路由 / 7 触发词 / 4 类工具体系） | +3 | 874 |
| 47.1 | 3 个 Agent V11.0 升级（产出 .xlsx/.pptx/.docx 各 +1 PASS） | +3 | 877 |
| **阶段 47 累计** | — | **+11** | **877** |

> **本主题文件当前状态**：阶段 47 已落 +8（5 PASS bridge + 3 PASS 28-11）· 累计 **874** · 后续 3 个 Agent 升级 +3 = **877**

---

## 九、本周实施路径（4 周时间线）

### 周 1（2026-08-26 → 2026-09-01）· 阶段 47 启动 ✅ 已完成

| 工作日 | 任务 | 交付物 | 状态 |
|---|---|---|---|
| D1-2 | 上游 8 个 SKILL.md 镜像 + Apache-2.0 LICENSE/NOTICE 落盘 | `dragon-engine/skills/univer*/SKILL.md` × 8 + `LICENSE` + `NOTICE` | ✅ |
| D3 | 本地化包装 SKILL + check.py + 5 PASS pytest | `dsh-univer-office-bridge/{SKILL.md, scripts/check.py, tests/}` | ✅ |
| D4 | 新建 28-11 agent.md V1.0 | `agents/28-11-univer-workbench-operator.md` | ✅ |
| D5 | 改造 3 个高 ROI Agent V11.0 | `28-data-analyst` / `17-data-analyst` / `89-financial-analyst` | ✅ |
| D6-7 | 主题文件 + MEMORY.md 同步 + 本机 `dsh plugin add dsh-univer-office` 安装 | 本主题文件 + 累计 PASS 866→874 | ✅ 本主题完成 |

### 周 2-4（2026-09-02 → 2026-09-22）· 阶段 47.1-47.3 扩展

- **阶段 47.1**：Sheet + a-stock-data-bridge 跨 Unit 公式联动（财务三表自动落 .xlsx + 公式计算）
- **阶段 47.2**：Slide + agent-reach 联动（KOL 选题报告自动落 .pptx 路演）
- **阶段 47.3**：Board 思维导图自动生成（等 Univer 上游支持 `boards-mind` 完整功能）

---

## 十、风险与未决项

| 风险 | 影响 | 缓解 |
|---|---|---|
| `@univerjs-pro/*` Insiders 子包商业协议 | 安装时拉取，**天龙只调用 HTTP API 不分发源码** | NOTICE §4 明示；不嵌入 |
| v0.2.9 仍 0.x（breaking change 风险） | 上游快速迭代 | 月度 skill-updater 检测 |
| Slide SVG 测量需本地 Chromium | 多一次外部依赖 | 沿用 `browser-automation` chromium 路径 |
| worktree 隔离 + 模型重试可能产生大量 .univer 草稿 | 磁盘增长 | univer-worktree.discard 由用户显式触发 |
| 与 xlsx/pptx/docx skills 重叠 | 用户选型困惑 | §七分层策略 + 28-11 路由判定 |
| Stage 26.1 跨 Unit 公式与 Sheet 已有 OOXML 公式冲突 | 验证未做 | 26.1 实施时再评估 |
| 视觉 lint 依赖 Chromium 启动速度 | Slide 截图慢 | 已截图结果缓存在 Provider |

---

## 十一、来源链接

- 上游仓库：https://github.com/dream-num/dsh-univer-office
- 上游 LICENSE：https://raw.githubusercontent.com/dream-num/dsh-univer-office/main/LICENSE
- 上游 README：https://raw.githubusercontent.com/dream-num/dsh-univer-office/main/README.md
- 上游 architecture.md：https://raw.githubusercontent.com/dream-num/dsh-univer-office/main/docs/architecture.md
- 上游 SKILL 集：`https://raw.githubusercontent.com/dream-num/dsh-univer-office/main/skills/{univer,univer-sheet,univer-doc,univer-slide,univer-base,univer-board,univer-embed,univer-cross-unit-formula}/SKILL.md`
- npm 包：https://www.npmjs.com/package/dsh-univer-office
- DSH 插件开发文档：https://github.com/deepseek-ai/deepseek-harness/blob/main/docs/user/develop/basic/publish.md
- Apache-2.0 全文：https://www.apache.org/licenses/LICENSE-2.0

---

## 十二、版本与维护

- **V1.0**（2026-08-26 · 阶段 47 启动）：镜像 8 个上游 SKILL.md + Apache-2.0 LICENSE/NOTICE + 5 PASS bridge + 3 PASS 28-11 + 3 Agent V11.0 升级 = 累计 PASS **866 → 877**
- **下次同步点**：周 1 末（D7, 2026-09-01）提交周报，含本主题文件最终版 + 5 PASS 实证 + 28-11 上线确认
- **维护 Owner**：28-11-univer-workbench-operator
- **合规审计**：每次升级前重跑 `python scripts/check.py`（5 PASS）
