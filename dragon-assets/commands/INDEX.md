# commands/ INDEX · 天龙引擎命令分类索引

> **版本**: V1.2 · **生成日期**: 2026-08-19 · **共 132 条命令**

> **分类法**：按业务用途分组，与 `agents/AGENT_INDEX.md` 十进制分类对齐。
> 核心九部（00-07 师级）与 agents/ 同步；其余按用途聚类。

---

## 0. 使用方式

commands/ 下的 .md 文件作为 Claude Code 的 slash commands 使用，
通过 `/<name>` 调用（去掉 .md 后缀）。

例如 `commands/check.md` → 输入 `/check` 调用。

---

## 0. 核心九部 (与 agents/ 同步) (8 个)

> **对齐说明**：agents/ 用英文 kebab-case (`00-investigator.md`)，commands/ 用中文 (`00调研师.md`)。
> 角色翻译以 `agents/AGENT_INDEX.md` 为准 (构建师 / 安全员)。
> "对应 agents/" 列建立双向索引（2026-08-05 修复）。

| 命令 | 对应 agents/ | 描述 |
|------|-------------|------|
| `/00调研师` | `agents/01-investigator.md` | 考古摸底：在开工前查清现有代码逻辑、依赖和技术坑点。Invoke the investigator agent. |
| `/01架构师` | `agents/02-architect.md` | 01架构师 (Architect)。划定蓝图：将模糊需求拆解为原子化的 MULTI_AGENT_PLAN.md。Invoke the 01architec... |
| `/02建模师` | `agents/03-builder.md` | 02构建师 (Builder)。代码施工：根据蓝图编写高质量、防御性的生产级代码。Invoke the 02builder agent. |
| `/03验证师` | `agents/04-validator.md` | 03验证师 (Validator)。极端找茬：跑压力测试，不让一个 Bug 溜走。Invoke the 03validator agent. |
| `/04安全师` | `agents/05-security-reviewer.md` | 04安全员 (Security-Master)。专项排雷：检查 SQL 注入、秘钥泄露等安全漏洞。Invoke the 04security-review... |
| `/05审查师` | `agents/06-code-reviewer.md` | 05审查师 (Reviewer)。终极审计：检查安全、性能与代码美感。Invoke the 05code-reviewer agent. |
| `/06记录师` | `agents/07-scribe.md` | 06记录师 (Scribe)。文明传承：自动编写 API 文档、README 和高质量代码注释。Invoke the 06scribe agent. |
| `/07发布师` | `agents/08-publisher.md` | 07发布师 (Publisher)。功德圆满：规范提交 Git，发布到 GitHub。Invoke the 07publisher agent. |

## 1. 工作流 / 编排 (8 个)

| 命令 | 描述 |
|------|------|
| `/nine-dragons-check` | 九部天龙健康检查 - 检测agents/skills/commands配置完整性并提供修复建议 |
| `/nine-dragons-cost-opt` | 九部天龙成本优化模式 - 混合模型策略节省47%成本 |
| `/nine-dragons-help` | 九部天龙智能助手 - 自动判断任务场景并推荐最优执行路径 |
| `/nine-dragons-plan-status` | "查看九部天龙任务进度 - 阶段状态、成本统计、错误追踪" |
| `/nine-dragons-plan` | "九部天龙任务规划 - 智能判断任务场景并创建3文件持久化计划" |
| `/nine-dragons-ui2code` | 九部天龙UI转代码 - 设计稿直接生成前端代码（三引擎联动） |
| `/orchestrate` |  |
| `/plan` | Restate requirements, assess risks, and create step-by-step implementation pl... |

## 2. 工具 / 检查 (12 个)

| 命令 | 描述 |
|------|------|
| `/check` | 质量检查 - 快速质量检查命令 |
| `/checkpoint` | Claude Code会话快照与回滚管理 - 保存/恢复/对比会话状态 |
| `/critical-check` |  |
| `/critical-evidence` |  |
| `/dbs-action` |  |
| `/dbs-benchmark` |  |
| `/dbs-diagnosis` |  |
| `/opf-audit` |  |
| `/opf-scan` |  |
| `/opf-verify` |  |
| `/shibazi-check` | 十八子写作验收标准检查命令。自动检查文章是否满足预定义的验收标准。 |
| `/verify` |  |

## 3. 构建 / 部署 (15 个)

