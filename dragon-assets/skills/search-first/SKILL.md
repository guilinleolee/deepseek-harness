---
license: UNKNOWN
name: search-first
description: Research-before-coding workflow. Search for existing tools, libraries, and patterns before writing custom code. Invokes the researcher agent.
github_repo: affaan-m/everything-claude-code
github_hash: 4e66b2882da9afb9747468b08a253ca2f09c85f3
last_updated: 2026-04-25
source_type: derived
origin: ECC (everything-claude-code)
triggers: ["search first", "Search First — 研究优先于编码"]
---

# Search First — 研究优先于编码

> 来源: [affaan-m/everything-claude-code/skills/search-first](https://github.com/affaan-m/everything-claude-code)

## 功能概述

"研究已有解决方案再实现"工作流的系统化方法。在编写自定义代码前搜索现有工具、库和模式。

## 工作流

```
┌─────────────────────────────────────────────┐
│  1. NEED ANALYSIS                           │
│     定义需要什么功能                          │
│     识别语言/框架约束                        │
├─────────────────────────────────────────────┤
│  2. PARALLEL SEARCH (researcher agent)      │
│     ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│     │  npm /   │ │  MCP /   │ │  GitHub / │ │
│     │  PyPI    │ │  Skills  │ │  Web      │ │
│     └──────────┘ └──────────┘ └──────────┘ │
├─────────────────────────────────────────────┤
│  3. EVALUATE                                │
│     评分候选方案（功能、维护、社区、文档）    │
├─────────────────────────────────────────────┤
│  4. DECIDE                                  │
│     ┌─────────┐  ┌──────────┐  ┌─────────┐ │
│     │  Adopt  │  │  Extend  │  │  Build  │ │
│     │ as-is   │  │  /Wrap   │  │  Custom │ │
│     └─────────┘  └──────────┘  └─────────┘ │
├─────────────────────────────────────────────┤
│  5. IMPLEMENT                               │
│     安装包 / 配置MCP / 编写最小自定义代码   │
└─────────────────────────────────────────────┘
```

## 决策矩阵

| 信号 | 行动 |
|------|------|
| 完全匹配，维护良好，MIT/Apache许可 | **Adopt** — 直接安装使用 |
| 部分匹配，基础良好 | **Extend** — 安装 + 写薄包装 |
| 多个弱匹配 | **Compose** — 组合2-3个小包 |
| 未找到合适方案 | **Build** — 编写自定义，但基于研究 |

## 快速模式（内联）

在编写工具或添加功能前，心理运行：

0. 仓库中已存在？→ 在相关模块/测试中`rg`搜索
1. 这是常见问题？→ 搜索npm/PyPI
2. 有MCP可用？→ 检查`~/.claude/settings.json`
3. 有Skill可用？→ 检查`~/.claude/skills/`
4. 有GitHub实现/模板？→ 运行GitHub代码搜索，在写新代码前找到维护的OSS

## 完整模式（Agent）

对于非平凡功能，启动调研Agent：

```
Task(subagent_type="general-purpose", prompt="
  Research existing tools for: [DESCRIPTION]
  Language/framework: [LANG]
  Constraints: [ANY]

  Search: npm/PyPI, MCP servers, Claude Code skills, GitHub
  Return: Structured comparison with recommendation
")
```

## 按类别搜索快捷方式

### 开发工具

| 需求 | 方案 |
|------|------|
| Linting | `eslint`, `ruff`, `textlint`, `markdownlint` |
| 格式化 | `prettier`, `black`, `gofmt` |
| 测试 | `jest`, `pytest`, `go test` |
| Pre-commit | `husky`, `lint-staged`, `pre-commit` |

### AI/LLM集成

| 需求 | 方案 |
|------|------|
| Claude SDK | Context7获取最新文档 |
| 提示管理 | 检查MCP服务器 |
| 文档处理 | `unstructured`, `pdfplumber`, `mammoth` |

### 数据与API

| 需求 | 方案 |
|------|------|
| HTTP客户端 | `httpx`(Python), `ky`/`got`(Node) |
| 验证 | `zod`(TS), `pydantic`(Python) |
| 数据库 | 先检查MCP服务器 |

### 内容发布

| 需求 | 方案 |
|------|------|
| Markdown处理 | `remark`, `unified`, `markdown-it` |
| 图片优化 | `sharp`, `imagemin` |

## 集成点

### 与规划师Agent

规划师应在Phase 1(架构审查)前调用调研：
- 调研Agent识别可用工具
- 规划师将其纳入实施计划
- 在计划中避免"重复造轮子"

### 与架构师Agent

架构师应咨询调研：
- 技术栈决策
- 集成模式发现
- 现有参考架构

## 示例

### 示例1: "添加死链检查"

```
Need: 检查markdown文件中的死链
Search: npm "markdown dead link checker"
Found: textlint-rule-no-dead-link (score: 9/10)
Action: ADOPT — npm install textlint-rule-no-dead-link
Result: 零自定义代码，经过实战验证的方案
```

### 示例2: "添加HTTP客户端包装"

```
Need: 带重试和超时处理的弹性HTTP客户端
Search: npm "http client retry", PyPI "httpx retry"
Found: got (Node) + retry插件, httpx (Python) 内置retry
Action: ADOPT — 直接使用got/httpx配置retry
Result: 零自定义代码，生产验证的库
```

### 示例3: "添加配置文件检查器"

```
Need: 根据schema验证项目配置文件
Search: npm "config linter schema"
Found: ajv-cli (score: 8/10)
Action: ADOPT + EXTEND — 安装ajv-cli，写项目特定schema
Result: 1包 + 1 schema文件，无自定义验证逻辑
```

## 反模式

- **跳到代码**: 在检查是否存在前编写工具
- **忽略MCP**: 不检查MCP服务器是否已提供该功能
- **过度定制**: 包装库过于厚重，失去其优势
- **依赖膨胀**: 为一个小功能安装大包

## 天龙引擎集成

### 适用岗位

| 岗位 | 集成方式 | 增强能力 |
|------|---------|---------|
| **01调研师** | 研究工作流 | 5步研究 + 决策矩阵 |
| **02架构师** | 技术栈决策 | 工具发现 + 模式搜索 |
| **03构建师** | 依赖选择 | npm/PyPI搜索 |

### 天龙引擎增强

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎 Search First体系                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   5步研究流程:                                              │
│   ├── 1.需求分析 → 定义功能 + 约束                       │
│   ├── 2.并行搜索 → npm/PyPI/MCP/GitHub                   │
│   ├── 3.评估 → 评分候选方案                              │
│   ├── 4.决策 → Adopt/Extend/Compose/Build               │
│   └── 5.实现 → 安装 + 最小化自定义                       │
│                                                             │
│   协同技能:                                                 │
│   ├── /deep-research      → 深度调研                      │
│   ├── /enterprise-docs-search → 企业文档搜索             │
│   └── /agent-reach       → 14平台数据采集                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 核心命令

```bash
# 研究优先
[@调研师] 研究这个功能的现有解决方案
[@架构师] 在选择技术栈前搜索已有工具

# 快速检查
[@构建师] 检查npm/PyPI是否有这个库
[@构建师] 搜索MCP服务器是否已提供此功能

# 决策
[@调研师] 评估这些候选方案并给出建议
[@架构师] 根据调研选择Adopt/Extend/Build
```

---

**版本**: V1.0 | **兼容性**: 天龙引擎 V8.68+ | **来源**: ECC
