# Marketing Strategy PMM EXTEND.md

## 默认产品营销配置

---

## 自定义市场定位 (Custom Market Positioning)

### cost-leader
- strategy: lowest_cost
- differentiation: price
- target: price_sensitive
- messaging: value_focused

### differentiation
- strategy: unique_features
- differentiation: quality_innovation
- target: quality_seekers
- messaging: feature_focused

### niche-focus
- strategy: specialized_segment
- differentiation: expertise
- target: specific_needs
- messaging: specialized_knowledge

---

## 自定义客户画像 (Custom ICP Definition)

### basic-icp
- demographics: firmographics
- psychographics: buying_behavior
- pain_points: general
- use_cases: typical

### detailed-icp
- demographics: detailed_firmographics
- psychographics: decision_factors
- pain_points: specific_challenges
- use_cases: comprehensive

### persona-based
- demographics: full_profile
- psychographics: personality_traits
- pain_points: emotional_rational
- use_cases: day_in_life

---

## 自定义竞品分析 (Custom Competitive Analysis)

### basic-landscape
- competitors: top_3
- features: feature_comparison
- pricing: price_comparison
- positioning: perceptual_map

### deep-analysis
- competitors: top_10
- features: feature_matrix
- pricing: tco_analysis
- positioning: strategy_canvas

### intelligence
- competitors: all_relevant
- features: gap_analysis
- pricing: dynamic_analysis
- positioning:预测_changes

---

## 自定义GTM策略 (Custom GTM Strategy)

### direct-sales
- channel: direct_sales_team
- cycle: enterprise_cycle
- pricing: quote_based
- support: high_touch

### product-led
- channel: self_service
- cycle: instant_access
- pricing: tiered_subscriptions
- support: community_plus_paid

### partner-driven
- channel: resellers_partners
- cycle: partner_managed
- pricing: partner_pricing
- support: partner_certified

---

## 自定义定价策略 (Custom Pricing Strategy)

### cost-plus
- method: cost_margin
- research: cost_analysis
- tiers: single_tier
- model: one_time

### value-based
- method: value_delivered
- research: willingness_to_pay
- tiers: multiple_tiers
- model: subscription

### dynamic-pricing
- method: algorithmic
- research: real_time_demand
- tiers: personalized
- model: hybrid

---

## 自定义消息框架 (Custom Messaging Framework)

### feature-focused
- structure: feature_benefit
- tone: descriptive
- proof: testimonials
- differentiation: feature_comparison

### benefit-focused
- structure: problem_solution
- tone: aspirational
- proof: case_studies
- differentiation: outcome_based

### value-story
- structure: hero_journey
- tone: emotional
- proof: roi_metrics
- differentiation: transformation

---

## 自定义渠道策略 (Custom Channel Strategy)

### single-channel
- focus: 1_channel
- integration: none
- attribution: last_click
- optimization: channel_specific

### multi-channel
- focus: 2_3_channels
- integration: basic
- attribution: linear
- optimization: cross_channel

### omnichannel
- focus: all_relevant
- integration: full
- attribution: data_driven
- optimization: holistic

---

## 自定义内容策略 (Custom Content Strategy)

### basic-content
- types: [blog, social]
- frequency: weekly
- distribution: owned_channels
- measurement: views_engagement

### content-marketing
- types: all_formats
- frequency: daily
- distribution: all_channels
- measurement: full_funnel

### content-operation
- types: personalized_content
- frequency: algorithmic
- distribution: dynamic
- measurement: attribution_based

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/marketing-strategy-pmm/EXTEND.md`
- **用户级**: `~/.claude/skills/marketing-strategy-pmm/EXTEND.md`
- **默认级**: `skills/marketing-strategy-pmm/EXTEND.md`

---

## 使用示例

### 早期创业公司
```markdown
## Early Stage Startup

### early-stage-strategy
- positioning: differentiation
- icp: basic-icp
- competitive: basic-landscape
- gtm: product-led
- pricing: value-based
- messaging: benefit-focused
- channels: single-channel
- content: basic-content
```

### 成长期公司
```markdown
## Growth Stage Company

### growth-stage-strategy
- positioning: differentiation
- icp: detailed-icp
- competitive: deep-analysis
- gtm: hybrid_model
- pricing: value-based
- messaging: value-story
- channels: multi-channel
- content: content-marketing
```

### 企业级公司
```markdown
## Enterprise Company

### enterprise-strategy
- positioning: niche-focus
- icp: persona-based
- competitive: intelligence
- gtm: direct-sales
- pricing: dynamic-pricing
- messaging: value-story
- channels: omnichannel
- content: content-operation
```
