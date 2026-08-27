---
license: UNKNOWN
name: seo-geo
description: >
Optimize content for AI Overviews (formerly SGE), ChatGPT web search,
Perplexity, and other AI-powered search experiences. GEO analysis including
brand mention signals, AI crawler accessibility, llms.txt compliance,
passage-level citability scoring, and platform-specific optimization.
Use when user says "AI Overviews", "SGE", "GEO", "AI search",
"LLM optimization", "Perplexity", "AI citations", "ChatGPT search",
or "AI visibility".
user-invokable: true
argument-hint: "[url]"
allowed-tools: - Read
- Grep
- Glob
- Bash
- WebFetch
triggers: ["seo geo", "SEO-GEO: AI搜索引擎优化 (V2.0)"]
---

# SEO-GEO: AI搜索引擎优化 (V2.0)

## L0: 一句话描述 (≤15字)
AI搜索引擎GEO优化，让AI推荐你的内容

## L1: 使用场景 (50-100字)

**适用场景**：
- 优化内容被ChatGPT、Perplexity、Google AI Overviews、Bing Copilot等AI助手引用
- 检测品牌在AI搜索结果中的提及和引用情况
- 针对AI搜索算法特性优化内容结构和引用上下文
- 提升品牌在Wikipedia、Reddit、YouTube等高权重平台的提及

**触发关键词**：`/seo-geo`、`GEO优化`、`AI搜索优化`、`AI引用`、`AI citations`、`AI Overviews`

## L2: 详细文档

### 一、GEO核心指标 (2026年最新数据)

| 指标 | 数值 | 来源 |
|------|------|------|
| AI Overviews月活用户 | 15亿+ (200+国家) | Google |
| AI Overviews查询覆盖率 | 50%+ | 行业数据 |
| AI推荐会话增长 | 527% (2025年1-5月) | SparkToro |
| ChatGPT周活用户 | 9亿 | OpenAI |
| Perplexity月查询量 | 5亿+ | Perplexity |

### 二、核心洞察：品牌提及 > 传统外链

**品牌提及与AI可见性的相关性比外链高3倍**
(Ahrefs 2025年12月75000品牌研究)

| 信号类型 | 与AI引用的相关性 |
|---------|----------------|
| YouTube提及 | ~0.737 (最强) |
| Reddit提及 | 高 |
| Wikipedia存在 | 高 |
| LinkedIn存在 | 中等 |
| 域名权重(外链) | ~0.266 (弱) |

**仅11%的域名**同时被ChatGPT和Google AI Overviews引用同一查询，平台特定优化至关重要。

---

### 三、GEO分析标准 (五维评分)

#### 1. 可引用性评分 (Citability Score) - 25%

**最佳段落长度：134-167词**

| 强信号 | 弱信号 |
|--------|--------|
| 清晰、可引用的事实/数据句 | 模糊、笼统的表述 |
| 自包含答案块（脱离上下文可理解） | 无证据的观点 |
| 段落开头40-60词直接回答 | 结论埋藏在段落中 |
| 归因于特定来源的主张 | 无具体数据点 |
| "X is..." / "X refers to..." 定义模式 | |
| 独特数据点（其他地方没有） | |

#### 2. 结构可读性 (Structural Readability) - 20%

**92%的AI Overview引用来自排名前10的页面**，但47%来自排名5位以下的页面（选择逻辑不同）。

| 强信号 | 弱信号 |
|--------|--------|
| 清晰的H1→H2→H3标题层级 | 大段文字无结构 |
| 基于问题的标题（匹配查询模式） | 标题层级不一致 |
| 短段落（2-4句） | 无列表或表格 |
| 对比数据表格 | 信息埋在段落中 |
| 有序/无序列表（步骤或多项目） | |
| FAQ部分（清晰的Q&A格式） | |

#### 3. 多模态内容 (Multi-Modal Content) - 15%

含多模态元素的内容**选择率高156%**。

| 检查项 | 说明 |
|--------|------|
| 文本 + 相关图片 | 基础多模态 |
| 视频内容（嵌入或链接） | 增强参与度 |
| 信息图和图表 | 视觉化数据 |
| 交互元素（计算器、工具） | 最高参与度 |
| 支持媒体的结构化数据 | 技术增强 |

#### 4. 权威与品牌信号 (Authority & Brand Signals) - 20%

| 强信号 | 弱信号 |
|--------|--------|
| 带资质的作者署名 | 匿名作者 |
| 发布日期和最后更新日期 | 无日期 |
| 引用主要来源（研究、官方文档、数据） | 无引用来源 |
| 组织资质和附属机构 | 无品牌跨平台存在 |
| 专家引用（带归属） | |
| Wikipedia、Wikidata实体存在 | |
| Reddit、YouTube、LinkedIn上的提及 | |

#### 5. 技术可访问性 (Technical Accessibility) - 20%

**AI爬虫不执行JavaScript**，服务器端渲染至关重要。

