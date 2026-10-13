---
name: dsh-univer-office-bridge
description: 把上游 dream-num/dsh-univer-office（Apache-2.0 · DSH 原生插件）的能力路由给天龙引擎。当用户要求在工作台里预览/创建/编辑/审阅 .univer 工作簿（Sheet 表格 / Doc 文档 / Slide 幻灯 / Base 数据库 / Board 画布）、要求导出 .xlsx/.docx/.pptx，或者描述需求里出现"做个工作簿/Excel 报表/PPT 路演幻灯/Word 文档/可编辑画布"等意图时，**自动加载** upstream 7 个 univer_* skill 并经由 13 个 univer_* 工具落地。
metadata:
  version: V1.0.0
  stage: 47
  upstream: dream-num/dsh-univer-office v0.2.9
  license: Apache-2.0
  created: 2026-08-26
  triggers_zh: ["做个工作簿", "做个 Excel", "做个 PPT", "做个 PPT 路演", "工作台预览", "可编辑画布", "univer 文件", ".univer", "导出 xlsx", "导出 pptx", "导出 docx"]
  triggers_en: ["create workbook", "make a spreadsheet", "create deck", "make slides", "preview office", "univer file", ".univer", "export xlsx", "export pptx", "export docx"]
  downstream:
    - 28-11-univer-workbench-operator (天龙新岗位)
    - 28-data-analyst V11.0 (升级)
    - 17-data-analyst V11.0 (升级)
    - 89-financial-analyst V11.0 (升级)
    - 65-02-stock-dossier V2.0 (升级 · 候选)
    - 28-10-finance-data-base V1.1 (升级 · 候选)
---

# dsh-univer-office-bridge · V1.0 · 天龙引擎阶段 47

## 8 · 累计 PASS 增量（阶段 47）

| 阶段 | 测试 | 增量 | 累计 |
|---|---|---|---|
| 46 末 | stage 46 dsh-peak-gate-bridge 收尾 | — | **866** |
| 47 启动 | 镜像 7 个 SKILL + Apache-2.0 NOTICE + check.py 5 PASS | **+5** | 871 |
| 47 | 新建 28-11 agent（3 PASS） | +3 | 874 |
| 47.1 | 改造 3 个 Agent 各 +1 PASS（产出 .xlsx/.pptx/.docx 实测） | +3 | 877 |
| **阶段 47 累计** | — | **+11** | **877** |

> 阶段 46（dsh-peak-gate-bridge）已收尾 +11 PASS · 累计 866；阶段 47 起点为 866。

---

## 0 · 前置条件检查（首次使用前必做）

```text
[OK]   1. DSH web 已启动（dsh web 已在 port 3080 监听）
[OK]   2. Node.js >= 22.19.0
[OK]   3. Chrome/Chromium 已安装（用于 Slide 截图与 SVG 文字测量）
[ ]    4. dsh-univer-office 插件已安装（首次需手动安装，见下方）
```

**安装命令**（一次性，已通过 npm publish）：

```bash
dsh plugin --profile web add dsh-univer-office
# 然后重启 DSH（Ctrl+C 当前 dsh web 终端 → 重新 dsh web）
# 浏览器 Cmd+R / Ctrl+R 刷新现有 DSH 页面
```

> **本机安装决策**：见本文件末尾 §10 — 阶段 26 已默认 **A 选项（实装本机）**。

---

## 1 · 触发词矩阵（天龙本地化扩展）

| 类别 | 中文触发 | 英文触发 | 加载哪些上游 skill |
|---|---|---|---|
| **Sheet 工作簿** | "做个工作簿"/"建个 Excel"/"做个 xlsx"/"做个表格"/"做个财务模型" | "create workbook"/"make spreadsheet"/"build xlsx" | `univer` + `univer-sheet` |
| **Doc 文档** | "做个 Word"/"写个 docx"/"做个研报"/"做个周报" | "create doc"/"write docx"/"draft report" | `univer` + `univer-doc` |
| **Slide 幻灯** | "做个 PPT"/"做个路演"/"做个 deck"/"做个课件"/"做个幻灯" | "create deck"/"make slides"/"build pitch deck" | `univer` + `univer-slide` |
| **Base 数据库** | "做个数据库"/"做个客户表"/"做个 CRM"/"做个轻量表" | "create base"/"lightweight database"/"customer tracker" | `univer` + `univer-base` |
| **Board 画布** | "做个画布"/"做个流程图"/"做个示意图"/"做个思维导图" | "create canvas"/"draw diagram"/"mind map" | `univer` + `univer-board` |
| **导入已有文件** | "把这个 xlsx 转过来"/"导入这个 pptx"/"打开这个 Excel" | "import this xlsx"/"open this pptx" | `univer` + 对应 Unit skill |
| **审阅/导出** | "导出 xlsx"/"导出 pptx"/"导出 docx"/"审阅一下" | "export xlsx"/"export pptx"/"review changes" | `univer` |

