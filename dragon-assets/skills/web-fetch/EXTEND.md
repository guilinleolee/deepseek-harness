# Web Fetch EXTEND.md

## 默认网页抓取配置

---

## 自定义请求方法 (Custom Request Method)

### simple-get
- method: GET
- headers: minimal
- body: none
- follow_redirects: true

### authenticated-get
- method: GET
- headers: with_auth
- body: none
- follow_redirects: true

### post-request
- method: POST
- headers: content_type
- body: json_or_form
- follow_redirects: false

---

## 自定义请求头 (Custom Request Headers)

### minimal-headers
- user_agent: default
- accept: text/html
- encoding: gzip
- custom: none

### browser-headers
- user_agent: realistic_browser
- accept: all_types
- encoding: gzip_br
- custom: common_headers

### custom-headers
- user_agent: user_defined
- accept: user_specified
- encoding: user_choice
- custom: full_control

---

## 自定义认证方式 (Custom Authentication)

### no-auth
- type: none
- credentials: none
- token: none
- session: none

### basic-auth
- type: basic
- credentials: username_password
- token: none
- session: stateless

### bearer-token
- type: bearer
- credentials: none
- token: header_token
- session: stateless

### session-auth
- type: cookie_based
- credentials: initial_login
- token: cookie
- session: maintained

### api-key
- type: api_key
- credentials: none
- token: header_or_query
- session: stateless

---

## 自定义超时配置 (Custom Timeout Config)

### quick-timeout
- connect: 5_seconds
- read: 10_seconds
- total: 15_seconds
- retry: none

### standard-timeout
- connect: 10_seconds
- read: 30_seconds
- total: 60_seconds
- retry: 3_attempts

### generous-timeout
- connect: 30_seconds
- read: 120_seconds
- total: 300_seconds
- retry: unlimited

---

## 自定义重试策略 (Custom Retry Strategy)

### no-retry
- enabled: false
- on: none
- backoff: none
- max_attempts: 1

### linear-retry
- enabled: true
- on: [timeout, 5xx]
- backoff: linear
- max_attempts: 3

### exponential-retry
- enabled: true
- on: [timeout, 5xx, network_error]
- backoff: exponential
- max_attempts: 5

---

## 自定义内容解析 (Custom Content Parsing)

### text-only
- format: plain_text
- encoding: utf8
- cleanup: minimal
- structure: none

### html-parsed
- format: html
- encoding: auto_detect
- cleanup: formatted
- structure: dom_tree

### markdown-converted
- format: markdown
- encoding: utf8
- cleanup: readable
- structure: headers

### json-extracted
- format: json
- encoding: utf8
- cleanup: structured
- structure: schema_based

---

## 自定义错误处理 (Custom Error Handling)

### fail-fast
- strategy: raise_immediately
- logging: error_only
- recovery: manual
- details: minimal

### retry-then-fail
- strategy: retry_then_raise
- logging: attempt_details
- recovery: automatic_retry
- details: standard

### resilient
- strategy: best_effort
- logging: comprehensive
- recovery: graceful_degradation
- details: verbose

---

## 自定义缓存策略 (Custom Caching Strategy)

### no-cache
- enabled: false
- ttl: 0
- storage: none
- validation: none

### memory-cache
- enabled: true
- ttl: 5_minutes
- storage: ram
- validation: time_based

### disk-cache
- enabled: true
- ttl: 1_hour
- storage: disk
- validation: etag_based

### smart-cache
- enabled: true
- ttl: adaptive
- storage: disk
- validation: conditional_headers

---

## 自定义代理配置 (Custom Proxy Config)

### no-proxy
- enabled: false
- http_proxy: none
- https_proxy: none
- bypass: none

### http-proxy
- enabled: true
- http_proxy: specified
- https_proxy: same_as_http
- bypass: local_addresses

### socks-proxy
- enabled: true
- http_proxy: socks5
- https_proxy: socks5
- bypass: none

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/web-fetch/EXTEND.md`
- **用户级**: `~/.claude/skills/web-fetch/EXTEND.md`
- **默认级**: `skills/web-fetch/EXTEND.md`

---

## 使用示例

### 简单网页抓取
```markdown
## Simple Web Fetch

### simple-fetch
- method: simple-get
- headers: minimal-headers
- auth: no-auth
- timeout: quick-timeout
- retry: no-retry
- parsing: text-only
- errors: fail-fast
- cache: no-cache
- proxy: no-proxy
```

### API 请求
```markdown
## API Request

### api-request
- method: authenticated-get
- headers: custom-headers
- auth: bearer-token
- timeout: standard-timeout
- retry: exponential-retry
- parsing: json-extracted
- errors: retry-then-fail
- cache: memory-cache
- proxy: no-proxy
```

### 健壮的爬虫
```markdown
## Resilient Scraper

### resilient-scraper
- method: browser-headers
- headers: browser-headers
- auth: session-auth
- timeout: generous-timeout
- retry: exponential-retry
- parsing: markdown-converted
- errors: resilient
- cache: smart-cache
- proxy: socks-proxy
```