| 检查项 | 说明 |
|--------|------|
| 服务器端渲染(SSR) vs 仅客户端内容 | 关键差异 |
| robots.txt中的AI爬虫访问 | 技术前提 |
| llms.txt文件存在和配置 | 新兴标准 |
| RSL 1.0许可条款 | 新兴标准 |

---

### 四、AI爬虫检测

检查 `robots.txt` 中的AI爬虫：

| 爬虫 | 所有者 | 用途 |
|------|--------|------|
| GPTBot | OpenAI | ChatGPT网络搜索 |
| OAI-SearchBot | OpenAI | OpenAI搜索功能 |
| ChatGPT-User | OpenAI | ChatGPT浏览 |
| ClaudeBot | Anthropic | Claude网络功能 |
| PerplexityBot | Perplexity | Perplexity AI搜索 |
| CCBot | Common Crawl | 训练数据（常被阻止） |
| anthropic-ai | Anthropic | Claude训练 |
| Bytespider | ByteDance | TikTok/Douyin AI |
| cohere-ai | Cohere | Cohere模型 |

**建议**：允许GPTBot、OAI-SearchBot、ClaudeBot、PerplexityBot以获得AI搜索可见性。阻止CCBot和训练爬虫（如需要）。

---

### 五、llms.txt标准

新兴的 **llms.txt** 标准为AI爬虫提供结构化内容指导。

**位置**：`/llms.txt` (域名根目录)

**格式**：
```
# Site Title
> Brief description

## Main sections
- [Page title](url): Description
- [Another page](url): Description

## Optional: Key facts
- Fact 1
- Fact 2
```

**检查项**：
- `/llms.txt` 存在性
- 结构化内容指导
- 关键页面突出
- 联系/权威信息

---

### 六、RSL 1.0 (Really Simple Licensing)

2025年12月新标准，用于机器可读的AI许可条款。

**支持者**：Reddit、Yahoo、Medium、Quora、Cloudflare、Akamai、Creative Commons

---

### 七、平台特定优化矩阵

| 平台 | 关键引用来源 | 优化重点 |
|------|------------|---------|
| **Google AI Overviews** | 排名前10页面(92%) | 传统SEO + 段落优化 |
| **ChatGPT** | Wikipedia(47.9%), Reddit(11.3%) | 实体存在、权威来源 |
| **Perplexity** | Reddit(46.7%), Wikipedia | 社区验证、讨论 |
| **Bing Copilot** | Bing索引、权威站点 | Bing SEO、IndexNow |

---

### 八、AI搜索平台详细对比

| 维度 | Google AI Overviews | Bing Copilot | Perplexity | ChatGPT |
|------|-------------------|-------------|------------|---------|
| **类型** | SERP功能 | SERP功能 | 独立 | 独立 |
| **来源选择** | Top 10-12有机; Gemini | Bing索引; GPT-4 | 200B+ URL索引 | GPTBot; 高权威 |
| **域名偏好** | 15年以上(49%) | 年轻(18.85%) | 中等站点机会 | 较老(45.8%) |
| **独特信号** | 传统SEO | LinkedIn(B2B) | 新鲜度、语义 | 外链、权威 |
| **引用CTR** | 20-35%高于有机 | 最短响应~3链接 | 高可追踪 | 高转化6x |

---

### 九、快速提升指南

#### 立即见效 (1-2小时)

1. 在前60词添加"What is [topic]?"定义
2. 创建134-167词自包含答案块
3. 添加基于问题的H2/H3标题
4. 包含具体统计数据（带来源）
5. 添加发布/更新日期
6. 为作者实现Person schema
7. 在robots.txt中允许关键AI爬虫

#### 中等投入 (1-2天)

1. 创建 `/llms.txt` 文件
2. 添加作者简介（含资质+ Wikipedia/LinkedIn链接）
3. 确保关键内容的服务器端渲染
4. 在Reddit、YouTube建立实体存在
5. 添加对比数据表
6. 实施FAQ部分（结构化，非商业站点schema）

#### 高影响 (1-4周)

1. 创建原创研究/调查（独特可引用性）
2. 建立品牌/关键人物的Wikipedia存在
3. 建立YouTube频道（含内容提及）
4. 实施综合实体链接（跨平台sameAs）
5. 开发独特工具或计算器

---

### 十、GEO分析输出格式

生成 `GEO-ANALYSIS.md` 包含：

1. **GEO准备度评分：XX/100**
2. **平台分解** (Google AIO, ChatGPT, Perplexity分数)
3. **AI爬虫访问状态** (允许/阻止的爬虫)
4. **llms.txt状态** (存在/缺失/建议)
5. **品牌提及分析** (Wikipedia, Reddit, YouTube, LinkedIn存在)
6. **段落级可引用性** (识别134-167词最佳块)
7. **服务器端渲染检查** (JavaScript依赖分析)
8. **Top 5最高影响变更**
9. **Schema建议** (AI可发现性)
10. **内容重格式化建议** (需重写特定段落)

---

### 十一、技术检查清单

#### robots.txt检查
```bash
# 允许AI爬虫
User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

# 可选：阻止训练爬虫
User-agent: CCBot
Disallow: /
```

