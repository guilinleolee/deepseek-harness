# Skills 使用说明与索引（本仓库 `skills/`）

> 更新时间：2026-01-24  
> 覆盖范围：仅统计本仓库 `skills/` 目录下，**包含 `SKILL.md` 的技能**。  
> 索引口径：同名多份时优先选择“更靠近 `skills/` 根目录 / 非镜像目录”的那份，并在备注中列出其它入口。

---

## 快速索引

- **按分类**：下方「分类清单」跳转各小节。
- **按名称**：文末「[按名称速查](#按名称速查)」表，Ctrl+F 搜索 skill 名。
- **按场景**：看「[常见任务 → 推荐技能](#常见任务--推荐技能组合)」。

---

## 分类清单

| 分类 | 数量 | 跳转 |
|------|------|------|
| 过程型 / 工作流 | 21 | [→](#-过程型--工作流) |
| 编程宗师 (天龙八部) | 8 | [→](#-编程宗师-天龙八部) |
| 开发与代码质量 | 13 | [→](#-开发与代码质量) |
| 前端与 UI | 7 | [→](#-前端与-ui) |
| 文档与办公 | 6 | [→](#-文档与办公) |
| 营销与增长 | 7 | [→](#-营销与增长) |
| 科学研究 (Scientific) | 140 | [→](#-科学研究-scientific) |
| 设计与视觉 | 10 | [→](#-设计与视觉) |
| 浏览器 / 自动化与媒体 | 4 | [→](#-浏览器--自动化与媒体) |
| 工具与集成 | 5 | [→](#-工具与集成) |
| 写作与技能建设 | 2 | [→](#-写作与技能建设) |
| 其他 | 2 | [→](#-其他) |

---

### 过程型 / 工作流

规划、执行、审查、验证等流程类技能。

| Skill | 用途 | 入口 | GitHub |
|-------|------|------|--------|
| `brainstorming` | 做任何功能/行为变更前的需求澄清与方案探索 | [SKILL.md](./brainstorming/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/brainstorming) |
| `writing-plans` | 多步骤任务的计划拆解与执行顺序设计 | [SKILL.md](./writing-plans/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/writing-plans) |
| `executing-plans` | 有计划文档时的分步执行工作流（含检查点） | [SKILL.md](./executing-plans/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/executing-plans) |
| `dispatching-parallel-agents` | 2+ 独立任务并行分发 | [SKILL.md](./dispatching-parallel-agents/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/dispatching-parallel-agents) |
| `finishing-a-development-branch` | 开发完成后的合并/PR/清理决策流程 | [SKILL.md](./finishing-a-development-branch/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/finishing-a-development-branch) |
| `subagent-driven-development` | 子代理驱动开发（并行+质量门） | [SKILL.md](./subagent-driven-development/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/subagent-driven-development) |
| `using-git-worktrees` | Git worktree 隔离式并行开发 | [SKILL.md](./using-git-worktrees/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/using-git-worktrees) |
| `using-superpowers` | “技能优先”的工作方式与调用纪律（建议长期启用） | [SKILL.md](./using-superpowers/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/using-superpowers) |
| `requesting-code-review` | 提交前主动做代码审查的清单 | [SKILL.md](./requesting-code-review/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/requesting-code-review) |
| `receiving-code-review` | 收到 CR 反馈后的处理流程（先验证再改） | [SKILL.md](./receiving-code-review/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/receiving-code-review) |
| `systematic-debugging` | 系统化调试：先根因、后修复（四阶段） | [SKILL.md](./systematic-debugging/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/systematic-debugging) |
| `verification-before-completion` | 宣称完成前的验证流程（证据优先） | [SKILL.md](./verification-before-completion/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/verification-before-completion) |
| `verification-loop` | 构建/类型/lint/测试/安全/diff 的全链路验收 | [SKILL.md](./verification-loop/SKILL.md) | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/tree/main/skills/verification-loop) |

---

### 编程宗师 (天龙八部)

全自动人工智能开发军团，覆盖软件开发全生命周期。

| Skill | 用途 | 入口 | GitHub |
|-------|------|------|--------|
| `01investigator` | **/01调研师**：考古摸底，查清代码逻辑与技术坑点 | [SKILL.md](./investigator/SKILL.md) | — |
| `02architect` | **/02架构师**：划定蓝图，原子化拆解任务计划 | [SKILL.md](./architect/SKILL.md) | — |
| `03builder` | **/03构建师**：施工交付，编写高质量生产级代码 | [SKILL.md](./builder/SKILL.md) | — |
| `04validator` | **/04验证师**：极端找茬，跑压力与全方位测试 | [SKILL.md](./validator/SKILL.md) | — |
| `05security-reviewer` | **/05安全师**：专项排雷，扫描安全漏洞 | [SKILL.md](./security-reviewer/SKILL.md) | — |
| `06code-reviewer` | **/06审查师**：终极审计，评审安全、性能与美感 | [SKILL.md](./code-reviewer/SKILL.md) | — |
| `07scribe` | **/07记录师**：文明传承，自动维护高质量文档 | [SKILL.md](./scribe/SKILL.md) | — |
| `08publisher` | **/08发布师**：功德圆满，规范提交与 GitHub 发布 | [SKILL.md](./publisher/SKILL.md) | — |

---

### 开发与代码质量

架构、规范、测试、安全、数据库等。

| Skill | 用途 | 入口 | GitHub |
|-------|------|------|--------|
| `backend-patterns` | Node/Express/Next.js API 后端架构与最佳实践 | [SKILL.md](./backend-patterns/SKILL.md) | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/tree/main/skills/backend-patterns) |
| `coding-standards` | TS/JS/React/Node 通用编码规范与模式 | [SKILL.md](./coding-standards/SKILL.md) | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/tree/main/skills/coding-standards) |
| `frontend-patterns` | React/Next.js 前端开发模式（状态、性能、UI） | [SKILL.md](./frontend-patterns/SKILL.md) | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/tree/main/skills/frontend-patterns) |
| `ddd` → `software-architecture` | 质量导向的软件架构与设计指导 | [SKILL.md](./ddd/skills/software-architecture/SKILL.md) | — |
| `security-review` | 安全审查清单（鉴权/输入/密钥/API/支付等） | [SKILL.md](./security-review/SKILL.md) | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/tree/main/skills/security-review) |
| `tdd-workflow` | 以 TDD 与覆盖率为核心的工程化流程 | [SKILL.md](./tdd-workflow/SKILL.md) | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/tree/main/skills/tdd-workflow) |
| `test-driven-development` | TDD 红-绿-重构流程（功能/修复/重构） | [SKILL.md](./test-driven-development/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/test-driven-development) |
| `testing-patterns` | Jest 测试模式（mock、factory、TDD 流程） | [SKILL.md](./testing-patterns/SKILL.md) | — |
| `eval-harness` | Eval 驱动开发（EDD）评估框架与模板 | [SKILL.md](./eval-harness/SKILL.md) | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/tree/main/skills/eval-harness) |
| `kaizen` | 迭代改进、根因分析、避免过度工程 | [SKILL.md](./kaizen/skills/kaizen/SKILL.md) | — |
| `strategic-compact` | 在关键阶段做“上下文压缩/整理”的策略 | [SKILL.md](./strategic-compact/SKILL.md) | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/tree/main/skills/strategic-compact) |
| `continuous-learning` | 从会话中提炼可复用模式并沉淀为技能 | [SKILL.md](./continuous-learning/SKILL.md) | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/tree/main/skills/continuous-learning) |
| `project-guidelines-example` | 项目级 Skill 模板示例（架构/目录/流程） | [SKILL.md](./project-guidelines-example/SKILL.md) | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/tree/main/skills/project-guidelines-example) |

---

### 前端与 UI

组件、表单、GraphQL、设计系统等。

| Skill | 用途 | 入口 | GitHub |
|-------|------|------|--------|
| `react-ui-patterns` | React UI 模式（loading/error/empty、数据获取） | [SKILL.md](./react-ui-patterns/SKILL.md) | — |
| `core-components` | 核心组件库/设计系统模式（tokens、组件用法） | [SKILL.md](./core-components/SKILL.md) | — |
| `formik-patterns` | Formik 表单结构/校验/提交模式 | [SKILL.md](./formik-patterns/SKILL.md) | — |
| `graphql-schema` | GraphQL 查询/变更/类型生成模式 | [SKILL.md](./graphql-schema/SKILL.md) | — |
| `frontend-design` | 前端 UI/页面的高品质设计与实现指导 | [SKILL.md](./frontend-design/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/frontend-design) |
| `ui-ux-pro-max` | UI/UX 设计智能（多风格/配色/字体/组件栈） | [SKILL.md](./ui-ux-pro-max-skill/skills/ui-ux-pro-max/SKILL.md) | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) |
| `web-artifacts-builder` | 构建复杂 HTML artifacts（React/Tailwind/shadcn/ui） | [SKILL.md](./web-artifacts-builder/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/web-artifacts-builder) |

---

### 文档与办公

Word、PDF、PPT、Excel、协作文档、内部沟通等。

| Skill | 用途 | 入口 | GitHub |
|-------|------|------|--------|
| `docx` | 创建/编辑/分析 Word（修订、批注、格式保留） | [SKILL.md](./docx/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/docx) |
| `pdf` | PDF 提取/生成/合并拆分/表单处理 | [SKILL.md](./pdf/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/pdf) |
| `pptx` | 创建/编辑 PPT（布局/备注/评论） | [SKILL.md](./pptx/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/pptx) |
| `xlsx` | 表格创建/分析/可视化（含公式） | [SKILL.md](./xlsx/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/xlsx) |
| `doc-coauthoring` | 结构化协作撰写技术文档/提案/规范 | [SKILL.md](./doc-coauthoring/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/doc-coauthoring) |
| `internal-comms` | 内部沟通文档模板（周报/通告/状态更新等） | [SKILL.md](./internal-comms/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/internal-comms) |

---

### 营销与增长

内容、获客、定位、竞品、国内平台等。

| Skill | 用途 | 入口 | GitHub |
|-------|------|------|--------|
| `content-creator` | SEO/品牌语气/内容框架的营销内容生成 | [SKILL.md](./content-creator/SKILL.md) | — |
| `marketing-demand-acquisition` | 多渠道获客与需求生成（含 CAC/渠道打法） | [SKILL.md](./marketing-demand-acquisition/SKILL.md) | — |
| `marketing-strategy-pmm` | PMM 定位/GTM/竞品情报与发布策略 | [SKILL.md](./marketing-strategy-pmm/SKILL.md) | — |
| `china-viral-content-analyzer` | 国内平台爆款内容拆解（小红书/抖音/B站等） | [SKILL.md](./china-viral-content-analyzer/SKILL.md) | — |
| `client-finder-pro` | 面向中国市场的客户线索搜索与整理（可导出 CRM CSV） | [SKILL.md](./client-finder-pro/SKILL.md) | — |
| `user-persona-extractor` | 关键词用户画像提取（多数据源聚合+可视化报告） | [SKILL.md](./user-persona-extractor/SKILL.md) | — |
| `comment-analyzer` | 国内平台评论分析（情绪/观点/画像/高频话题） | [SKILL.md](./comment-analyzer/SKILL.md) | — |

---

### 科学研究 (Scientific)

由 K-Dense AI 提供的 140+ 项专业科学研究技能。

| Skill | 用途 | 入口 | GitHub |
|-------|------|------|--------|
| `pubmed-database` | PubMed 文献检索与 API 调用（生物医学） | [SKILL.md](../plugins/cache/claude-scientific-skills/scientific-skills/1.0.0/pubmed-database/SKILL.md) | [K-Dense-AI/claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills) |
| `rdkit` |  cheminformatics 与分子建模工具 | [SKILL.md](../plugins/cache/claude-scientific-skills/scientific-skills/1.0.0/rdkit/SKILL.md) | [K-Dense-AI/claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills) |
| `scanpy` | 单细胞 RNA 测序数据分析 | [SKILL.md](../plugins/cache/claude-scientific-skills/scientific-skills/1.0.0/scanpy/SKILL.md) | [K-Dense-AI/claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills) |
| `chembl-database` | ChEMBL 药物化学数据库访问 | [SKILL.md](../plugins/cache/claude-scientific-skills/scientific-skills/1.0.0/chembl-database/SKILL.md) | [K-Dense-AI/claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills) |
| `astropy` | 天文学计算与数据处理 | [SKILL.md](../plugins/cache/claude-scientific-skills/scientific-skills/1.0.0/astropy/SKILL.md) | [K-Dense-AI/claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills) |
| `scientific-writing` | 科学论文撰写、润色与格式化指导 | [SKILL.md](../plugins/cache/claude-scientific-skills/scientific-skills/1.0.0/scientific-writing/SKILL.md) | [K-Dense-AI/claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills) |
| `... (140+ total)` | 涵盖生物、化学、物理、临床医学等全领域 | [目录](../plugins/cache/claude-scientific-skills/scientific-skills/1.0.0/) | [K-Dense-AI/claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills) |

---

### 设计与视觉

品牌、排版、艺术、Obsidian、主题、动图等。

| Skill | 用途 | 入口 | GitHub |
|-------|------|------|--------|
| `algorithmic-art` | p5.js 算法/生成艺术（可控随机种子、交互参数） | [SKILL.md](./algorithmic-art/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/algorithmic-art) |
| `brand-guidelines` | 应用 Anthropic 品牌色与排版规范 | [SKILL.md](./brand-guidelines/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/brand-guidelines) |
| `canvas-design` | 生成原创静态视觉设计（.png/.pdf） | [SKILL.md](./canvas-design/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/canvas-design) |
| `magazine-layout` | 将文章排版为杂志风格 HTML（多风格、可导出 PDF） | [SKILL.md](./magazine-layout/SKILL.md) | — |
| `theme-factory` | 为 artifacts/报告/页面快速套用主题体系 | [SKILL.md](./theme-factory/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/theme-factory) |
| `web-asset-generator` | 生成 favicon/app icon/OG 图等 Web 资产 | [SKILL.md](./web-asset-generator/SKILL.md) | — |
| `slack-gif-creator` | 为 Slack 生成/优化动画 GIF | [SKILL.md](./slack-gif-creator/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/slack-gif-creator) |
| `obsidian-markdown` | Obsidian Markdown（wikilink、callout、frontmatter 等） | [SKILL.md](./obsidian-markdown/SKILL.md) | — |
| `obsidian-bases` | 创建/编辑 Obsidian Bases（筛选/视图/公式/汇总） | [SKILL.md](./obsidian-bases/SKILL.md) | — |
| `json-canvas` | 创建/编辑 Obsidian .canvas（节点/连线/分组） | [SKILL.md](./json-canvas/SKILL.md) | — |

---

### 浏览器 / 自动化与媒体

自动化、测试、视频下载等。

| Skill | 用途 | 入口 | GitHub |
|-------|------|------|--------|
| `playwright-skill` | Playwright 自动化测试（截图/表单/响应式/UX 校验） | [SKILL.md](./playwright-skill/SKILL.md) | [lackeyjb/playwright-skill](https://github.com/lackeyjb/playwright-skill) |
| `webapp-testing` | Web 应用测试工具箱（偏本地/交互验证） | [SKILL.md](./webapp-testing/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) |
| `dev-browser` | 持久化页面状态的浏览器自动化（偏开发/调试/采集） | [SKILL.md](./dev-browser/skills/dev-browser/SKILL.md) | [sawyerhood/dev-browser](https://github.com/sawyerhood/dev-browser) |
| `video-downloader` | 用 yt-dlp 下载/抽音频/排错 | [SKILL.md](./video-downloader/SKILL.md) | — |

---

### 工具与集成

MCP、tmux、NotebookLM、Z-Library 等。

| Skill | 用途 | 入口 | GitHub |
|-------|------|------|--------|
| `mcp-builder` | 构建高质量 MCP Server（Python/TS）的方法论与清单 | [SKILL.md](./mcp-builder/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/mcp-builder) |
| `mcp-cli` | 通过 CLI 按需使用 MCP（避免提前注入大量上下文） | [SKILL.md](./mcp-cli/SKILL.md) | — |
| `using-tmux-for-interactive-commands` | 用 tmux 驾驭交互式命令（vim/REPL/rebase 等） | [SKILL.md](./using-tmux-for-interactive-commands/SKILL.md) | — |
| `notebooklm` | 通过 NotebookLM 做“来源可追溯”的文档问答 | [SKILL.md](./notebooklm-skill/SKILL.md) | [PleasePrompto/notebooklm-skill](https://github.com/PleasePrompto/notebooklm-skill) |
| `zlibrary-to-notebooklm` | Z-Library → NotebookLM 自动下载/转换/上传 | [SKILL.md](./zlibrary-to-notebooklm/SKILL.md) | [zstmfhy/zlibrary-to-notebooklm](https://github.com/zstmfhy/zlibrary-to-notebooklm) |

---

### 写作与技能建设

自媒体写作、自定义 Skill 编写等。

| Skill | 用途 | 入口 | GitHub |
|-------|------|------|--------|
| `writing-assistant` | 自媒体写作全流程（选题→大纲→正文→标题→排版） | [SKILL.md](./writing-assistant-skill-main/SKILL.md) | — |
| `writing-skills` | 编写/测试/发布自定义 Skill 的指南 | [SKILL.md](./writing-skills/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/writing-skills) |

---

### 其他

| Skill | 用途 | 入口 | GitHub |
|-------|------|------|--------|
| `peers-advisory-group` | 私董会流程（多角色提问与可执行建议） | [SKILL.md](./peers-advisory-group/SKILL.md) | — |
| `clickhouse-io` | ClickHouse 查询/建模/性能优化模式 | [SKILL.md](./clickhouse-io/SKILL.md) | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/tree/main/skills/clickhouse-io) |

---

## 常见任务 → 推荐技能组合

- **做新功能（通用）**  
  `brainstorming` → `writing-plans` → `tdd-workflow`（或 `test-driven-development`）→ `requesting-code-review` → `verification-before-completion`（或 `verification-loop`）

- **修 Bug / 查线上问题**  
  `systematic-debugging` →（必要时 `security-review`）→ `test-driven-development` → `verification-before-completion`

- **React/前端页面开发**  
  `frontend-patterns` + `react-ui-patterns` + `core-components`（表单再加 `formik-patterns`）

- **GraphQL 相关**  
  `graphql-schema`（配合 `react-ui-patterns` 做 loading/error/empty）

- **浏览器自动化 / Web 测试**  
  `playwright-skill`（偏 E2E）/ `webapp-testing`（偏本地验证）/ `dev-browser`（偏调试采集）

- **做 PPT/Word/Excel/PDF**  
  `pptx` / `docx` / `xlsx` / `pdf`

- **Obsidian 知识库与可视化**  
  `obsidian-markdown` + `obsidian-bases` + `json-canvas`

- **营销增长/策略**  
  `content-creator` + `marketing-demand-acquisition` + `marketing-strategy-pmm`（国内内容再加 `china-viral-content-analyzer`）

- **获取线索/做画像/分析评论**  
  `client-finder-pro` / `user-persona-extractor` / `comment-analyzer`

- **UI/视觉资产**  
  `ui-ux-pro-max`、`frontend-design`、`brand-guidelines`、`canvas-design`、`web-asset-generator`、`magazine-layout`

---

## 按名称速查

Ctrl+F 搜索 skill 名称即可定位。入口为相对 `skills/` 的路径；**GitHub** 为上游仓库链接（— 表示暂无）。

| Skill | 分类 | 入口 | GitHub |
|-------|------|------|--------|
| `architect` | 编程宗师 | [architect/SKILL.md](./architect/SKILL.md) | — |
| `backend-patterns` | 开发与代码质量 | [backend-patterns/SKILL.md](./backend-patterns/SKILL.md) | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/tree/main/skills/backend-patterns) |
| `brainstorming` | 过程型 | [brainstorming/SKILL.md](./brainstorming/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/brainstorming) |
| `brand-guidelines` | 设计与视觉 | [brand-guidelines/SKILL.md](./brand-guidelines/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/brand-guidelines) |
| `builder` | 编程宗师 | [builder/SKILL.md](./builder/SKILL.md) | — |
| `canvas-design` | 设计与视觉 | [canvas-design/SKILL.md](./canvas-design/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/canvas-design) |
| `china-viral-content-analyzer` | 营销与增长 | [china-viral-content-analyzer/SKILL.md](./china-viral-content-analyzer/SKILL.md) | — |
| `clickhouse-io` | 其他 | [clickhouse-io/SKILL.md](./clickhouse-io/SKILL.md) | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/tree/main/skills/clickhouse-io) |
| `client-finder-pro` | 营销与增长 | [client-finder-pro/SKILL.md](./client-finder-pro/SKILL.md) | — |
| `code-reviewer` | 编程宗师 | [code-reviewer/SKILL.md](./code-reviewer/SKILL.md) | — |
| `coding-standards` | 开发与代码质量 | [coding-standards/SKILL.md](./coding-standards/SKILL.md) | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/tree/main/skills/coding-standards) |
| `comment-analyzer` | 营销与增长 | [comment-analyzer/SKILL.md](./comment-analyzer/SKILL.md) | — |
| `content-creator` | 营销与增长 | [content-creator/SKILL.md](./content-creator/SKILL.md) | — |
| `continuous-learning` | 开发与代码质量 | [continuous-learning/SKILL.md](./continuous-learning/SKILL.md) | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/tree/main/skills/continuous-learning) |
| `core-components` | 前端与 UI | [core-components/SKILL.md](./core-components/SKILL.md) | — |
| `dev-browser` | 浏览器/自动化 | [dev-browser/skills/dev-browser/SKILL.md](./dev-browser/skills/dev-browser/SKILL.md) | [sawyerhood/dev-browser](https://github.com/sawyerhood/dev-browser) |
| `dispatching-parallel-agents` | 过程型 | [dispatching-parallel-agents/SKILL.md](./dispatching-parallel-agents/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/dispatching-parallel-agents) |
| `doc-coauthoring` | 文档与办公 | [doc-coauthoring/SKILL.md](./doc-coauthoring/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/doc-coauthoring) |
| `docx` | 文档与办公 | [docx/SKILL.md](./docx/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/docx) |
| `ddd` / `software-architecture` | 开发与代码质量 | [ddd/skills/software-architecture/SKILL.md](./ddd/skills/software-architecture/SKILL.md) | — |
| `eval-harness` | 开发与代码质量 | [eval-harness/SKILL.md](./eval-harness/SKILL.md) | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/tree/main/skills/eval-harness) |
| `executing-plans` | 过程型 | [executing-plans/SKILL.md](./executing-plans/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/executing-plans) |
| `finishing-a-development-branch` | 过程型 | [finishing-a-development-branch/SKILL.md](./finishing-a-development-branch/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/finishing-a-development-branch) |
| `formik-patterns` | 前端与 UI | [formik-patterns/SKILL.md](./formik-patterns/SKILL.md) | — |
| `frontend-design` | 前端与 UI | [frontend-design/SKILL.md](./frontend-design/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/frontend-design) |
| `frontend-patterns` | 开发与代码质量 | [frontend-patterns/SKILL.md](./frontend-patterns/SKILL.md) | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/tree/main/skills/frontend-patterns) |
| `graphql-schema` | 前端与 UI | [graphql-schema/SKILL.md](./graphql-schema/SKILL.md) | — |
| `internal-comms` | 文档与办公 | [internal-comms/SKILL.md](./internal-comms/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/internal-comms) |
| `investigator` | 编程宗师 | [investigator/SKILL.md](./investigator/SKILL.md) | — |
| `json-canvas` | 设计与视觉 | [json-canvas/SKILL.md](./json-canvas/SKILL.md) | — |
| `kaizen` | 开发与代码质量 | [kaizen/skills/kaizen/SKILL.md](./kaizen/skills/kaizen/SKILL.md) | — |
| `magazine-layout` | 设计与视觉 | [magazine-layout/SKILL.md](./magazine-layout/SKILL.md) | — |
| `marketing-demand-acquisition` | 营销与增长 | [marketing-demand-acquisition/SKILL.md](./marketing-demand-acquisition/SKILL.md) | — |
| `marketing-strategy-pmm` | 营销与增长 | [marketing-strategy-pmm/SKILL.md](./marketing-strategy-pmm/SKILL.md) | — |
| `mcp-builder` | 工具与集成 | [mcp-builder/SKILL.md](./mcp-builder/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/mcp-builder) |
| `mcp-cli` | 工具与集成 | [mcp-cli/SKILL.md](./mcp-cli/SKILL.md) | — |
| `notebooklm` | 工具与集成 | [notebooklm-skill/SKILL.md](./notebooklm-skill/SKILL.md) | [PleasePrompto/notebooklm-skill](https://github.com/PleasePrompto/notebooklm-skill) |
| `obsidian-bases` | 设计与视觉 | [obsidian-bases/SKILL.md](./obsidian-bases/SKILL.md) | — |
| `obsidian-markdown` | 设计与视觉 | [obsidian-markdown/SKILL.md](./obsidian-markdown/SKILL.md) | — |
| `pdf` | 文档与办公 | [pdf/SKILL.md](./pdf/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/pdf) |
| `peers-advisory-group` | 其他 | [peers-advisory-group/SKILL.md](./peers-advisory-group/SKILL.md) | — |
| `playwright-skill` | 浏览器/自动化 | [playwright-skill/SKILL.md](./playwright-skill/SKILL.md) | [lackeyjb/playwright-skill](https://github.com/lackeyjb/playwright-skill) |
| `publisher` | 编程宗师 | [publisher/SKILL.md](./publisher/SKILL.md) | — |
| `pptx` | 文档与办公 | [pptx/SKILL.md](./pptx/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/pptx) |
| `project-guidelines-example` | 开发与代码质量 | [project-guidelines-example/SKILL.md](./project-guidelines-example/SKILL.md) | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/tree/main/skills/project-guidelines-example) |
| `react-ui-patterns` | 前端与 UI | [react-ui-patterns/SKILL.md](./react-ui-patterns/SKILL.md) | — |
| `receiving-code-review` | 过程型 | [receiving-code-review/SKILL.md](./receiving-code-review/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/receiving-code-review) |
| `scribe` | 编程宗师 | [scribe/SKILL.md](./scribe/SKILL.md) | — |
| `requesting-code-review` | 过程型 | [requesting-code-review/SKILL.md](./requesting-code-review/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/requesting-code-review) |
| `security-review` | 开发与代码质量 | [security-review/SKILL.md](./security-review/SKILL.md) | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/tree/main/skills/security-review) |
| `security-reviewer` | 编程宗师 | [security-reviewer/SKILL.md](./security-reviewer/SKILL.md) | — |
| `slack-gif-creator` | 设计与视觉 | [slack-gif-creator/SKILL.md](./slack-gif-creator/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/slack-gif-creator) |
| `strategic-compact` | 开发与代码质量 | [strategic-compact/SKILL.md](./strategic-compact/SKILL.md) | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/tree/main/skills/strategic-compact) |
| `subagent-driven-development` | 过程型 | [subagent-driven-development/SKILL.md](./subagent-driven-development/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/subagent-driven-development) |
| `systematic-debugging` | 过程型 | [systematic-debugging/SKILL.md](./systematic-debugging/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/systematic-debugging) |
| `tdd-workflow` | 开发与代码质量 | [tdd-workflow/SKILL.md](./tdd-workflow/SKILL.md) | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/tree/main/skills/tdd-workflow) |
| `test-driven-development` | 开发与代码质量 | [test-driven-development/SKILL.md](./test-driven-development/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/test-driven-development) |
| `testing-patterns` | 开发与代码质量 | [testing-patterns/SKILL.md](./testing-patterns/SKILL.md) | — |
| `theme-factory` | 设计与视觉 | [theme-factory/SKILL.md](./theme-factory/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/theme-factory) |
| `ui-ux-pro-max` | 前端与 UI | [ui-ux-pro-max-skill/skills/ui-ux-pro-max/SKILL.md](./ui-ux-pro-max-skill/skills/ui-ux-pro-max/SKILL.md) | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) |
| `using-git-worktrees` | 过程型 | [using-git-worktrees/SKILL.md](./using-git-worktrees/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/using-git-worktrees) |
| `using-superpowers` | 过程型 | [using-superpowers/SKILL.md](./using-superpowers/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/using-superpowers) |
| `using-tmux-for-interactive-commands` | 工具与集成 | [using-tmux-for-interactive-commands/SKILL.md](./using-tmux-for-interactive-commands/SKILL.md) | — |
| `validator` | 编程宗师 | [validator/SKILL.md](./validator/SKILL.md) | — |
| `user-persona-extractor` | 营销与增长 | [user-persona-extractor/SKILL.md](./user-persona-extractor/SKILL.md) | — |
| `verification-before-completion` | 过程型 | [verification-before-completion/SKILL.md](./verification-before-completion/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/verification-before-completion) |
| `verification-loop` | 过程型 | [verification-loop/SKILL.md](./verification-loop/SKILL.md) | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/tree/main/skills/verification-loop) |
| `video-downloader` | 浏览器/自动化 | [video-downloader/SKILL.md](./video-downloader/SKILL.md) | — |
| `web-asset-generator` | 设计与视觉 | [web-asset-generator/SKILL.md](./web-asset-generator/SKILL.md) | — |
| `web-artifacts-builder` | 前端与 UI | [web-artifacts-builder/SKILL.md](./web-artifacts-builder/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/web-artifacts-builder) |
| `webapp-testing` | 浏览器/自动化 | [webapp-testing/SKILL.md](./webapp-testing/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) |
| `writing-assistant` | 写作与技能建设 | [writing-assistant-skill-main/SKILL.md](./writing-assistant-skill-main/SKILL.md) | — |
| `writing-plans` | 过程型 | [writing-plans/SKILL.md](./writing-plans/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/writing-plans) |
| `writing-skills` | 写作与技能建设 | [writing-skills/SKILL.md](./writing-skills/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/writing-skills) |
| `xlsx` | 文档与办公 | [xlsx/SKILL.md](./xlsx/SKILL.md) | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/xlsx) |
| `zlibrary-to-notebooklm` | 工具与集成 | [zlibrary-to-notebooklm/SKILL.md](./zlibrary-to-notebooklm/SKILL.md) | [zstmfhy/zlibrary-to-notebooklm](https://github.com/zstmfhy/zlibrary-to-notebooklm) |

---

## 维护建议（避免索引漂移）

- **以 `SKILL.md` 为准**：目录里有 README 但无 `SKILL.md` 的不纳入索引。
- **同名多份**：多为镜像/多平台导出，优先用更靠近根目录、语义更完整的那份。
- **新增 Skill**：新建 `skills/<skill-name>/SKILL.md`（含 name/description frontmatter），在对应分类表与「按名称速查」各加一行并链到入口。
- **GitHub 链接**：优先链到该 skill 所在上游仓库的 `tree/main/skills/<name>`（或等价路径）；若为本地/自定义且无公开仓库则填 `—`。发现新来源时请同步更新分类表与速查表。
