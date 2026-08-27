# Comment Analyzer EXTEND.md

## 默认评论分析配置

---

## 自定义平台适配 (Custom Platform Adaptation)

### weibo-adapter
- platform: 微博
- comment_structure: nested
- emoji_support: full
- hashtag_behavior: clickable
- user_mentions: enabled

### xiaohongshu-adapter
- platform: 小红书
- comment_structure: flat
- emoji_support: full
- hashtag_behavior: discoverable
- user_mentions: enabled

### douyin-adapter
- platform: 抖音
- comment_structure: flat_with_sort
- emoji_support: full
- hashtag_behavior: topic_based
- user_mentions: enabled

### zhihu-adapter
- platform: 知乎
- comment_structure: threaded
- emoji_support: limited
- hashtag_behavior: minimal
- user_mentions: enabled

### juejin-adapter
- platform: 掘金
- comment_structure: nested
- emoji_support: full
- hashtag_behavior: technical
- user_mentions: enabled

---

## 自定义情感分析 (Custom Sentiment Analysis)

### basic-sentiment
- model: rule_based
- categories: [positive, neutral, negative]
- confidence: binary
- aspect: overall

### fine-grained-sentiment
- model: deep_learning
- categories: [strong_positive, positive, neutral, negative, strong_negative]
- confidence: probability_score
- aspect: sentence_level

### aspect-sentiment
- model: aspect_based
- categories: multi_dimensional
- confidence: detailed
- aspect: feature_level

---

## 自定义主题提取 (Custom Topic Extraction)

### keyword-extraction
- method: tf_idf
- count: top_10
- ngram: unigrams
- filtering: stop_words_removed

### phrase-extraction
- method: collocation
- count: top_20
- ngram: bigrams_trigrams
- filtering: meaningful_only

### topic-modeling
- method: lda
- count: 5_topics
- ngram: phrases
- filtering: semantic_relevance

---

## 自定义用户画像 (Custom User Profiling)

### basic-profile
- demographics: [location, gender]
- interests: inferred
- behavior: basic_metrics
- influence: follower_count

### detailed-profile
- demographics: [location, gender, age]
- interests: explicit_tags
- behavior: engagement_patterns
- influence: interaction_quality

### advanced-profile
- demographics: full_spectrum
- interests: semantic_clusters
- behavior: temporal_patterns
- influence: network_analysis

---

## 自定义观点聚类 (Custom Opinion Clustering)

### simple-clustering
- algorithm: k_means
- clusters: 3_5
- similarity: lexical
- labeling: frequent_terms

### semantic-clustering
- algorithm: hierarchical
- clusters: 5_10
- similarity: embedding_based
- labeling: representative_phrases

### community-clustering
- algorithm: community_detection
- clusters: organic
- similarity: interaction_based
- labeling: community_themes

---

## 自定义热点检测 (Custom Hot Topic Detection)

### frequency-based
- metric: comment_volume
- threshold: spike_detection
- window: sliding_window
- normalization: baseline_adjusted

### velocity-based
- metric: growth_rate
- threshold: exponential
- window: time_series
- normalization: relative

### influence-based
- metric: weighted_engagement
- threshold: top_percentile
- window: cumulative
- normalization: user_weighted

---

## 自定义异常检测 (Custom Anomaly Detection)

### spam-detection
- method: pattern_matching
- sensitivity: medium
- action: flag_only
- learning: static_rules

### bot-detection
- method: behavioral_analysis
- sensitivity: high
- action: auto_hide
- learning: adaptive

### sentiment-anomaly
- method: statistical_outlier
- sensitivity: medium
- action: alert_only
- learning: baseline_dynamic

---

## 自定义可视化 (Custom Visualization)

### summary-charts
- charts: [sentiment_pie, topic_bar, engagement_line]
- detail: aggregated
- interactivity: static
- export: png

### interactive-dashboard
- charts: all_types
- detail: drill_down
- interactivity: filters_selections
- export: multiple_formats

### real-time-monitor
- charts: live_updates
- detail: stream
- interactivity: auto_refresh
- export: scheduled_reports

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/comment-analyzer/EXTEND.md`
- **用户级**: `~/.claude/skills/comment-analyzer/EXTEND.md`
- **默认级**: `skills/comment-analyzer/EXTEND.md`

---

## 使用示例

### 微博评论分析
```markdown
## Weibo Comment Analysis

### weibo-analysis
- platform: weibo-adapter
- sentiment: fine-grained-sentiment
- topics: phrase-extraction
- profile: basic-profile
- clustering: semantic-clustering
- hot_topics: velocity-based
- anomaly: spam-detection
- visualization: summary-charts
```

### 小红书用户洞察
```markdown
## Xiaohongshu User Insights

### xiaohongshu-insights
- platform: xiaohongshu-adapter
- sentiment: aspect-sentiment
- topics: topic-modeling
- profile: detailed-profile
- clustering: community-clustering
- hot_topics: influence-based
- anomaly: bot-detection
- visualization: interactive-dashboard
```

### 跨平台舆情监控
```markdown
## Cross-Platform Monitoring

### cross-platform-monitor
- platforms: [weibo, xiaohongshu, douyin]
- sentiment: fine-grained-sentiment
- topics: topic-modeling
- profile: advanced-profile
- clustering: semantic-clustering
- hot_topics: all_methods
- anomaly: full_detection
- visualization: real-time-monitor
```