#### llms.txt模板
```markdown
# Brand Name
> AI-optimized description of your brand (1-2 sentences)

## Products/Services
- [Product Name](https://example.com/product): Brief description
- [Service Name](https://example.com/service): Brief description

## Key Information
- Founded: YEAR
- Headquarters: LOCATION
- Core offering: ONE SENTENCE

## Expertise Areas
- Area 1
- Area 2
- Area 3

## Latest Content
- [Recent Article](https://example.com/blog/article): Description
- [Another Post](https://example.com/blog/post): Description
```

---

### 十二、与现有SEO技能协同

| 协同技能 | 协同方式 | 效果 |
|---------|---------|------|
| `seo-audit` | 传统SEO审计 → GEO差距分析 | 双重覆盖 |
| `seo-technical` | 技术可访问性检查 → SSR/爬虫配置 | 技术基础 |
| `seo-content` | 内容优化 → 可引用段落重写 | 内容质量 |
| `schema-markup` | 结构化数据 → AI可发现性 | 语义增强 |
| `keyword-research` | 关键词研究 → AI查询模式 | 目标精准 |
| `link-building` | 外链建设 → 品牌提及增强 | 权威信号 |
| `generative-engine-optimization` | GEO策略完整指南 | 策略互补 |
| `ai-traffic-tracking` | AI流量追踪 → GEO效果测量 | 效果验证 |

**协同工作流**：
```
seo-audit (传统审计) → seo-geo (AI优化差距分析) → seo-content (内容重写) → ai-traffic-tracking (效果追踪)
```

---

### 十三、相关技能

- `generative-engine-optimization` - GEO完整策略指南
- `seo-audit` - 传统SEO审计
- `seo-technical` - 技术SEO检查
- `seo-content` - 内容优化
- `schema-markup` - 结构化数据
- `keyword-research` - 关键词研究
- `link-building` - 外链建设
- `ai-traffic-tracking` - AI流量追踪
- `serp-features` - SERP功能（AI Overviews是SERP功能）
- `featured-snippet` - 精选摘要优化

---

### 十四、MCP集成（V3.0新增）

#### MCP服务调用

本技能已集成天龙引擎MCP中心，支持按需调用各种MCP服务。

##### MCP命令速查

```bash
# GEO分析（使用内置MCP）
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/cli.py" geo-analyze https://example.com

# llms.txt生成（使用内置MCP）
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/cli.py" llms-generate https://example.com

# Schema生成（使用内置MCP）
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/cli.py" schema-generate Article --title "标题" --url "https://example.com"

# 使用远程MCP服务
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/mcp_remote.py" firecrawl scrape --url https://example.com

# 语义搜索（Exa MCP）
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/mcp_remote.py" exa search --query "AI搜索引擎趋势"

# AI搜索（Tavily MCP）
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/mcp_remote.py" tavily search --query "GEO优化最佳实践"
```

##### MCP集成工作流

```
┌─────────────────────────────────────────────────────────────┐
│  SEO-GEO + MCP 集成工作流                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. GEO分析（MCP内置）                                       │
│     └── /mcp geo-analyze [url]                             │
│         ├── 机器人检查                                       │
│         ├── llms.txt分析                                    │
│         └── 五维评分                                        │
│                    ↓                                        │
│  2. 内容采集（Firecrawl MCP）                                │
│     └── mcp_remote.py firecrawl scrape [url]              │
│         ├── Markdown提取                                    │
│         └── 结构化内容                                       │
│                    ↓                                        │
│  3. 竞品分析（Exa MCP）                                      │
│     └── mcp_remote.py exa search [keyword]                │
│         ├── 语义搜索                                        │
│         └── 相似内容发现                                    │
│                    ↓                                        │
│  4. SERP分析（Tavily MCP）                                  │
│     └── mcp_remote.py tavily search [query]               │
│         ├── AI搜索结果                                      │
│         └── 引用上下文                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

##### MCP服务配置

```bash
# 必需环境变量（可选，但解锁高级功能）
export FIRECRAWL_API_KEY="your-key"      # https://firecrawl.dev
export EXA_API_KEY="your-key"            # https://exa.ai
export TAVILY_API_KEY="your-key"         # https://tavily.com
export DATAFORSEO_LOGIN="your-login"
export DATAFORSEO_PASSWORD="your-password"
```

##### MCP协同矩阵

| 天龙组件 | MCP服务 | 协同方式 |
|---------|---------|---------|
| seo-geo | geo-analyzer | GEO健康度评分 |
| seo-geo | llms-mcp | llms.txt生成 |
| seo-geo | schema-mcp | JSON-LD生成 |
| seo-content | firecrawl | 内容采集 |
| 32-01市场研究 | exa | 语义搜索 |
| 01调研师 | tavily | AI搜索分析 |

---

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| 3.0 | 2026-08-19 | MCP集成中心，按需调用GEO/SEO服务 |
| 2.0 | 2026-04-23 | L0/L1/L2渐进披露格式 + 五维评分 + 平台特定优化 |
| 1.0 | 2026-04-07 | 初始GEO分析标准 |
