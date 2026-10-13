# China Viral Content Analyzer EXTEND.md

## 默认爆款分析配置

---

## 自定义平台选择 (Custom Platform Selection)

### xiaohongshu-platform
- platform: 小红书
- data_type: posts
- engagement: [likes, collects, comments, shares]
- algorithm: recommendation_based

### douyin-platform
- platform: 抖音
- data_type: videos
- engagement: [likes, comments, shares, completion]
- algorithm: traffic_based

### weibo-platform
- platform: 微博
- data_type: posts
- engagement: [likes, comments, reposts]
- algorithm: trending_based

### zhihu-platform
- platform: 知乎
- data_type: answers
- engagement: [upvotes, comments, shares]
- algorithm: quality_based

### juejin-platform
- platform: 掘金
- data_type: articles
- engagement: [views, likes, comments, collects]
- algorithm: tech_community

---

## 自定义分析维度 (Custom Analysis Dimensions)

### content-analysis
- title: pattern_analysis
- structure: framework_extraction
- tone: emotional_tone
- length: optimal_length

### visual-analysis
- images: style_analysis
- layout: composition
- colors: color_psychology
- format: best_format

### timing-analysis
- post_time: peak_hours
- day_of_week: best_days
- frequency: posting_frequency
- seasonality: trend_aware

### audience-analysis
- demographics: user_profile
- psychographics: interest_tags
- pain_points: needs_analysis
- behavior: engagement_pattern

---

## 自定义爆款要素 (Custom Viral Elements)

### emotional-triggers
- emotions: [curiosity, excitement, resonance, surprise]
- intensity: high
- authenticity: genuine
- timing: trend_sensitive

### value-proposition
- type: [educational, entertaining, inspirational]
- uniqueness: differentiated
- practicality: actionable
- depth: comprehensive

### social-proof
- indicators: [user_count, authority, verification]
- ugc_content: encouraged
- community_interaction: active
- influence: measurable

### algorithm-friendliness
- keywords: optimized
- hashtags: strategic
- interactions: encouraged
- retention: high_completion

---

## 自定义数据收集 (Custom Data Collection)

### basic-collection
- sources: 1_platform
- sample_size: top_10
- time_range: 7_days
- metrics: basic_metrics

### standard-collection
- sources: 2_3_platforms
- sample_size: top_30
- time_range: 30_days
- metrics: standard_metrics

### deep-collection
- sources: all_platforms
- sample_size: top_100
- time_range: 90_days
- metrics: all_metrics

---

## 自定义报告格式 (Custom Report Format)

### summary-report
- sections: [key_findings, top_elements, recommendations]
- length: concise
- charts: essential
- action_items: prioritized

### detailed-report
- sections: all_sections
- length: comprehensive
- charts: multiple
- action_items: detailed

### presentation-report
- sections: visual_focused
- length: slide_format
- charts: abundant
- action_items: next_steps

---

## 自定义趋势检测 (Custom Trend Detection)

### basic-trends
- method: keyword_frequency
- window: 7_days
- threshold: linear_increase
- confidence: moderate

### advanced-trends
- method: semantic_analysis
- window: 30_days
- threshold: exponential_growth
- confidence: high

### predictive-trends
- method: machine_learning
- window: 90_days
- threshold: pattern_prediction
- confidence: probabilistic

---

## 自定义竞品分析 (Custom Competitor Analysis)

### direct-competitors
- scope: same_niche
- depth: top_5
- metrics: performance_comparison
- benchmarks: industry_standard

### indirect-competitors
- scope: adjacent_niche
- depth: top_10
- metrics: strategy_analysis
- benchmarks: cross_industry

### comprehensive-competitors
- scope: all_relevant
- depth: unlimited
- metrics: full_spectrum
- benchmarks: best_in_class

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/china-viral-content-analyzer/EXTEND.md`
- **用户级**: `~/.claude/skills/china-viral-content-analyzer/EXTEND.md`
- **默认级**: `skills/china-viral-content-analyzer/EXTEND.md`

---

## 使用示例

### 小红书爆款分析
```markdown
## Xiaohongshu Viral Analysis

### xiaohongshu-analysis
- platform: xiaohongshu-platform
- dimensions: all_dimensions
- elements: all_viral_elements
- collection: standard-collection
- report: detailed-report
- trends: advanced-trends
- competitors: direct-competitors
```

### 跨平台爆款分析
```markdown
## Cross-Platform Viral Analysis

### cross-platform-analysis
- platforms: [xiaohongshu, douyin, weibo]
- dimensions: content-analysis + timing-analysis
- elements: emotional-triggers + value-proposition
- collection: deep-collection
- report: presentation-report
- trends: predictive-trends
- competitors: comprehensive-competitors
```

### 快速爆款检测
```markdown
## Quick Viral Detection

### quick-detection
- platform: xiaohongshu-platform
- dimensions: content-analysis
- elements: algorithm-friendliness
- collection: basic-collection
- report: summary-report
- trends: basic-trends
- competitors: none
```
