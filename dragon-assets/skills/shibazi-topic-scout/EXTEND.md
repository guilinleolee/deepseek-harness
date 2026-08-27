# Shibazi Topic Scout EXTEND.md

## 默认选题侦察配置

---

## 自定义爆款分析 (Custom Viral Analysis)

### basic-viral
- platforms: [xiaohongshu]
- posts: top_20
- timeframe: 7_days
- metrics: [likes, comments]

### comprehensive-viral
- platforms: [xiaohongshu, douyin, weibo]
- posts: top_100
- timeframe: 30_days
- metrics: all_metrics

### real-time-viral
- platforms: all_platforms
- posts: trending_now
- timeframe: 24_hours
- metrics: velocity_focused

---

## 自定义市场洼地 (Custom Market Gap Detection)

### obvious-gaps
- analysis: supply_demand
- depth: surface_level
- competition: direct_only
- opportunity: high_volume_low_quality

### hidden-gaps
- analysis: semantic_analysis
- depth: moderate
- competition: indirect_included
- opportunity: underserved_segments

### blue-ocean
- analysis: comprehensive
- depth: deep
- competition: full_landscape
- opportunity: untapped_spaces

---

## 自定义三维匹配 (Custom 3D Matching)

### basic-match
- dimensions: 2
- weights: equal
- threshold: 50%
- feedback: binary

### weighted-match
- dimensions: 3
- weights: custom
- threshold: 70%
- feedback: scored

### ai-match
- dimensions: 3_plus
- weights: learned
- threshold: adaptive
- feedback: detailed_explanation

---

## 自定义信息增量 (Custom Information Increment)

### novelty-check
- comparison: exact_match
- depth: title_only
- benchmark: recent_posts
- innovation: minor_twists

### gap-analysis
- comparison: semantic_similarity
- depth: content_analysis
- benchmark: top_performing
- innovation: meaningful_additions

### value-assessment
- comparison: comprehensive
- depth: deep_content_analysis
- benchmark: industry_standards
- innovation: significant_insights

---

## 自定义标题推荐 (Custom Title Recommendation)

### template-based
- method: formula_templates
- variety: 10_variants
- testing: none
- optimization: click_maximizing

### data-driven
- method: historical_analysis
- variety: 20_variants
- testing: ab_tested
- optimization: conversion_optimized

### ai-creative
- method: generative_ai
- variety: unlimited
- testing: multi_armed_bandit
- optimization: engagement_maximized

---

## 自定义评分系统 (Custom Scoring System)

### simple-scoring
- factors: 3
- weights: equal
- scale: 1_10
- interpretation: manual

### weighted-scoring
- factors: 10
- weights: priority_based
- scale: 1_100
- interpretation: categorized

### ml-scoring
- factors: algorithmic
- weights: learned
- scale: probabilistic
- interpretation: confidence_interval

---

## 自定义竞品监控 (Custom Competitor Monitoring)

### basic-monitoring
- targets: top_5
- frequency: weekly
- depth: public_only
- alerts: major_changes

### intensive-monitoring
- targets: top_20
- frequency: daily
- depth: content_analysis
- alerts: all_updates

### predictive-monitoring
- targets: all_relevant
- frequency: real_time
- depth: deep_analysis
- alerts: trend_predictions

---

## 自定义趋势预测 (Custom Trend Prediction)

### historical-trends
- method: linear_extrapolation
- horizon: 1_week
- confidence: low
- application: reactive

### cyclical-trends
- method: seasonal_analysis
- horizon: 1_month
- confidence: medium
- application: proactive

### ai-trends
- method: deep_learning
- horizon: 3_months
- confidence: probabilistic
- application: strategic

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/shibazi-topic-scout/EXTEND.md`
- **用户级**: `~/.claude/skills/shibazi-topic-scout/EXTEND.md`
- **默认级**: `skills/shibazi-topic-scout/EXTEND.md`

---

## 使用示例

### 快速选题
```markdown
## Quick Topic Selection

### quick-selection
- viral: basic-viral
- market: obvious-gaps
- matching: basic-match
- increment: novelty-check
- titles: template-based
- scoring: simple-scoring
- monitoring: basic-monitoring
- trends: historical-trends
```

### 深度研究选题
```markdown
## Deep Research Topic

### deep-research
- viral: comprehensive-viral
- market: hidden-gaps
- matching: weighted-match
- increment: gap-analysis
- titles: data-driven
- scoring: weighted-scoring
- monitoring: intensive-monitoring
- trends: cyclical-trends
```

### 智能选题系统
```markdown
## Intelligent Topic System

### intelligent-system
- viral: real-time-viral
- market: blue-ocean
- matching: ai-match
- increment: value-assessment
- titles: ai-creative
- scoring: ml-scoring
- monitoring: predictive-monitoring
- trends: ai-trends
```
