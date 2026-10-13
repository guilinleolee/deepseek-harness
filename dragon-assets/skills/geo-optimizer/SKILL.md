---
license: UNKNOWN
name: geo-optimizer
description: GEO(生成引擎优化)内容优化技能。针对Perplexity、Google SGE、ChatGPT Search等AI生成引擎优化内容可见性。包含实体优化、结构化数据、引用分析、效果监控等核心功能。触发词：GEO优化、AI搜索优化、Perplexity优化、SGE优化、AI引用优化、生成引擎优化。
version: 1.0.0
author: 天龙引擎
created: 2026-03-03
category: marketing
domain: digital-marketing
tech-stack: GEO, AI-Search, Schema.org, LLM
triggers: ["geo optimizer", "GEO Optimizer - 生成引擎优化技能"]
---

# GEO Optimizer - 生成引擎优化技能

针对AI生成引擎（Perplexity、Google SGE、ChatGPT Search等）的内容优化完整方案。

## 🎯 核心理念

### GEO vs SEO：本质差异

| 维度 | SEO（搜索引擎优化） | GEO（生成引擎优化） |
|------|-------------------|-------------------|
| **目标对象** | 搜索引擎爬虫 | AI大模型 |
| **核心逻辑** | 关键词匹配 | 理解+引用+推荐 |
| **优化重点** | 排名位置 | 被引用概率 |
| **内容要求** | 关键词密度 | 权威性+结构化 |
| **成功指标** | 搜索排名 | AI引用率 |

### AI引用决策模型

```
AI引用决策链：
1. 可发现性 → AI能否找到内容？
2. 理解性 → AI能否理解内容？
3. 信任性 → AI是否信任内容？
4. 相关性 → 内容是否相关？
5. 引用价值 → 是否值得引用？
```

## 🚀 Quick Start

### 1. GEO诊断
```bash
# 分析单页面GEO优化潜力
/geo-analyze https://example.com/article

# 全站GEO扫描
/geo-analyze --site https://example.com
```

### 2. 内容优化
```bash
# 优化现有内容
/geo-optimize content.md

# 生成GEO友好内容
/geo-optimize --create "主题关键词"
```

### 3. 引用追踪
```bash
# 追踪关键词被引用情况
/geo-track "人工智能发展趋势"

# 竞品引用分析
/geo-track --competitor "竞品域名"
```

## 📋 核心功能

### 功能1：实体优化

**目标**：让AI准确识别和理解内容核心实体。

**操作步骤**：
1. 识别内容核心实体（每页≤3个）
2. 添加实体定义（首次出现时）
3. 建立实体关联（内部链接）
4. 使用Schema标记实体

**工具**：
- `prompts/entity-optimization.md` - 实体优化提示词
- `tools/entity-extractor.js` - 实体提取工具

### 功能2：结构化数据

**目标**：提升AI理解效率。

**必选Schema类型**：
- Article（文章）
- FAQPage（问答）
- Organization（组织）
- Person（作者）
- BreadcrumbList（面包屑）

**工具**：
- `prompts/structured-data.md` - 结构化数据模板
- `tools/schema-generator.js` - Schema生成器

### 功能3：引用价值提升

**目标**：增加被AI引用的概率。

**核心策略**：
1. 数据支撑（定量描述）
2. 权威引文（可信来源）
3. 清晰结构（易于理解）
4. 独特观点（差异化价值）

**工具**：
- `prompts/citation-analysis.md` - 引用分析框架
- `tools/citation-tracker.js` - 引用追踪工具

### 功能4：效果监控

**目标**：持续追踪GEO优化效果。

**监控指标**：
- AI引用率（周度）
- 引用位置分布（月度）
- 实体识别准确率（月度）
- 平台覆盖情况（季度）

**工具**：
- `tools/geo-analyzer.js` - GEO效果分析

## 🔧 工作流程

### 流程1：新项目GEO诊断

```
Step 1: 可发现性检查
├── robots.txt验证
├── sitemap.xml覆盖
├── 内部链接结构
└── 外部引用情况

Step 2: 引用价值评估
├── 内容权威性评分
├── 结构化数据检测
├── 实体清晰度分析
└── 竞品对比分析

Step 3: 优化策略制定
├── 优先级排序（P0-P3）
├── 实施路径规划
├── 资源评估
└── 预期效果
```

### 流程2：单篇内容优化

```
Step 1: 实体定义
- 识别核心实体
- 添加实体描述
- 建立实体关联

Step 2: 结构化标记
- 选择Schema类型
- 生成JSON-LD
- 验证正确性

Step 3: 权威性增强
- 添加数据支撑
- 引用可信来源
- 作者资质展示

Step 4: 可读性优化
- 逻辑结构清晰
- 问答式表达
- 段落简洁
```

### 流程3：持续监控迭代

```
Week 1: 基准测试
├── 初始引用率
├── 竞品对比
└── 优化空间识别

Week 2-4: 优化实施
├── P0问题修复
├── 内容优化
└── 结构化完善

Month 2: 效果评估
├── 引用率变化
├── A/B测试结果
└── 策略调整

Month 3+: 持续迭代
├── 新平台适配
├── 内容更新
└── 竞品跟进
```

## 🚫 优化底线

### 绝对禁止

| 禁止行为 | 原因 | 后果 |
|---------|------|------|
| ❌ 关键词填充 | AI能识别并降低信任度 | 引用率下降 |
| ❌ 隐藏内容 | AI理解完整性受损 | 权威性归零 |
| ❌ 伪造评价 | 信任体系崩溃 | 永久黑名单 |
| ❌ 过度结构化 | 被判定为营销内容 | 引用概率降低 |

