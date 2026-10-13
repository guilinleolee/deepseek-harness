# 阶段 47 dsh-univer-office · 用户拍板 B（延后重启）· 状态快照

> 写入日期：2026-08-26 · 阶段 47 已落 DSH plugin + 镜像 + 路由层 + Agent V11.0
> 决策：**B · 延后重启 DSH**（保留当前 session）
> 下次重启 DSH 后，13 个 `univer_*` 工具**自动**在浏览器生效（不需要任何额外命令）

---

## ✅ 已完成（本 session 落地）

| 项 | 状态 | 路径 / 命令 |
|---|---|---|
| 镜像上游 8 个 SKILL.md | ✅ | `dragon-engine/skills/{univer,univer-sheet,univer-doc,univer-slide,univer-base,univer-board,univer-embed,univer-cross-unit-formula}/SKILL.md` |
| 本地化包装 SKILL | ✅ | `dragon-engine/skills/dsh-univer-office-bridge/SKILL.md`（9 章） |
| Apache-2.0 LICENSE | ✅ | `dragon-engine/skills/dsh-univer-office-bridge/LICENSE`（11.6 KB verbatim） |
| Apache-2.0 NOTICE | ✅ | `dragon-engine/skills/dsh-univer-office-bridge/NOTICE`（含 Modified by dragon-engine / 2026-08-26） |
| 触发词速查（130 个） | ✅ | `dragon-engine/skills/dsh-univer-office-bridge/references/triggers.md` |
| 健康检查脚本 | ✅ | `dragon-engine/skills/dsh-univer-office-bridge/scripts/check.py`（5 PASS） |
| pytest 5 项 | ✅ | `dragon-engine/skills/dsh-univer-office-bridge/tests/test_{01..05}_*.py`（5/5 PASS） |
| **本机安装 DSH 插件** | ✅ | `node D:\deepseek-harness\apps\cli\lib\bin.js plugin --profile web add dsh-univer-office` 跑通 |
| reconcile 到 web profile | ✅ | `C:\Users\li\.dsh\profiles\web\package.json` line 16 加入 `dsh-univer-office` |
| 上游 8 个 SKILL 目录 | ✅ | `C:\Users\li\.dsh\profiles\web\node_modules\dsh-univer-office\skills\{...}` |
| 新建 28-11 Agent V1.0 | ✅ | `dragon-engine/agents/28-11-univer-workbench-operator.md` |
| 3 Agent V11.0 升级 | ✅ | `dragon-engine/agents/{28-data-analyst,17-data-analyst,89-financial-analyst}.md` |
| 主题文件 V1.0 | ✅ | `dragon-engine/memory/dsh-univer-office-integration.md` |
| MEMORY.md stage 47 行 + 累计 874 | ✅ | `dragon-engine/memory/MEMORY.md` line 83 + line 88 |
| 安装完成备忘 | ✅ | `dragon-engine/skills/dsh-univer-office-bridge/references/install-completed.md` |
| 本 handoff 文件 | ✅ | 本文件 |

## ⏸ 待用户操作（择期）

### 重启 DSH 触发 13 个 univer_* 工具激活

任一方式即可：

```powershell
# 方式 A：手动 Ctrl+C 当前 dsh 终端 + 重启
# 1. 找到当前跑 dsh web 的终端窗口
# 2. Ctrl+C
# 3. 重新启动：
cd "D:\deepseek-harness\apps\cli"
node lib/bin.js web
# 4. 浏览器 Cmd+R / Ctrl+R 刷新 http://127.0.0.1:3080
```

```powershell
# 方式 B：直接结束 node 进程 + 重启
Get-Process node | Where-Object { $_.MainWindowTitle -like "*dsh*" } | Stop-Process -Force
cd "D:\deepseek-harness\apps\cli"
node lib/bin.js web
```

### 重启后验证 1 条命令

在 DSH 新 session 里发：

```
打开 D:\知识库\FDE\秉凌自媒体工作台\输入内容\，帮我做一个简单的工作簿，列出本周待办事项。
```

如果 `28-11-univer-workbench-operator` 路由生效，浏览器会**实时弹出 Univer Viewer 浮窗** + 创建 `.univer` 文件。

## 📊 阶段 47 累计 PASS 实绩

```
stage 46 末      ───────────────────────────────────► 866 PASS
   │ +5 bridge (mirror + NOTICE + 触发词)          ─► 871
   │ +3 28-11 agent (5 Unit 路由 / 7 触发词 / 4 工具体系)
                                                   ─► 874
   ▼
阶段 47 启动完成（plugin 装好，重启激活工具）    ─► 874 PASS ✅ 锁定
```

### Stage 47.1 / 47.2 / 47.3 候选（下次接力）

| 子阶段 | 内容 | 增量 PASS |
|---|---|---|
| **47.1** | 3 Agent V11.0 实测（产出真实 .xlsx/.pptx/.docx 文件） | +3 → 877 |
| **47.2** | Sheet + a-stock-data-bridge 跨 Unit 公式联动（财务三表自动落 .xlsx + 公式） | +5 → 882 |
| **47.3** | Slide + agent-reach 联动（KOL 选题报告自动落 .pptx 路演） | +3 → 885 |

## 🔧 风险与回滚

- **回滚插件**（如果重启后 13 个工具冲突）：
  ```bash
  cd C:\Users\li\.dsh\profiles\web
  pnpm remove dsh-univer-office
  # 手动删 web/package.json bundles 里 dsh-univer-office 那行
  node D:\deepseek-harness\apps\cli\lib\bin.js web
  ```
- **Insiders 子包商业协议**：本机 install 已自动接受上游 EULA
- **Chromium 依赖**：Slide SVG 测量 + 截图需本地 Chrome，没装时只影响 `univer_lint` / `univer_screenshot`

## 📂 关键文件指针（接续用）

| 资产 | 路径 |
|---|---|
| 安装完成备忘 | `dragon-engine/skills/dsh-univer-office-bridge/references/install-completed.md` |
| 主题文件 | `dragon-engine/memory/dsh-univer-office-integration.md` |
| 本 handoff | `dragon-engine/memory/stage-47-handoff.md`（本文件） |
| MEMORY.md 阶段 47 行 | `dragon-engine/memory/MEMORY.md` line 83 + line 88 |
| 检查脚本 | `dragon-engine/skills/dsh-univer-office-bridge/scripts/check.py` |
| 测试套 | `dragon-engine/skills/dsh-univer-office-bridge/tests/`（5 pytest PASS） |

## 🔁 下次进入此项目先做 3 件事

1. **读本文件**（stage-47-handoff.md）—— 知道现状
2. **跑 pytest 复测**：`cd dragon-engine/skills/dsh-univer-office-bridge && python -m pytest tests/ -v`
3. **根据用户意图决定**：
   - 用户要"做工作簿 / PPT / Word" → 28-11 路由 → univer_* 工具
   - 用户要"批量生成" → xlsx/pptx/docx Python skills
   - 用户要"升级 47.1/47.2/47.3" → 接续阶段 47 子任务
