# Marketing Demand Acquisition EXTEND.md

## 默认营销获客配置

---

## 自定义渠道策略 (Custom Channel Strategy)

### single-channel
- channels: 1
- focus: maximized
- integration: none
- budget: 100%

### multi-channel
- channels: 2-3
- focus: balanced
- integration: basic
- budget: distributed

### omni-channel
- channels: all_relevant
- focus: customer_centric
- integration: full
- budget: dynamic_allocation

---

## 自定义付费广告 (Custom Paid Advertising)

### search-ads
- platform: google_ads
- bidding: manual
- budget: daily
- targeting: keywords
- optimization: conversions

### social-ads
- platform: [facebook, instagram, linkedin]
- bidding: automatic
- budget: campaign_based
- targeting: demographics + interests
- optimization: engagements

### display-ads
- platform: google_display
- bidding: cpm
- budget: campaign_based
- targeting: placements + topics
- optimization: clicks

---

## 自定义内容营销 (Custom Content Marketing)

### blog-content
- type: articles
- frequency: weekly
- length: 1000-2000_words
- seo: optimized
- promotion: social_media

### video-content
- type: videos
- frequency: bi_weekly
- length: 30-90_seconds
- platform: youtube
- promotion: social_media + email

### social-content
- type: micro_content
- frequency: daily
- length: short
- platforms: [twitter, linkedin, instagram]
- engagement: community_building

---

## 自定义SEO策略 (Custom SEO Strategy)

### on-page-seo
- keywords: long_tail
- density: 1-2%
- meta_tags: all
- content: quality_focused
- technical: optimized

### off-page-seo
- backlinks: quality_over_quantity
- social_signals: tracked
- guest_posting: regular
- pr: ongoing
- citations: consistent

### technical-seo
- site_speed: optimized
- mobile: responsive
- structure: hierarchical
- schema: markup
- sitemap: submitted

---

## 自定义邮件营销 (Custom Email Marketing)

### newsletter
- frequency: weekly
- content: curated
- segmentation: basic
- automation: minimal
- analytics: open_rates + click_rates

### drip-campaign
- trigger: user_action
- content: personalized
- segmentation: behavioral
- automation: full
- analytics: conversion_rates

### promotional
- frequency: monthly
- content: offers
- segmentation: purchase_history
- automation: scheduled
- analytics: revenue_attribution

---

## 自定义社交媒体 (Custom Social Media)

### organic-social
- platforms: [linkedin, twitter, instagram]
- frequency: daily
- content: mixed
- engagement: community_first
- analytics: engagement_metrics

### paid-social
- platforms: [linkedin, facebook, instagram]
- frequency: daily
- content: promotional
- engagement: conversion_focused
- analytics: roas

### community-management
- platforms: community_primary
- frequency: continuous
- content: responsive
- engagement: relationship_building
- analytics: sentiment_analysis

---

## 自定义转化优化 (Custom Conversion Optimization)

### a-b-testing
- tool: platform_native
- variants: 2-3
- duration: 2_weeks
- significance: 95%
- metrics: conversion_rate

### funnel-optimization
- stages: [awareness, interest, consideration, intent, evaluation, purchase]
- focus: drop_off_points
- optimization: iterative
- metrics: funnel_completion_rate

### personalization
- level: segment_based
- data: behavioral + demographic
- dynamic_content: enabled
- optimization: machine_learning
- metrics: lift_in_conversion

---

## 自定义分析指标 (Custom Analytics Metrics)

### awareness-metrics
- impressions: tracked
- reach: measured
- frequency: capped
- share_of_voice: monitored
- cost_per_impression: calculated

### consideration-metrics
- website_visits: tracked
- time_on_site: measured
- bounce_rate: monitored
- page_depth: tracked
- return_visits: segmented

### conversion-metrics
- leads: counted
- sales: tracked
- revenue: attributed
- cost_per_acquisition: calculated
- customer_lifetime_value: projected

---

## 自定义广告创意 (Custom Ad Creative)

### text-ads
- format: text_only
- headlines: multiple
- descriptions: multiple
- extensions: enabled
- responsive: keyword_based

### image-ads
- format: static_image
- creative: multiple_variations
- sizes: standard
- responsive: device_based
- testing: creative_rotation

### video-ads
- format: video
- duration: 6-60_seconds
- creative: multiple_variations
- CTAs: overlay_buttons
- testing: creative_testing

---

## 自定义受众定位 (Custom Audience Targeting)

### demographic-targeting
- age: ranges
- gender: all_or_specific
- income: brackets
- education: levels
- location: geo_targeted

### behavioral-targeting
- interests: categories
- intents: in_market
- life_events: milestones
- purchase_behavior: patterns
- device_usage: platforms

### custom-audiences
- source: website_visitors
- similarity: lookalike
- exclusion: excluded_audiences
- size: 1000-1000000
- refresh: 30_days

---

## 自定义预算配置 (Custom Budget Configuration)

### fixed-budget
- type: fixed
- amount: monthly
- allocation: manual
- optimization: none
- monitoring: monthly_review

### flexible-budget
- type: flexible
- amount: monthly_range
- allocation: dynamic
- optimization: automated
- monitoring: weekly_review

### performance-budget
- type: performance_based
- amount: roi_targeted
- allocation: algorithmic
- optimization: real_time
- monitoring: continuous

---

## 自定义ROI分析 (Custom ROI Analysis)

### basic-roas
- metric: return_on_ad_spend
- attribution: last_click
- window: 30_days
- frequency: monthly
- action: optimize_or_kill

### multi-touch-attribution
- model: data_driven
- attribution: [first_click, linear, time_decay]
- window: 90_days
- frequency: quarterly
- action: comprehensive_optimization

### customer-ltv
- metric: customer_lifetime_value
- cac: included
- payback_period: calculated
- frequency: monthly
- action: budget_reallocation

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/marketing-demand-acquisition/EXTEND.md`
- **用户级**: `~/.claude/skills/marketing-demand-acquisition/EXTEND.md`
- **默认级**: `skills/marketing-demand-acquisition/EXTEND.md`

---

## 使用示例

### 小企业营销
```markdown
## Small Business Marketing

### small-business
- channels: multi-channel
- paid_advertising: search-ads + social-ads
- content: blog-content + social-content
- seo: on-page-seo
- email: newsletter
- social_media: organic-social
- optimization: a-b-testing
- analytics: awareness-metrics + conversion-metrics
- creative: text-ads + image-ads
- targeting: demographic + behavioral
- budget: fixed-budget
- roi: basic-roas
```

### 增长黑客营销
```markdown
## Growth Hacking Marketing

### growth-hacking
- channels: omni-channel
- paid_advertising: all_platforms
- content: all_content_types
- seo: full_seo
- email: drip-campaign
- social_media: paid-social
- optimization: full_optimization
- analytics: full_analytics
- creative: video-ads
- targeting: advanced_audiences
- budget: performance-budget
- roi: multi-touch-attribution
```

### 企业级营销
```markdown
## Enterprise Marketing

### enterprise-marketing
- channels: omni-channel
- paid_advertising: enterprise_platforms
- content: full_content_strategy
- seo: technical_seo
- email: full_email_automation
- social_media: managed_community
- optimization: personalization
- analytics: custom_dashboard
- creative: full_production
- targeting: crm_integration
- budget: performance-budget
- roi: customer-ltv + multi-touch-attribution
```
