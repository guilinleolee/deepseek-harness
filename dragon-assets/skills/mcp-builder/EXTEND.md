# MCP Builder EXTEND.md

## 默认 MCP 构建配置

---

## 自定义服务器类型 (Custom Server Type)

### stdio-server
- transport: stdio
- communication: jsonrpc
- lifecycle: parent_managed
- platform: all_platforms

### sse-server
- transport: http_sse
- communication: event_stream
- lifecycle: independent
- platform: web_only

### websocket-server
- transport: ws
- communication: bidirectional
- lifecycle: independent
- platform: web_and_desktop

---

## 自定义工具定义 (Custom Tool Definition)

### query-tool
- type: read_only
- input_schema: strict_validation
- output: structured_response
- error_handling: graceful

### action-tool
- type: write
- input_schema: loose_validation
- output: status_response
- error_handling: detailed

### stream-tool
- type: streaming
- input_schema: minimal
- output: chunked_response
- error_handling: real_time

---

## 自定义资源定义 (Custom Resource Definition)

### file-resource
- type: file
- mime_type: auto_detect
- caching: etag_based
- watching: disabled

### directory-resource
- type: directory
- mime_type: directory
- caching: ttl_based
- watching: enabled

### api-resource
- type: dynamic
- mime_type: json
- caching: header_based
- watching: disabled

---

## 自定义提示词模板 (Custom Prompt Template)

### instruction-prompt
- type: instruction
- arguments: required
- validation: strict
- temperature: fixed

### template-prompt
- type: template
- arguments: optional
- validation: relaxed
- temperature: configurable

### resource-prompt
- type: resource_reference
- arguments: uri_based
- validation: uri_validation
- temperature: not_applicable

---

## 自定义日志配置 (Custom Logging Config)

### minimal-logging
- level: errors_only
- format: json
- destination: stderr
- rotation: disabled

### standard-logging
- level: info
- format: structured
- destination: file
- rotation: daily

### verbose-logging
- level: debug
- format: detailed
- destination: file
- rotation: hourly

---

## 自定义错误处理 (Custom Error Handling)

### silent-errors
- display: none
- logging: internal
- recovery: automatic
- user_feedback: disabled

### friendly-errors
- display: user_friendly
- logging: detailed
- recovery: suggested
- user_feedback: hints

### technical-errors
- display: raw_error
- logging: verbose
- recovery: manual
- user_feedback: stack_trace

---

## 自定义认证配置 (Custom Authentication Config)

### no-auth
- method: none
- validation: disabled
- tokens: none
- rate_limit: disabled

### api-key-auth
- method: header
- validation: required
- tokens: single_key
- rate_limit: standard

### oauth-auth
- method: oauth2
- validation: token_validation
- tokens: refresh_tokens
- rate_limit: per_user

---

## 自定义缓存策略 (Custom Caching Strategy)

### no-cache
- enabled: false
- ttl: 0
- invalidation: none
- storage: none

### memory-cache
- enabled: true
- ttl: 300_seconds
- invalidation: time_based
- storage: in_memory

### persistent-cache
- enabled: true
- ttl: 3600_seconds
- invalidation: smart
- storage: disk

---

## 自定义代码生成 (Custom Code Generation)

### typescript-server
- language: typescript
- framework: official_sdk
- style: strict_typed
- testing: included

### python-server
- language: python
- framework: official_sdk
- style: pep8
- testing: included

### go-server
- language: go
- framework: community
- style: idiomatic
- testing: included

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/mcp-builder/EXTEND.md`
- **用户级**: `~/.claude/skills/mcp-builder/EXTEND.md`
- **默认级**: `skills/mcp-builder/EXTEND.md`

---

## 使用示例

### 简单工具服务器
```markdown
## Simple Tool Server

### simple-server
- server: stdio-server
- tools: query-tool
- resources: file-resource
- prompts: instruction-prompt
- logging: minimal-logging
- errors: friendly-errors
- auth: no-auth
- cache: memory-cache
- code: typescript-server
```

### 完整生产服务器
```markdown
## Production Server

### production-server
- server: sse-server
- tools: all_tools
- resources: all_resources
- prompts: all_prompts
- logging: verbose-logging
- errors: technical-errors
- auth: oauth-auth
- cache: persistent-cache
- code: typescript-server
```

### 开发原型服务器
```markdown
## Development Prototype

### dev-prototype
- server: stdio-server
- tools: action-tool
- resources: api-resource
- prompts: template-prompt
- logging: standard-logging
- errors: friendly-errors
- auth: api-key-auth
- cache: no-cache
- code: python-server
```
