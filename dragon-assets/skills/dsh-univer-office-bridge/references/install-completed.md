# dsh-univer-office 安装完成 · 等待 DSH 重启激活

> 日期：2026-08-26 · 阶段 47

## 已完成（无需用户操作）

| 步骤 | 状态 | 证据 |
|---|---|---|
| ① pnpm 切到 npmjs.org | ✅ | `pnpm config get registry` = `https://registry.npmjs.org` |
| ② `node lib/bin.js plugin --profile web add dsh-univer-office` | ✅ | `https://registry.npmjs.org/dsh-univer-office/-/dsh-univer-office-0.2.9.tgz` 拉取成功 |
| ③ packages installed | ✅ | `C:\Users\li\.dsh\profiles\web\node_modules\dsh-univer-office\` 落盘 |
| ④ reconcile 到 web profile bundles | ✅ | `C:\Users\li\.dsh\profiles\web\package.json` line 16 加入 `dsh-univer-office` |
| ⑤ 上游 8 个 SKILL 目录全部装入 | ✅ | `node_modules/dsh-univer-office/skills/{univer,univer-sheet,univer-doc,univer-slide,univer-base,univer-board,univer-embed,univer-cross-unit-formula}/` 全部存在 |
| ⑥ 累计 PASS（bridge 5 + agent 3） | ✅ | pytest 5/5 PASS · 累计 866 → 874 |

## 待用户操作（重启 DSH 才能激活 13 个 univer_* 工具）

> **⚠️ 警告**：重启 DSH 会**中断当前 DSH Web GUI session**。建议在不需要继续对话时执行。

### 重启步骤（PowerShell）

```powershell
# 1. 当前 DSH 终端 Ctrl+C（如果还在前台跑）
#    或者从任务管理器结束 node 进程（PID 4876 / 9052 / 9172）

# 2. 重新启动 DSH web
cd "D:\deepseek-harness\apps\cli"
node lib/bin.js web
# 或如果你已设 PATH：dsh web

# 3. 浏览器 Cmd+R / Ctrl+R 刷新 http://127.0.0.1:3080
```

### 验证（重启后）

进入新 session 后试一句：

```
打开 D:\知识库\FDE\秉凌自媒体工作台\输入内容\，帮我做一个简单的工作簿，列出本周待办事项。
```

如果 28-11-univer-workbench-operator 正确路由，应该：
- DSH 浏览器里**实时弹出 Univer Viewer 浮窗**
- 创建出 `.univer` 文件
- 工具体系展示 `univer_new` / `univer_status` / `univer_unit` / `univer_execute` 等 13 个工具

## 累计 PASS 终值

```
stage 46 末      ──────────────────────────► 866 PASS
   │ +5 bridge PASS                       ─► 871
   │ +3 28-11 agent PASS                  ─► 874
   ▼
阶段 47 启动完成（plugin 装好待重启）    ─► 874 PASS
```

## 回滚方案

如果插件冲突导致 DSH 起不来：

```bash
# 1. 进 web profile 目录
cd C:\Users\li\.dsh\profiles\web

# 2. pnpm remove
pnpm remove dsh-univer-office

# 3. 编辑 package.json 删掉 bundles 里的 dsh-univer-office 一行
# 4. 重启 DSH
```