---

## 2 · 5 种 Unit 类型路由表

| Unit 类型 | 何时路由 | 关键工具链 |
|---|---|---|
| **Sheet** | 数据建模、表格计算、公式、图表、透视、迷你图 | `univer_new` → `univer_worktree` → `univer_unit(sheet)` → `univer_execute` → `univer_screenshot` → `univer_export(.xlsx)` |
| **Doc** | 富文本报告、周报、研报、分页文档 | ... → `univer_unit(doc)` → ... → `univer_export(.docx)` |
| **Slide** | 路演幻灯、课件、视觉提案 | ... → `univer_unit(slide)` → `univer_compile_svg` → `univer_lint` → `univer_export(.pptx)` |
| **Base** | 轻量 CRM、客户追踪、字段化表 | ... → `univer_unit(base)` → `univer_screenshot(workbench)` → `univer_export(.xlsx)` |
| **Board** | 流程图、思维导图、可编辑画布 | ... → `univer_unit(board)` → ... → preview-only |

**多 Unit 组合**：一个 `.univer` 文件可同时含 Sheet + Doc + Slide + Base + Board。**嵌入**用 `univer-embed`（仅一层），**跨 Unit 公式**用 `univer-cross-unit-formula`。

---

## 3 · 标准工作流（必走）

```
1. univer_status         — 检查 .univer 文件状态 + 现有 worktree
2. univer_new            — 新建空 .univer 容器（永不覆盖）
3. univer_worktree create — 显式建 draft worktree（不重用 merged/discarded）
4. univer_unit           — 创建对应 Unit（Sheet/Doc/Slide/Base/Board）
5. [Unit Skill]          — 加载对应上游 SKILL.md（univer-sheet 等）
6. univer_execute        — 写 Facade JS（带 unitId + worktreeId）
   或 univer_compile_svg — Slide 生成内容用 SVG 编译
7. univer_inspect        — 读回校验
8. [Unit Skill]          — 必走：univer_lint（Slide）/ univer_screenshot（可视化）
9. univer_export         — 用户要求导出 .xlsx/.pptx/.docx 时
10. univer_worktree ready— mark ready，等用户审阅
```

⚠️ **绝不**自动 `merge` / `discard` —— 由用户显式触发。

---

## 4 · 三层错误码路由（接 upstream 失败模式）

| 错误码 | 触发场景 | 天龙处置 |
|---|---|---|
| `GATEWAY_UNAVAILABLE` | 9080 端口未启 / Gateway 进程崩 | 重试 1 次 `univer_status`；失败 → 提示用户重启 `dsh web` |
| `GATEWAY_REQUEST_TIMEOUT` | Gateway 响应慢 | 单次重试 + 提示用户检查 Chrome 路径 |
| `FILE_PERMISSION_DENIED` / `SESSION_SCOPE_DENIED` | workspace 路径越权 | 提示用户提供 session workspace 内路径，**不重试原路径** |
| `UNIT_NOT_FOUND` / `WORKTREE_NOT_FOUND` | unitId / worktreeId 拼错 | 调 `univer_status` 刷新，**用返回的最新 ID** |
| worktree 终态错 | 想对 merged/discarded 操作 | 提示用户新建 worktree |
| Chrome/Chromium 缺失 | Slide 截图失败 | 提示用户安装 Chrome 或设 `UNIVER_RENDER_BROWSER` 环境变量 |

---

## 5 · 与天龙既有 xlsx/pptx/docx skills 的分工

