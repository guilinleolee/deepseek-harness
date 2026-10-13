# Architect EXTEND.md

## 默认架构师配置

---

## 自定义架构模式 (Custom Architecture Patterns)

### layered-architecture
- layers: [presentation, business, data, infrastructure]
- dependency_direction: downward_only
- separation: strict
- cross_cutting: [logging, validation, caching]

### hexagonal-architecture
- core: domain_logic
- ports: interfaces
- adapters: implementations
- dependency_inversion: enforced

### onion-architecture
- center: domain_entities
- layers: concentric
- dependency_rule: inward_only
- testability: high

### clean-architecture
- entities: core
- use_cases: application
- interface_adapters: presentation
- frameworks: external

---

## 自定义系统分解 (Custom System Decomposition)

### monolithic
- structure: single_codebase
- deployment: one_unit
- scaling: vertical
- complexity: low
- team_size: small

### modular-monolith
- structure: bounded_contexts
- deployment: one_unit
- scaling: module_level
- complexity: medium
- team_size: medium

### microservices
- structure: distributed_services
- deployment: per_service
- scaling: per_service
- complexity: high
- team_size: large
- communication: api_based

### serverless
- structure: functions
- deployment: per_function
- scaling: automatic
- complexity: medium
- team_size: small_to_medium
- execution: event_driven

---

## 自定义数据架构 (Custom Data Architecture)

### relational-database
- type: rdbms
- normalization: 3nf
- acid: enforced
- scaling: vertical
- examples: [postgresql, mysql]

### document-database
- type: nosql_document
- schema: flexible
- acid: eventual_consistency
- scaling: horizontal
- examples: [mongodb, couchdb]

### key-value-store
- type: nosql_kv
- schema: none
- acid: tunable
- scaling: horizontal
- examples: [redis, dynamodb]

### graph-database
- type: nosql_graph
- schema: flexible
- acid: configurable
- scaling: horizontal
- examples: [neo4j, arangodb]

---

## 自定义API设计 (Custom API Design)

### rest-api
- style: rest
- format: json
- versioning: url_based
- documentation: openapi
- state: server_side

### graphql-api
- style: graphql
- format: json
- versioning: schema_based
- documentation: graphql
- state: client_controlled

### grpc-api
- style: grpc
- format: protobuf
- versioning: proto_based
- documentation: proto_comments
- state: server_side

### event-driven-api
- style: events
- format: json/cloud_events
- versioning: schema_registry
- documentation: asyncapi
- state: event_sourced

---

## 自定义安全架构 (Custom Security Architecture)

### zero-trust
- principle: never_trust_always_verify
- identity: central_idp
- network: micro_segmentation
- data: encryption_everywhere
- monitoring: continuous

### defense-in-depth
- layers: [network, host, application, data]
- principle: multiple_controls
- redundancy: built_in
- fail_safe: default_deny

### devsecops
- shift_left: security_in_ci_cd
- automation: security_scans
- policy: code_defined
- monitoring: runtime_protection

---

## 自定义扩展策略 (Custom Scalability Strategy)

### vertical-scaling
- type: scale_up
- approach: bigger_machines
- complexity: low
- cost: linear
- limits: hardware

### horizontal-scaling
- type: scale_out
- approach: more_machines
- complexity: high
- cost: linear
- limits: infinite

### caching-strategy
- type: cache
- levels: [browser, cdn, application, data]
- invalidation: ttl_based
- consistency: eventual

---

## 自定义容错设计 (Custom Fault Tolerance)

### redundancy
- approach: active_passive
- failover: automatic
- consistency: strong
- rpo: zero
- rto: minutes

### circuit-breaker
- states: [closed, open, half_open]
- threshold: 5_failures
- timeout: 30_seconds
- fallback: degraded_service

### retry-pattern
- strategy: exponential_backoff
- max_attempts: 3
- base_delay: 1_second
- max_delay: 30_seconds
- jitter: added

---

## 自定义监控可观测性 (Custom Monitoring Observability)

### metrics
- type: numerical
- aggregation: histogram
- granularity: 1_second
- retention: 30_days
- alerting: threshold_based

### logging
- format: structured_json
- level: configurable
- correlation: trace_id
- retention: 7_days
- search: full_text

### tracing
- system: distributed_tracing
- span_duration: recorded
- context: propagated
- retention: 7_days
- visualization: dependency_graph

---

## 自定义部署策略 (Custom Deployment Strategy)

### blue-green-deployment
- environments: 2
- switch: instant
- rollback: instant
- risk: low
- resource_usage: 2x

### canary-deployment
- phases: incremental
- traffic_percentage: [1, 5, 25, 50, 100]
- rollback: gradual
- risk: medium
- resource_usage: 1.5x

### rolling-deployment
- phases: incremental
- batch_size: 25%
- rollback: gradual
- risk: medium
- resource_usage: 1x

### feature-flags
- deployment: decoupled
- release: gradual
- rollback: instant
- risk: very_low
- complexity: high

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/architect/EXTEND.md`
- **用户级**: `~/.claude/skills/architect/EXTEND.md`
- **默认级**: `skills/architect/EXTEND.md`

---

## 使用示例

### 小型Web应用
```markdown
## Small Web App

### small-web-app
- architecture: layered-architecture
- decomposition: monolithic
- data: relational-database
- api: rest-api
- security: defense-in-depth
- scalability: vertical-scaling + caching-strategy
- fault_tolerance: retry-pattern
- observability: [metrics, logging]
- deployment: blue-green-deployment
```

### 微服务平台
```markdown
## Microservices Platform

### microservices-platform
- architecture: clean-architecture
- decomposition: microservices
- data: document-database + key-value-store
- api: graphql-api + event-driven-api
- security: zero-trust
- scalability: horizontal-scaling + caching-strategy
- fault_tolerance: circuit-breaker + retry-pattern
- observability: [metrics, logging, tracing]
- deployment: canary-deployment + feature-flags
```

### 无服务器架构
```markdown
## Serverless Architecture

### serverless-architecture
- architecture: hexagonal-architecture
- decomposition: serverless
- data: document-database
- api: rest-api + event-driven-api
- security: devsecops
- scalability: horizontal-scaling
- fault_tolerance: retry-pattern
- observability: [metrics, logging, tracing]
- deployment: feature-flags
```
