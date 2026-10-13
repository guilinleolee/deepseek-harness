# Client Finder Pro EXTEND.md

## 默认客户搜索配置

---

## 自定义搜索源 (Custom Search Sources)

### google-maps-only
- source: google_maps_api
- depth: basic_listings
- verification: none
- freshness: real_time

### multi-source
- source: [google, yelp, bing]
- depth: cross_referenced
- verification: automated
- freshness: cached

### deep-web
- source: all_available
- depth: comprehensive
- verification: multi_stage
- freshness: hybrid

---

## 自定义搜索策略 (Custom Search Strategy)

### radius-search
- method: geographic_radius
- center: user_specified
- radius: configurable
- sorting: distance

### keyword-search
- method: keyword_matching
- scope: all_fields
- matching: fuzzy
- sorting: relevance

### category-search
- method: industry_category
- taxonomy: standard_sic
- filter: hierarchical
- sorting: rating

---

## 自定义数据提取 (Custom Data Extraction)

### basic-info
- fields: [name, phone, address]
- enrichment: none
- verification: automated
- quality: standard

### standard-info
- fields: [name, contact, location, hours, website]
- enrichment: social_media
- verification: manual_review
- quality: enhanced

### comprehensive-info
- fields: all_available
- enrichment: full_profile
- verification: multi_source
- quality: premium

---

## 自定义导出格式 (Custom Export Format)

### csv-export
- format: csv
- encoding: utf8_bom
- delimiter: comma
- headers: standard

### excel-export
- format: xlsx
- encoding: native
- sheets: single
- formatting: basic

### crm-export
- format: crm_specific
- encoding: utf8
- mapping: preconfigured
- validation: schema_based

---

## 自定义CRM集成 (Custom CRM Integration)

### generic-csv
- target: generic_csv_import
- mapping: manual
- validation: none
- sync: one_time

### salesforce
- target: salesforce_api
- mapping: auto_mapped
- validation: field_validation
- sync: real_time

### chinese-crm
- target: [weCom, dingTalk, feishu]
- mapping: localized
- validation: chinese_format
- sync: api_push

---

## 自定义去重策略 (Custom Deduplication Strategy)

### no-dedup
- enabled: false
- method: none
- threshold: n/a
- action: keep_all

### fuzzy-dedup
- enabled: true
- method: similarity_score
- threshold: 0.85
- action: flag_review

### strict-dedup
- enabled: true
- method: exact_match
- threshold: 1.0
- action: auto_remove

---

## 自定义数据验证 (Custom Data Validation)

### no-validation
- enabled: false
- checks: none
- correction: none
- reporting: none

### format-validation
- enabled: true
- checks: [phone_format, email_format, address_format]
- correction: auto_format
- reporting: error_summary

### existence-validation
- enabled: true
- checks: [reachable_numbers, valid_emails]
- correction: flag_only
- reporting: detailed_report

---

## 自定义搜索限制 (Custom Search Limits)

### free-tier
- api_quota: 100_day
- rate_limit: 10_minute
- depth: page_1
- features: basic

### professional-tier
- api_quota: 1000_day
- rate_limit: 100_minute
- depth: all_pages
- features: standard

### enterprise-tier
- api_quota: unlimited
- rate_limit: 1000_minute
- depth: unlimited
- features: all_features

---

## 自定义结果排序 (Custom Result Sorting)

### distance-sort
- primary: distance
- secondary: rating
- tertiary: name
- custom: none

### rating-sort
- primary: rating_count
- secondary: avg_rating
- tertiary: distance
- custom: none

### relevance-sort
- primary: match_score
- secondary: freshness
- tertiary: popularity
- custom: weighted

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/client-finder-pro/EXTEND.md`
- **用户级**: `~/.claude/skills/client-finder-pro/EXTEND.md`
- **默认级**: `skills/client-finder-pro/EXTEND.md`

---

## 使用示例

### 本地商户搜索
```markdown
## Local Business Search

### local-search
- source: google-maps-only
- strategy: radius-search
- extraction: basic-info
- export: csv-export
- crm: generic-csv
- dedup: fuzzy-dedup
- validation: format-validation
- limits: free-tier
- sorting: distance-sort
```

### 销售线索收集
```markdown
## Sales Lead Collection

### lead-collection
- source: multi-source
- strategy: category-search
- extraction: standard-info
- export: crm-export
- crm: salesforce
- dedup: strict-dedup
- validation: existence-validation
- limits: professional-tier
- sorting: rating-sort
```

### 企业级客户获取
```markdown
## Enterprise Client Acquisition

### enterprise-acquisition
- source: deep-web
- strategy: keyword-search
- extraction: comprehensive-info
- export: crm-export
- crm: chinese-crm
- dedup: strict-dedup
- validation: existence-validation
- limits: enterprise-tier
- sorting: relevance-sort
```
