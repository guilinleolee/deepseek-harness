# GEO Optimizer - 自定义配置

> 基于baoyu-skills的EXTEND机制，支持两级自定义配置

## 📋 配置层级

```
优先级：项目级 > 全局级 > 默认配置

项目级：[项目根目录]/.claude/geo-optimizer/EXTEND.md
全局级：~/.claude/skills/geo-optimizer/EXTEND.md（本文件）
默认级：~/.claude/skills/geo-optimizer/SKILL.md
```

## 🎯 自定义规则

### 规则1：目标平台配置

```yaml
# 优先优化的AI平台（按重要性排序）
target_platforms:
  - name: Perplexity
    weight: 0.4
    priority: high
    features:
      - academic_citations
      - real_time_search

  - name: Google SGE
    weight: 0.3
    priority: high
    features:
      - structured_data
      - e_e_a_t

  - name: ChatGPT Search
    weight: 0.2
    priority: medium
    features:
      - conversational_context

  - name: Claude Search
    weight: 0.1
    priority: medium
    features:
      - long_context
```

### 规则2：行业特定实体

```yaml
# 自定义行业实体库
industry_entities:
  tech:
    - "人工智能"
    - "机器学习"
    - "深度学习"
    - "自然语言处理"
    - "计算机视觉"

  finance:
    - "金融科技"
    - "区块链"
    - "数字货币"
    - "智能投顾"

  healthcare:
    - "数字医疗"
    - "远程医疗"
    - "医疗AI"
    - "精准医疗"
```

### 规则3：引用源白名单

```yaml
# 权威引用源（按可信度评分）
trusted_sources:
  academic:
    - domain: "scholar.google.com"
      score: 1.0
    - domain: "arxiv.org"
      score: 0.95
    - domain: "nature.com"
      score: 0.95
    - domain: "science.org"
      score: 0.95

  official:
    - domain: "gov.cn"
      score: 0.9
    - domain: "who.int"
      score: 0.9
    - domain: "worldbank.org"
      score: 0.85

  industry:
    - domain: "mckinsey.com"
      score: 0.8
    - domain: "deloitte.com"
      score: 0.8
    - domain: "bcg.com"
      score: 0.8
```

### 规则4：Schema优先级

```yaml
# 必选和可选Schema类型
schema_priority:
  required:
    - Article
    - Organization
    - BreadcrumbList

  recommended:
    - FAQPage
    - Person
    - WebSite

  optional:
    - VideoObject
    - ImageObject
    - HowTo
```

### 规则5：KPI阈值配置

```yaml
# 自定义KPI目标值
kpi_thresholds:
  ai_citation_rate:
    target: 0.15      # 15%
    warning: 0.10     # <10% 预警
    critical: 0.05    # <5% 严重

  citation_position_score:
    target: 2.0
    warning: 1.5
    critical: 1.0

  entity_recognition_rate:
    target: 0.80      # 80%
    warning: 0.60
    critical: 0.40

  schema_coverage:
    target: 0.90      # 90%
    warning: 0.70
    critical: 0.50
```

## 🔧 自定义工具

### 工具1：行业实体提取器

```javascript
// tools/custom-entity-extractor.js
module.exports = {
  name: 'custom-entity-extractor',
  extract: (content, industry) => {
    const entities = loadIndustryEntities(industry);
    return extractEntitiesFromContent(content, entities);
  }
};
```

### 工具2：引用源评分器

```javascript
// tools/citation-scorer.js
module.exports = {
  name: 'citation-scorer',
  score: (url) => {
    const trustedSources = loadTrustedSources();
    return calculateCitationScore(url, trustedSources);
  }
};
```

### 工具3：平台适配器

```javascript
// tools/platform-adapter.js
module.exports = {
  name: 'platform-adapter',
  adapt: (content, platform) => {
    const platformConfig = loadPlatformConfig(platform);
    return adaptContentForPlatform(content, platformConfig);
  }
};
```

## 📊 自定义报告模板

### 周度报告模板

```markdown
# GEO周度报告 - [日期范围]

## 📊 核心指标
- AI引用率：[当前值]（vs上周 [变化]）
- 引用位置分：[当前值]
- 新增引用：[数量]

## 🏆 平台分布
- Perplexity：[引用次数]
- Google SGE：[引用次数]
- ChatGPT Search：[引用次数]

## 📝 热门引用内容
1. [内容标题] - [引用次数]次
2. [内容标题] - [引用次数]次
3. [内容标题] - [引用次数]次

## 🎯 下周优化重点
- [优化项1]
- [优化项2]
```

## 🔄 配置更新日志

| 日期 | 变更内容 | 变更原因 |
|------|---------|---------|
| 2026-03-03 | 初始配置创建 | 新技能发布 |

---

**维护者**: 35-04 GEO内容优化师
**最后更新**: 2026-03-03