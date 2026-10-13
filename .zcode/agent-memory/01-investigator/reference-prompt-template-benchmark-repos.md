---
name: reference-prompt-template-benchmark-repos
description: 2026-09-27 经 GitHub API 逐一核验的提示词/模板管理类仓库事实清单（star/license/活跃度/能力修正），供全局模板库功能引用
metadata:
  node_type: memory
  type: reference
  originSessionId: sess_subagent_agent_ee5cdd74-f7d6-4053-a343-4ad135de402d
---

2026-09-27 经 GitHub API 核验的提示词/模板管理生态事实（star 数截至当日）：

**候选核验（模板库对标）**
- `yarin-zhang/AI-Gist` — 889 星，AGPL-3.0，活跃（2026-09-15 push），Electron+Capacitor。README 明确有「AI 提取变量：无需手动挖空，AI 自动提取可能的变量」。数据模型在 `src/shared/types/database.ts`：Prompt/PromptVariable（name/type 5 类+兼容别名/defaultValue/options/required/placeholder/description/validation/sortOrder）/PromptHistory（全字段快照+version+changeDescription）。渲染双轨：`{{var}}` 正则 parse+reconcile（`src/renderer/lib/utils/prompt-template.ts`）+ Jinja（实为 nunjucks，`jinja.service.ts`）。导出/导入/完全替换（replaceAllData）/CSV/WebDAV/iCloud，云同步 v2 有 tombstone+checksum。
- `PromptPal/PromptPal` — 79 星，Go+GraphQL+ent，on-premise，2025-08-31 后停更。license 为自定义「非商业免费/商业需购」NOT MIT。README 自述早期阶段；版本 backup/diff 标注 Work in Progress（但 `schema/prompt.history.go` 已有 History 快照实体：Snapshot{Name,Description,Prompts[],Variables[]}+ModifierId）。「分类/标签/预览」在 README 无证据。
- `jonathanbertholet/promptmanager`（README 标题即 Open Prompt Manager）— 103 星，Chrome 扩展，**无 license 文件**。`#variable#` 变量语法、标签筛选、v2 JSON 备份（prompts/folders/tags）。
- `langgenius/dify` — 157.3k 星，Dify Open Source License（Apache 2.0+附加条件）。Prompt IDE 只是平台一小部分，作模板库参考过重。

**补充核验**
- `Nagi-ovo/voyager` — 20.2k 星，GPL-3.0，活跃；浏览器增强套件含任意网站提示词管理器。
- `liujuntao123/prompt-manager` — 296 星，**无 license**，Next.js+Supabase+Clerk（非本地）；README 附完整建表 SQL（prompts.version/tags TEXT 字段）。
- `espanso/espanso` — 14.5k 星，GPL-3.0，活跃；文本扩展器，变量/表单细节在官网 docs 而非 README。
- `SilentVoid13/Templater` — 5.3k 星，AGPL-3.0，活跃；README："insert variables and functions results into your notes" + 可执行 JS 操作变量。
- `pezzolabs/pezzo` — 3.3k 星，Apache-2.0，2026-08 后低频；prompt 版本管理/observability。
- `langfuse/langfuse` — 35.1k 星，活跃；LICENSE 文件实为「MIT 核心 + ee/ 目录商业条款」（GitHub API 显示 NOASSERTION，README 徽章写 MIT）；Prompt Management 定位 "centrally manage, version control"。
- `microsoft/PromptWizard` — 4.0k 星，MIT，2025-10 后低频；任务感知提示词优化（feedback-driven self-evolving）。
- `stanfordnlp/dspy` — 38.4k 星，MIT，活跃；少样本示例反向优化提示词（MIPROv2）。

**How to apply:** 引用以上项目写对标文档时直接使用本清单数据，但 star 数与活跃度会过时，超过 1 个月需重查；`jonathanbertholet/promptmanager` 与 `liujuntao123/prompt-manager` 无 license，只能借鉴思路不能复制代码。项目背景见 [[project-content-studio-topic-library]]。