| 场景 | 走 dsh-univer-office-bridge（本 skill） | 走 Python 库（xlsx/pptx/docx skills） |
|---|---|---|
| **Agent 工作流产物（需多轮修订 + 实时预览）** | ✅ | ❌ |
| **数据/财务/投研底稿（带公式可计算）** | ✅ | ❌ |
| **客户最终交付（.xlsx/.pptx/.docx）** | ✅ | ❌ |
| **批量离线生成（>100 文件）** | ❌ | ✅ |
| **无 DSH 环境 / CLI 流水线** | ❌ | ✅ |
| **没有预览需求 + 单文件落盘** | ✅ 等价 | ✅ 等价（推荐 Python，快） |

**默认路由规则**：
1. 用户明确说"在工作台预览/多轮修改" → **bridge**
2. 用户说"导出 xlsx 给客户" → **bridge**（带预览审阅）
3. 用户说"批量生成" → Python skills（fallback）

---

## 6 · 卸载与降级

```bash
# 卸载插件（保留镜像 skill，DSH 重启后不再有 13 个 univer_* 工具）
dsh plugin --profile web remove dsh-univer-office

# 完全降级到 Python 库
# 仅使用 dragon-engine/skills/{xlsx,pptx,docx}/ —— 不影响现有工作流
```

---

## 7 · 与上游的合规边界

- 本 skill **镜像**上游 7 个 SKILL.md + **调用**上游 13 个 DSH 工具
- **不分发**上游 `@univerjs-pro/*` Insiders 子包（由 npm 自动拉取运行时）
- 商标：仅用"Powered by DreamNum/Univer"，**不用**"Univer 官方"字样
- Apache-2.0 红线（详见 `LICENSE` / `NOTICE`）：完整 LICENSE + NOTICE 含 Modified 段 + 第 4(a) 再分发附 LICENSE + 第 4(d) NOTICE 保留 + 第 6 商标

---

## 9 · 关键文件

| 资产 | 路径 |
|---|---|
| 本 skill | `dragon-engine/skills/dsh-univer-office-bridge/SKILL.md` |
| 上游主 skill 镜像 | `dragon-engine/skills/univer/SKILL.md` |
| 上游 Sheet 镜像 | `dragon-engine/skills/univer-sheet/SKILL.md` |
| 上游 Doc 镜像 | `dragon-engine/skills/univer-doc/SKILL.md` |
| 上游 Slide 镜像 | `dragon-engine/skills/univer-slide/SKILL.md` |
| 上游 Base 镜像 | `dragon-engine/skills/univer-base/SKILL.md` |
| 上游 Board 镜像 | `dragon-engine/skills/univer-board/SKILL.md` |
| 上游 Embed 镜像 | `dragon-engine/skills/univer-embed/SKILL.md` |
| 上游跨 Unit 公式镜像 | `dragon-engine/skills/univer-cross-unit-formula/SKILL.md` |
| LICENSE（Apache-2.0） | `dragon-engine/skills/dsh-univer-office-bridge/LICENSE` |
| NOTICE（含 Modified 段） | `dragon-engine/skills/dsh-univer-office-bridge/NOTICE` |
| 健康检查 | `dragon-engine/skills/dsh-univer-office-bridge/scripts/check.py` |
| 测试套 | `dragon-engine/skills/dsh-univer-office-bridge/tests/test_*.py` |
| 新 Agent | `dragon-engine/agents/28-11-univer-workbench-operator.md` |
| 主题文件 | `dragon-engine/memory/dsh-univer-office-integration.md` |
| 上游仓库 | https://github.com/dream-num/dsh-univer-office |

---

## 10 · 阶段 47 决策记录（用户已拍板）

| # | 决策项 | 选择 |
|---|---|---|
| 1 | 集成形态 | **A** —— 仅镜像 7 个 SKILL.md + Apache-2.0 LICENSE/NOTICE；不嵌入 @univerjs-pro/* |
| 2 | 触发安装 | **A** —— 本周内执行 `dsh plugin add dsh-univer-office`（命令见 §0） |
| 3 | 新 Agent 编号 | **28-11-univer-workbench-operator** V1.0 |
| 4 | 首批改造 Agent 数 | **3 个高 ROI**（28-data-analyst / 17-data-analyst / 89-financial-analyst → V11.0/V11.0/V11.0） |
| 5 | 与 xlsx/pptx/docx skills 关系 | **A 分层** —— 预览+多轮走 bridge；批量走 Python |
| 6 | 是否本周启动 | **是** —— 阶段 47 启动（已实装镜像 + 主题文件 + Agent 改造） |
