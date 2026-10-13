---
license: UNKNOWN
triggers: ["geo content generator", "GEO Content Generator - 决策级GEO内容生成引擎"]
---
# GEO Content Generator - 决策级GEO内容生成引擎

## L0: 一句话描述 (≤15字)
决策级GEO内容生成，自动质量门控

## L1: 使用场景 (50-100字)
适用场景：AI搜索优化内容生成、Perplexity/ChatGPT引用友好型文章、决策驱动型深度内容、批量GEO内容生产。触发条件：需要生成面向AI搜索引擎优化的长文内容、需要提升内容引用率、需要批量生产GEO内容。

## L2: 详细文档

### 核心能力矩阵

```
┌─────────────────────────────────────────────────────────────┐
│                 GEO Content Generator 核心架构                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Input Layer (输入层)                                      │
│  ├── Dageno API  → Prompt机会发现                         │
│  ├── Manual Topic → 手动主题输入                           │
│  └── Backlog     → Fanout队列                             │
│                    ↓                                        │
│  Process Layer (处理层)                                     │
│  ├── Fanout Extraction → 真实Fanout提取                    │
│  ├── Citation Crawl   → 引用页面爬取                       │
│  ├── Brief Builder    → Editorial Brief构建                 │
│  └── Quality Gate     → 5层质量门控                       │
│                    ↓                                        │
│  Output Layer (输出层)                                      │
│  └── WordPress/Raw → 发布就绪内容                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5层质量门控系统

| 层级 | 门控名称 | 检查项 | 阈值 |
|------|---------|--------|------|
| **L1** | 事实核查 | 数据准确性、来源可靠性 | 100% |
| **L2** | 引用质量 | 来源权威性、引用格式 | >=5个权威来源 |
| **L3** | 结构化 | 段落长度134-167词、标题层级 | 100% |
| **L4** | 实体清晰度 | 核心实体识别、避免歧义 | >80% |
| **L5** | 人类可读性 | AI痕迹检测、流畅度 | <0.3 AI分数 |

### Output Quality Contract (输出质量合约)

每个GEO内容必须满足：

```markdown
## Output Quality Contract

### 必需要素
1. [not ideal when...] - 每个主要选项必须有排除边界
2. [default recommendation] - 必须有默认推荐层级
3. [comparison] - 至少一个正面竞争对比
4. [decision engine] - If X -> Choose Y 决策框架
5. [convergence] - 单句收敛块 "If You Only Remember One Thing"

### 量化标准
- 引用数量: >=5个（编辑+官方混合）
- 最低字数: >=1200词
- 段落长度: 134-167词
- AI痕迹分数: <0.3
```

### Editorial Brief 结构

```yaml
working_title: "工作标题"
reader_persona: "读者画像（具体决策者）"
article_angle: "文章独特角度"
decision_frame: "决策框架"
differentiation_targets: ["差异化目标列表"]
must_prove: ["必须证明的3个核心观点"]
must_include: ["必须包含的5个关键要素"]
must_avoid: ["必须避免的3个陷阱"]
recommended_outline:
  - heading: "H2标题"
    purpose: "章节目的"
    target_length: "目标字数"
```

### 命令速查

```bash
# 核心命令
/geo-generate "主题" --depth [brief|full|decision]
/geo-generate --from-backlog --limit 5
/geo-brief "主题" --output brief.json
/geo-crawl "URL" --pages 10
/geo-publish "content_id" --cms wordpress --mode draft

# 质量门控
/geo-quality-gate [content_id]
/geo-quality-report [task_id]

# Backlog管理
/geo-backlog list
/geo-backlog add "Fanout内容"
/geo-backlog select --priority P0
```

### 与天龙引擎协同

| 天龙组件 | 协同方式 |
|---------|---------|
| **V8.10 Marketing Skills Pro** | 156 Skills + GEO内容策略 |
| **35-04 GEO内容优化师** | 核心执行岗位 |
| **07记录师** | 知识内容GEO优化 |
| **28-01文案策划** | GEO友好型模板 |
| **research-to-wechat** | 研究→GEO内容→发布闭环 |

### 依赖配置

```bash
# 环境变量
export DAGENO_API_KEY="your-dageno-api-key"
export FIRECRAWL_API_KEY="your-firecrawl-api-key"  # 可选

# Python依赖
pip install requests>=2.31.0
```

### 文件结构

```
geo-content-generator/
├── SKILL.md                    # 本文件
├── scripts/
│   ├── geo_cli.py             # CLI入口
│   ├── dageno_client.py        # Dageno API客户端
│   ├── fanout_extractor.py    # Fanout提取器
│   ├── citation_crawl.py       # 引用爬取
│   ├── brief_builder.py        # Editorial Brief构建器
│   ├── quality_gate.py         # 5层质量门控
│   └── wordpress_publisher.py   # WordPress发布
├── prompts/
│   ├── brief-generation.md     # Brief生成提示词
│   ├── content-generation.md    # 内容生成提示词
│   └── quality-check.md        # 质量检查提示词
└── templates/
    ├── editorial-brief-template.yaml
    └── output-contract-template.md
```

---

### MCP集成（V2.0新增）

#### MCP服务调用

本技能已集成天龙引擎MCP中心，可按需调用远程MCP服务。

##### MCP命令速查

```bash
# 内容采集（Firecrawl MCP）
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/mcp_remote.py" firecrawl scrape --url https://example.com/article

# 批量采集（Firecrawl MCP）
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/mcp_remote.py" firecrawl batch --urls https://a.com https://b.com

# 语义搜索（Exa MCP）
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/mcp_remote.py" exa search --query "AI搜索引擎趋势"

# 相似内容发现（Exa MCP）
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/mcp_remote.py" exa similar --url https://example.com/article

# AI搜索（Tavily MCP）
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/mcp_remote.py" tavily search --query "GEO优化最佳实践"

# 深度搜索（Tavily MCP）
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/mcp_remote.py" tavily deep --query "人工智能发展趋势分析"
```

##### MCP服务矩阵

| 阶段 | MCP服务 | 功能 | 优势 |
|------|---------|------|------|
| 内容采集 | Firecrawl | 批量页面采集 | Markdown提取、结构化 |
| 内容采集 | Exa | 语义搜索 | AI理解、相关性高 |
| 内容采集 | Brave | 搜索结果 | 隐私、快速 |
| 发布优化 | llms-mcp | llms.txt生成 | AI可发现性 |
| 发布优化 | schema-mcp | JSON-LD生成 | 结构化数据 |
| 发布优化 | geo-analyzer | GEO评分 | 效果验证 |

##### 环境变量配置

```bash
# MCP集成（可选，解锁高级功能）
export FIRECRAWL_API_KEY="your-key"      # https://firecrawl.dev (免费500次/月)
export EXA_API_KEY="your-key"            # https://exa.ai (免费1000次/月)
export TAVILY_API_KEY="your-key"         # https://tavily.com (免费1000次/月)
export BRAVE_API_KEY="your-key"          # https://brave.com (免费2000次/月)
```

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V2.0 | 2026-08-19 | MCP集成中心，远程MCP服务调用 |
| V1.0 | 2026-04-10 | 初始集成，基于GEO-SEO/geo-content-writer |