| 命令 | 描述 |
|------|------|
| `/build-fix` |  |
| `/commit-push-pr` | Commit, push, and open a PR |
| `/deploy` | 部署到生产环境 |
| `/dev-build` | 开发构建 - 项目编译打包流程 |
| `/dev-setup` | 开发环境配置 - 项目初始化和环境搭建 |
| `/dev-test` | 开发测试 - TDD开发流程中的测试编写和运行 |
| `/opf-pre` |  |
| `/pr-review` | Review a pull request using project standards |
| `/pr-summary` | Generate a summary for the current branch changes |
| `/profile` | 性能分析 - 定位性能瓶颈和优化机会 |
| `/prompt-master` |  |
| `/release` |  |
| `/shibazi-prd` | 十八子写作 PRD 管理命令。用于初始化内容计划、添加写作任务、查看进度状态。 |
| `/shibazi-publish` | 十八子写作发布自动化命令。一键发布到多个平台（掘金、微信公众号、知乎）。 |
| `/xiaohongshu-publish` | 将文章发布到小红书（小红书适配器） |

## 4. 文档 / 写作 (7 个)

| 命令 | 描述 |
|------|------|
| `/bidding-doc` |  |
| `/docs-sync` | Check if documentation is in sync with code |
| `/shibazi-draft` | 十八子写作 Git 草稿管理命令。用于创建草稿、记录里程碑、查看演化历史。 |
| `/update-docs` |  |
| `/write-integration-test` | 集成测试编写 - 测试模块间交互和API端点 |
| `/write-unit-test` | 单元测试编写 - 为函数和方法编写单元测试 |
| `/write` | 内容创作 - 启动完整内容创作流程 |

## 5. 客户 / 商业 (2 个)

| 命令 | 描述 |
|------|------|
| `/find-clients` | 搜索客户信息并自动保存CSV，支持国产CRM导入 |
| `/onboard` |  |

## 7. 数据 / 分析 (4 个)

| 命令 | 描述 |
|------|------|
| `/benchmark` | 性能基准测试 - 测量关键代码路径性能 |
| `/eval` |  |
| `/gpt-researcher` |  |
| `/math-viz` | 数学可视化CLI - plot/explain/flowchart/animate/interactive数学概念可视化 |

## 8. 设计 / 视觉 (4 个)

| 命令 | 描述 |
|------|------|
| `/design-pattern` | 设计模式选择 - 根据场景推荐合适的代码架构模式 |
| `/diagram` |  |
| `/quiz-generator` | Quiz Generator CLI - generate/interactive/export/templates/display智能测验生成 |
| `/system-design` | 系统设计 - 针对具体系统问题的专项设计 |

## 9. 学习 / 教学 (5 个)

| 命令 | 描述 |
|------|------|
| `/deeptutor` | DeepTutor CLI - chat/deep_solve/quiz/deep_research/math学习辅导桥接 |
| `/interview` | Interview to flesh out a plan/spec |
| `/langflow` |  |
| `/learn` |  |
| `/learned-skills` | 列出所有已学习的技能，支持筛选和排序 |

## 6. SEO / 数字营销 (14 个) ⭐ 2026-08-19

| 命令 | 描述 |
|------|------|
| `/seo-orchestrator` | SEO编排器 - 根据需求智能路由到最合适的SEO专家Agent |
| `/seo-technical` | Technical SEO Audit - 技术SEO审计（爬行、索引、Core Web Vitals） |
| `/seo-content` | Content Quality & E-E-A-T Analysis - 内容质量与E-E-A-T分析 |
| `/seo-geo` | SEO-GEO: AI搜索引擎优化 - AI搜索优化、ChatGPT/Perplexity引用 |
| `/seo-local` | Local SEO Analysis - 本地SEO分析（Google商家档案、本地排名） |
| `/seo-schema` | Schema Markup Analysis - 结构化数据分析与生成 |
| `/seo-performance` | Performance SEO - 性能SEO分析（页面速度、Core Web Vitals） |
| `/seo-sitemap` | Sitemap Analysis - 站点地图分析 |
| `/seo-visual` | Visual SEO - 视觉SEO分析（图片优化、视觉搜索） |
| `/seo-keyword` | Keyword Research - 关键词研究与分析 |
| `/seo-competitor` | Competitor Analysis - 竞品SEO分析 |
| `/seo-link-building` | Link Building - 外链建设策略 |
| `/seo-monitor` | SEO Monitor - SEO监控与报告 |
| `/baoyu-seo` | 百度SEO - 面向中文搜索引擎的SEO策略、百度算法规避 |

## 6.5 MCP / 模型上下文协议 (1 个) ⭐ 2026-08-19 新增

| 命令 | 描述 |
|------|------|
| `/mcp` | MCP集成中心 - 按需调用各种MCP服务（GEO分析、地理编码、Schema生成） |