### 强制执行

| 要求 | 原因 | 验证方法 |
|------|------|---------|
| ✅ 数据支撑 | AI偏好定量内容 | 每段≥1个数据点 |
| ✅ 权威引文 | 提升可信度 | 每篇≥3个引用 |
| ✅ 结构化数据 | 理解效率+50% | 覆盖率>90% |
| ✅ 实体明确 | 理解准确率+30% | 每页≤3核心实体 |

## 📊 效果指标

### 核心KPI

| 指标 | 计算方式 | 目标值 | 监控频率 |
|------|---------|--------|---------|
| **AI引用率** | 被引用次数/内容总数 | >15% | 周 |
| **引用位置分** | 首引3分/中引2分/尾引1分 | >2.0 | 月 |
| **实体识别率** | 正确识别实体数/总实体数 | >80% | 月 |
| **结构化覆盖** | Schema标记页面数/总页面数 | >90% | 季 |

### 辅助指标

| 指标 | 说明 | 健康值 |
|------|------|--------|
| 引用增长率 | 月度引用次数增长率 | >10% |
| 引用准确性 | AI引用内容与原文匹配度 | >90% |
| 平台覆盖 | 被引用的AI平台数量 | ≥3个 |
| 时效性 | 内容更新到被引用的时间 | <7天 |

## 🔗 依赖关系

### 技能依赖
```yaml
核心依赖:
  - content-creator      # 内容创作基础
  - humanizer-zh         # 内容人性化

可选依赖:
  - seo                  # SEO知识（对比学习）
  - china-viral-content-analyzer  # 爆款分析
```

### 工具依赖
```yaml
分析工具:
  - geo-analyzer.js      # GEO效果分析
  - entity-extractor.js  # 实体提取
  - citation-tracker.js  # 引用追踪

生成工具:
  - schema-generator.js  # Schema生成
```

## 📚 参考资料

### 官方文档
- `references/geo-guidelines.md` - GEO优化指南
- `references/schema-templates.md` - Schema模板库
- `references/citation-sources.md` - 权威引用源列表

### 案例库
- `references/case-studies/` - 成功案例
- `references/anti-patterns.md` - 反面案例

### 学术资源
- LLM引用行为研究论文
- GEO优化白皮书
- AI搜索算法分析

## 🎯 使用场景

### 场景1：新内容创作
```bash
# 使用实体优化提示词
/geo-optimize --create "人工智能发展趋势" --entity-optimization

# 自动添加结构化数据
/geo-optimize --create "主题" --auto-schema
```

### 场景2：现有内容优化
```bash
# 全面的GEO诊断
/geo-analyze https://example.com/article --full

# 针对性优化建议
/geo-optimize article.md --recommendations
```

### 场景3：竞品分析
```bash
# 竞品GEO策略分析
/geo-analyze --competitor competitor.com

# 差异化机会识别
/geo-optimize --gap-analysis
```

### 场景4：效果监控
```bash
# 生成周度报告
/geo-track --weekly-report

# 追踪特定关键词
/geo-track "目标关键词" --platform perplexity,sge
```

## 💡 最佳实践

### 内容创作
1. 每段包含1个数据点
2. 每篇引用≥3个可信来源
3. 核心实体≤3个/页
4. 使用问答式结构

### 技术实现
1. JSON-LD优于Microdata
2. Schema标记覆盖>90%
3. 页面加载速度<3秒
4. 移动端友好

### 持续优化
1. 周度引用率监控
2. 月度策略复盘
3. 季度竞品分析
4. 年度趋势研判

## 🔄 Evolution Pattern

本技能支持自定义扩展。创建 `evolution.json` 保存个性化配置：

```json
{
  "custom_rules": [
    "行业特定的实体定义",
    "自定义Schema扩展"
  ],
  "platforms": [
    "特定AI平台优化策略"
  ],
  "metrics": [
    "自定义KPI指标"
  ]
}
```

---

### MCP集成（V2.0新增）

#### MCP服务调用

本技能已集成天龙引擎MCP中心，支持按需调用各种MCP服务。

##### MCP命令速查

```bash
# GEO分析
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/cli.py" geo-analyze https://example.com

# Schema生成
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/cli.py" schema-generate Article --title "标题"

# llms.txt生成
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/cli.py" llms-generate https://example.com

# 内容采集（远程MCP）
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/mcp_remote.py" firecrawl scrape --url https://example.com

# 语义搜索（远程MCP）
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/mcp_remote.py" exa search --query "相关内容"
```

##### MCP协同矩阵

| 天龙组件 | MCP服务 | 协同方式 |
|---------|---------|---------|
| geo-optimizer | schema-mcp | Schema生成自动化 |
| geo-optimizer | llms-mcp | llms.txt生成 |
| geo-optimizer | geo-analyzer | GEO评分 |
| 35-04 GEO内容优化师 | firecrawl | 内容采集 |
| 01调研师 | exa | 语义搜索 |

##### 环境变量配置

```bash
# 远程MCP服务（可选）
export FIRECRAWL_API_KEY="your-key"      # https://firecrawl.dev
export EXA_API_KEY="your-key"          # https://exa.ai
export TAVILY_API_KEY="your-key"       # https://tavily.com

# 内置服务（无需配置）
export GEOAPIFY_KEY="your-key"         # 地理编码（免费60万次/月）
```

---

**版本**: 2.0.0
**最后更新**: 2026-08-19
**维护者**: 35-04 GEO内容优化师
**MCP集成**: MCP Integration Center V1.0