# Web Scraping Scrapling EXTEND.md

## 默认Scrapling爬虫配置

---

## 自定义爬取策略 (Custom Scraping Strategy)

### static-scraping
- method: http_requests_only
- javascript: none
- complexity: low
- reliability: high_for_static_sites

### dynamic-scraping
- method: headless_browser
- javascript: fully_executed
- complexity: high
- reliability: high_for_dynamic_sites

### hybrid-scraping
- method: adaptive_selection
- javascript: as_needed
- complexity: medium
- reliability: balanced

---

## 自定义解析引擎 (Custom Parsing Engine)

### regex-parsing
- method: pattern_matching
- flexibility: low
- maintenance: fragile
- learning_curve: low

### css-selector-parsing
- method: element_selection
- flexibility: medium
- maintenance: moderate
- learning_curve: low

### xpath-parsing
- method: path_based_selection
- flexibility: high
- maintenance: robust
- learning_curve: medium

### ml-parsing
- method: semantic_understanding
- flexibility: very_high
- maintenance: adaptive
- learning_curve: high

---

## 自定义并发控制 (Custom Concurrency Control)

### sequential
- parallelism: 1_request_at_a_time
- resource_usage: minimal
- speed: slow
- server_load: minimal

### moderate-concurrency
- parallelism: 5_10_requests
- resource_usage: moderate
- speed: moderate
- server_load: manageable

### aggressive-concurrency
- parallelism: 20_50_requests
- resource_usage: high
- speed: fast
- server_load: high

---

## 自定义速率限制 (Custom Rate Limiting)

### no-limit
- requests_per_second: unlimited
- politeness: none
- risk: blocking_likely
- use_case: isolated_tests

### conservative-limit
- requests_per_second: 1_2
- politeness: high
- risk: minimal
- use_case: production_scraping

### adaptive-limit
- requests_per_second: varies_by_response
- politeness: responsive
- risk: balanced
- use_case: intelligent_scraping

---

## 自定义错误处理 (Custom Error Handling)

### fail-fast
- strategy: stop_on_first_error
- recovery: none
- logging: error_only
- completeness: partial_likely

### retry-with-backoff
- strategy: exponential_backoff
- recovery: automatic_retry
- logging: retry_attempts
- completeness: improved

### resilient-scraping
- strategy: multiple_fallbacks
- recovery: full_recovery_mechanisms
- logging: comprehensive
- completeness: high

---

## 自定义数据存储 (Custom Data Storage)

### in-memory
- persistence: session_only
- size: limited_by_ram
- format: python_objects
- export: manual

### file-based
- persistence: disk_storage
- size: limited_by_disk
- format: json_csv
- export: immediate

### database-storage
- persistence: persistent_database
- size: scalable
- format: structured_tables
- export: query_based

---

## 自定义反爬检测 (Custom Anti-Detection)

### basic-browser
- user_agent: standard_browser
- headers: minimal
- behavior: human_like
- detection_risk: medium

### stealth-mode
- user_agent: rotated_realistic
- headers: complete_browser_headers
- behavior: randomized_human_patterns
- detection_risk: low

### undetected-mode
- user_agent: latest_browser
- headers: full_browser_fingerprint
- behavior: browser_automation_evasion
- detection_risk: very_low

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/web-scraping-scrapling/EXTEND.md`
- **用户级**: `~/.claude/skills/web-scraping-scrapling/EXTEND.md`
- **默认级**: `skills/web-scraping-scrapling/EXTEND.md`

---

## 使用示例

### 简单静态抓取
```markdown
## Simple Static Scraping

### simple-static
- strategy: static-scraping
- parsing: css-selector-parsing
- concurrency: sequential
- rate-limit: conservative-limit
- error-handling: fail-fast
- storage: file-based
- anti-detection: basic-browser
```

### 动态网站抓取
```markdown
## Dynamic Website Scraping

### dynamic-scraping
- strategy: dynamic-scraping
- parsing: xpath-parsing
- concurrency: moderate-concurrency
- rate-limit: adaptive-limit
- error-handling: retry-with-backoff
- storage: database-storage
- anti-detection: stealth-mode
```

### 企业级大规模抓取
```markdown
## Enterprise Scale Scraping

### enterprise-scale
- strategy: hybrid-scraping
- parsing: ml-parsing
- concurrency: aggressive-concurrency
- rate-limit: adaptive-limit
- error-handling: resilient-scraping
- storage: database-storage
- anti-detection: undetected-mode
```