## A. 其他 (52 个)

| 命令 | 描述 |
|------|------|
| `/architect` | 架构设计主流程 - 从需求到架构方案的全流程 |
| `/beads` |  |
| `/booster` |  |
| `/code-quality` | Run code quality checks on a directory |
| `/code-review` |  |
| `/command` |  |
| `/commands-list` |  |
| `/debug` | 调试主流程 - 系统化问题定位和修复 |
| `/devils-advocate` |  |
| `/e2e` | Generate and run end-to-end tests with Playwright. Creates test journeys, run... |
| `/hash` |  |
| `/last30` |  |
| `/llamaindex-rag` | LlamaIndex RAG CLI - 知识库创建/检索/管理/同步Obsidian |
| `/lsp` |  |
| `/opf-etl` |  |
| `/opf-patterns` |  |
| `/opf-redact` |  |
| `/opf-report` |  |
| `/optimize-performance` | 性能优化 - 针对具体性能问题的优化实施 |
| `/refactor-clean` |  |
| `/refactor-code` | 代码重构 - 提升代码质量而不改变外部行为 |
| `/remember` |  |
| `/rollback` | 回滚 - 代码或部署的回退操作 |
| `/setup-pm` | Configure your preferred package manager (npm/pnpm/yarn/bun) |
| `/shibazi-agent` |  |
| `/shibazi-archive` | 十八子写作文章存档命令。自动分类、标签管理、版本控制、快速检索。 |
| `/shibazi-batch` | 十八子写作批量生成命令。一键生成多篇草稿，提高启动速度。 |
| `/shibazi-config` | 十八子写作配置系统 - 初始化、管理品牌声音、SEO、风格、平台配置 |
| `/shibazi-dashboard` | 十八子写作进度可视化仪表板命令。生成美观的进度报告和图表。 |
| `/shibazi-illustrate` | 十八子写作智能配图命令。为文章自动生成配图，支持掘金/知乎/公众号/小红书多平台尺寸。触发词：配图、插图、illustration。 |
| `/shibazi-layout` | 杂志排版 - 12种专业风格、智能分页CSS、排版优化、PDF导出 |
| `/shibazi-loop` | 十八子写作 Shibazi Loop 循环执行命令。自动循环执行待完成的写作任务。 |
| `/shibazi-qa` | 质量检查 - 检查清单评分、ABCD四维审稿、SEO评分 |
| `/shibazi-smart` | 十八子写作智能推荐命令。基于 AI 的写作助手，提供模板推荐和写作建议。 |
| `/shibazi-topic` | 选题分析 - 爆款分析、市场洼地检测、标题推荐 |
| `/shibazi-translate` | 十八子写作翻译管道命令。将中文内容自动翻译成英文，保留 Markdown 格式。 |
| `/skill-cleanup` | 清理过时、低质量或重复的技能 |
| `/skill-review` | 审查和优化已提取的技能，检查质量、更新版本、合并重复 |
| `/tdd` | Enforce test-driven development workflow. Scaffold interfaces, generate tests... |
| `/test-coverage` |  |
| `/test-viral` | 测试国内平台爆款内容分析 |
| `/ticket` | Work on a JIRA/Linear ticket end-to-end |
| `/token` |  |
| `/trace` | 调用链追踪 - 分析代码执行路径和依赖关系 |
| `/turix-desktop` |  |
| `/uc` | 【万能格式转换助手 /uc】集成了 Pandoc, FFmpeg, ImageMagick, Stirling-PDF, Calibre 和 MeshLa... |
| `/update-codemaps` |  |
| `/viral` | 分析国内平台爆款内容，提取爆款要素并生成报告 |
| `/分析师` | 分析国内平台爆款内容，提取爆款要素并生成报告 |
| `/万能格式转换助手` | 【万能格式转换助手】集成了 Pandoc, FFmpeg, ImageMagick, Stirling-PDF, Calibre 和 MeshLab 的全... |
| `/评论分析` | 分析热门内容的评论，提取情感倾向、高频话题、用户画像和关键观点 |
| `/标书` | 标书生成 - 招投标文档智能生成。根据招标信息生成投标书/标书文档。|

---

**总计**: 132 个命令，分类于 12 个业务类。

## 维护说明

1. 新增 command 后，跑 `python scripts/_gen_commands_index.py` 重新生成本文件
2. 分类规则见脚本顶部 `CATEGORIES` dict（基于命名启发式）
3. 命令描述取自各 .md frontmatter `description:` 字段；缺失则显示空

