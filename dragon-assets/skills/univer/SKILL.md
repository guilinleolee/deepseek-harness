---
name: univer
description: Create, inspect, edit, import, export, and hand off multi-Unit .univer files through DSH tools and isolated worktrees. Use proactively for any task involving .univer files, spreadsheets or .xlsx/.csv/.tsv data, presentations or .pptx slides, .docx documents, Base databases, Board canvases, cross-Unit content, or exact Univer Facade API authoring; load this before the matching Unit skill.
metadata:
  source: dream-num/dsh-univer-office v0.2.9 (Apache-2.0)
  mirrored: 2026-08-26
  version_upstream: 0.2.9
---

> **Apache-2.0 镜像说明**：本文件是上游 `dream-num/dsh-univer-office` 仓库 `skills/univer/SKILL.md` 的镜像。原始仓库版权属于 DreamNum Co., Ltd.，遵循 Apache-2.0 协议（详见 `LICENSE` / `NOTICE`）。
>
> **完整上游文件**：[https://raw.githubusercontent.com/dream-num/dsh-univer-office/main/skills/univer/SKILL.md](https://raw.githubusercontent.com/dream-num/dsh-univer-office/main/skills/univer/SKILL.md)（约 200 行）
>
> **下游使用方式**：调用上游 DSH 插件 `dsh-univer-office` 的 13 个 `univer_*` 工具，由上游自动加载完整 SKILL 内容。

---

# Univer files（镜像摘要 · 完整版见上游）

使用结构化的 `univer_*` 工具处理所有 Office 内容的创建、读取、修改、转换与审阅任务。**不要**等待用户指定工具名；**不要**调用全局 `univer` CLI；**不要**直接编辑 `.univer` 存储；**不要**用 openpyxl/python-pptx/python-docx/ZIP 操作等替代方案。

## 立刻开始

- **已有 `.univer` 文件**：先调 `univer_status` 选定 Unit 和 worktree
- **新建 `.univer`**：调 `univer_new` + `univer_worktree action:"create"`
- **Office 源文件**（.xlsx/.csv/.tsv/.docx/.pptx）：新建 `.univer` 与 draft worktree 后调 `univer_import`
- **写入前必加载对应 Unit skill**：`univer-sheet` / `univer-doc` / `univer-slide` / `univer-base` / `univer-board`
- **如果嵌入了其他 Unit**：同时加载 `univer-embed`
- **跨 Unit 公式**：同时加载 `univer-cross-unit-formula`

## 心智模型（精简）

- `.univer` 文件是多 Unit 容器。每个 Sheet/Doc/Slide/Base/Board 是顶层 Unit，带稳定 `unitId`
- `trunk` 是审阅主线。worktree 是 Agent 改动的隔离作用域，**没有隐式当前 worktree**
- **每次内容写入需要完整三元组**：`file` + draft `worktreeId` + `unitId`
- `univer_execute` 仅在 Facade mutation 发生时持久化；只读执行不产生 revision
- `ready` 拒绝写入直到 `reopen`；`merged` / `discarded` 是终态，**永不重用**
- **工具成功不等于正确性证据** —— 必须读回模型并校验任务相关断言

## 必走工作流（10 步）

1. `univer_status` 发现 Unit IDs 与 worktree 状态
2. 创建或选定 draft worktree（继续已有 worktree 需先确认状态）
3. `univer_unit` 创建 Unit 或 `univer_import` 导入
4. 加载对应 Unit skill（`univer-sheet` 等）
5. 未知 Facade 用 `univer_api action:"find"` 查，不要猜
6. 通过 `univer_execute` mutation（Slide 生成内容用 `univer_compile_svg`）
7. `univer_inspect` 读回改动；缺失字段用新的只读 `univer_execute` 补读
8. **每个被改动的 Slide 页**：调 `univer_lint` 并解决每条 finding
9. **可视化相关改动**：调 `univer_screenshot` 显式 workspace output 目录
10. 用户请求时 `univer_export` 导出；mark `ready` 并 `univer_status` 确认

## 工具地图（13 个 `univer_*` 工具）

| 阶段 | 工具 | 用途 |
|---|---|---|
| 启动 | `univer_new` | 创建空 `.univer` 容器，永不覆盖，永不创建隐式 Unit |
| 启动 | `univer_status` | 列出 trunk Units 与 worktrees，或检查显式作用域 |
| 启动 | `univer_worktree` | `create` / `ready` / `reopen` / `merge` / `discard` |
| 启动 | `univer_unit` | 在 draft worktree 中增删 Sheet/Doc/Slide/Base/Board |
| 启动 | `univer_import` | 把本地 xlsx/csv/tsv/docx/pptx 导入为新 Unit |
| 写入 | `univer_execute` | 在 draft worktree 的一个 Unit 上跑版本匹配的 Facade JS |
| 写入 | `univer_compile_svg` | 把 workspace SVG 编译到一个显式 Slide 页（含浏览器文字测量） |
| 验证 | `univer_inspect` | 从 trunk 或 worktree 读取结构化 Unit 内容 |
| 验证 | `univer_lint` | 检查 Slide 文本越页 / 越框 / 重叠 |
| 验证 | `univer_screenshot` | 把 Sheet/Doc/Slide/Base/Board 渲染为 PNG 证据并返回给图片能力模型 |
| 参考 | `univer_api` | 按 API 关键字查找版本匹配的 Facade 符号 |
| 参考 | `univer_resources` | 列出 / 查找 / 读取 / 导出内置 SVG 资源或清理下载缓存 |
| 交付 | `univer_export` | 把 Sheet/Base 导出为 xlsx/csv/tsv，Doc 为 docx，Slide 为 pptx |

## 失败恢复（按错误码路由，不要解析自然语言）

| 错误码 | 处置 |
|---|---|
| `GATEWAY_UNAVAILABLE` / `GATEWAY_REQUEST_TIMEOUT` | 重试一次 `univer_status` 读；写入超时先 inspect 再继续 |
| `FILE_PERMISSION_DENIED` / `SESSION_SCOPE_DENIED` | 换 workspace 内可访问路径，**不要重试同一路径** |
| worktree / Unit 状态错 | `univer_status` 刷新；`ready` worktree 用 `reopen`；终态 worktree 重建 |

## 红线（DON'T）

- 🔴 **不要**等待用户报出工具名 —— 一旦判定任务涉及 Office 内容，**自动调用** `univer_*` 工具
- 🔴 **不要**调用全局 `univer` CLI
- 🔴 **不要**直接编辑 `.univer` 存储 / 用 openpyxl 等 Python 库替代
- 🔴 **不要**对 `merged` / `discarded` 终态 worktree 调 `reopen` —— 重建
- 🔴 **不要**在 `ready` worktree 上继续写入（必须先 `reopen`）
- 🔴 **不要**用 `mode: "add"` 修页 —— 只会叠加错误内容；改源 SVG 后用 `mode: "replace"` 重渲
- 🔴 **不要**凭工具 success 自夸"已完成" —— 必须 `univer_inspect` + `univer_lint` + `univer_screenshot` 三角验证
- 🔴 **不要**未等用户明确请求就 `merge` / `discard` —— 这两个操作必须由 DSH 审批

## 上游原文指针

- 完整 200+ 行 SKILL.md（含 Facade 执行细节、SVG 资源使用规范、Slide 重审工作流）：<https://raw.githubusercontent.com/dream-num/dsh-univer-office/main/skills/univer/SKILL.md>
- architecture.md（必须保留的产品功能 + 进程边界）：<https://raw.githubusercontent.com/dream-num/dsh-univer-office/main/docs/architecture.md>

## 相关天龙资源

- `dsh-univer-office-bridge` —— 本地化包装层（触发词 + 工作流 + Apache-2.0 NOTICE）
- `agents/28-11-univer-workbench-operator.md` —— Univer 工作台操作员
- `memory/dsh-univer-office-integration.md` —— 集成档案 V1.0
