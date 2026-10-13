# User Persona Extractor EXTEND.md

## 默认用户画像配置

---

## 自定义数据维度 (Custom Data Dimensions)

### basic-demographics
- age: age_groups
- gender: binary_and_other
- location: province_level
- education: levels
- income: brackets

### detailed-demographics
- age: exact_ranges
- gender: inclusive_spectrum
- location: city_level
- education: specific_majors
- income: precise_ranges

### psychographics
- personality: big_five
- values: value_systems
- lifestyle: activity_patterns
- attitudes: opinion_dimensions
- interests: hierarchical_categories

### behavioral
- purchase: buying_patterns
- content: consumption_preferences
- engagement: interaction_styles
- loyalty: brand_affinity
- journey: touchpoint_mapping

---

## 自定义提取方法 (Custom Extraction Methods)

### explicit-extraction
- source: user_provided
- validation: direct_confirmation
- completeness: user_controlled
- privacy: opt_in

### behavioral-inference
- source: activity_patterns
- validation: statistical_confidence
- completeness: partial_filling
- privacy: aggregated

### content-analysis
- source: ugc_content
- validation: semantic_analysis
- completeness: probabilistic
- privacy: anonymized

### social-listening
- source: public_data
- validation: cross_reference
- completeness: crowd_sourced
- privacy: public_only

---

## 自定义聚类策略 (Custom Clustering Strategy)

### demographic-clustering
- method: k_means
- variables: demographic_only
- segments: 3_5
- labeling: descriptive_names

### psychographic-clustering
- method: hierarchical
- variables: psychological_factors
- segments: 5_8
- labeling: persona_names

### hybrid-clustering
- method: two_step
- variables: all_dimensions
- segments: 8_12
- labeling: persona_profiles

### needs-based-clustering
- method: latent_class
- variables: needs_pain_points
- segments: 4_6
- labeling: need_based_names

---

## 自定义画像模板 (Custom Persona Templates)

### minimal-persona
- sections: [name, demographics, goals]
- length: one_page
- detail: essential
- photo: avatar_icon

### standard-persona
- sections: [name, photo, demographics, psychographics, behaviors, needs]
- length: two_pages
- detail: comprehensive
- photo: stock_image

### rich-persona
- sections: [name, photo, story, demographics, psychographics, behaviors, needs, pain_points, scenarios, quotes]
- length: multi_page
- detail: vivid
- photo: custom_illustration

---

## 自定义验证方法 (Custom Validation Methods)

### internal-validation
- method: cross_validation
- sample: split_sample
- metrics: consistency_scores
- threshold: 0.7

### external-validation
- method: market_comparison
- sample: benchmark_data
- metrics: alignment_scores
- threshold: industry_benchmark

### expert-validation
- method: stakeholder_review
- sample: representative_set
- metrics: agreement_level
- threshold: consensus

### predictive-validation
- method: holdout_test
- sample: temporal_split
- metrics: prediction_accuracy
- threshold: 0.8

---

## 自定义更新频率 (Custom Update Frequency)

### static-personas
- update: manual_only
- trigger: project_initiation
- validation: periodic_review
- version: single_version

### dynamic-personas
- update: quarterly
- trigger: scheduled
- validation: automatic_checks
- version: versioned

### real-time-personas
- update: continuous
- trigger: data_changes
- validation: real_time
- version: living_document

---

## 自定义隐私保护 (Custom Privacy Protection)

### minimal-privacy
- anonymization: basic_hashing
- aggregation: none
- consent: implied
- retention: indefinite

### standard-privacy
- anonymization: pseudonymization
- aggregation: group_level
- consent: opt_out
- retention: 2_years

### strict-privacy
- anonymization: differential_privacy
- aggregation: minimum_group_size
- consent: opt_in
- retention: 90_days

### gdpr-compliant
- anonymization: full_anonymization
- aggregation: statistical_only
- consent: explicit_gdpr
- retention: right_to_deletion

---

## 自定义输出格式 (Custom Output Format)

### markdown-report
- format: markdown
- sections: hierarchical
- visuals: embedded_links
- distribution: static_file

### interactive-dashboard
- format: web_app
- sections: navigable
- visuals: interactive_charts
- distribution: hosted_url

### json-api
- format: json_schema
- sections: structured_data
- visuals: separate_urls
- distribution: rest_api

### presentation-slides
- format: slide_deck
- sections: slide_breaks
- visuals: prominent
- distribution: pdf_pptx

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/user-persona-extractor/EXTEND.md`
- **用户级**: `~/.claude/skills/user-persona-extractor/EXTEND.md`
- **默认级**: `skills/user-persona-extractor/EXTEND.md`

---

## 使用示例

### 快速用户画像
```markdown
## Quick Persona

### quick-persona
- dimensions: basic-demographics
- extraction: explicit-extraction
- clustering: demographic-clustering
- template: minimal-persona
- validation: internal-validation
- update: static-personas
- privacy: minimal-privacy
- output: markdown-report
```

### 完整用户研究
```markdown
## Full User Research

### full-research
- dimensions: all_dimensions
- extraction: all_methods
- clustering: hybrid-clustering
- template: rich-persona
- validation: all_validations
- update: dynamic-personas
- privacy: standard-privacy
- output: interactive-dashboard
```

### 敏感数据处理
```markdown
## GDPR Compliant Personas

### gdpr-personas
- dimensions: detailed-demographics + behavioral
- extraction: behavioral-inference
- clustering: needs-based-clustering
- template: standard-persona
- validation: expert-validation
- update: dynamic-personas
- privacy: gdpr-compliant
- output: json-api
```
