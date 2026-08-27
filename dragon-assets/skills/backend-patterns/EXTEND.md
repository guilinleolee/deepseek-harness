# Backend Patterns EXTEND.md

## 默认后端模式配置

---

## 自定义架构风格

### mvc-pattern
- separation: model_view_controller
- routing: controller_based
- complexity: moderate
- scale: monolithic

### clean-architecture
- separation: layers_entities_use_cases
- routing: use_case_driven
- complexity: high
- scale: monolithic_modular

### microservices
- separation: service_boundaries
- routing: api_gateway
- complexity: very_high
- scale: distributed

### serverless
- separation: function_boundaries
- routing: event_triggers
- complexity: variable
- scale: cloud_native

---

## 自定义API设计

### rest-api
- protocol: http_restful
- serialization: json
- state: stateless
- real_time: polling_required

### graphql-api
- protocol: http_graphql
- serialization: graphql_schema
- state: stateless
- real_time: subscriptions_optional

### grpc-api
- protocol: http_2_protobuf
- serialization: protocol_buffers
- state: stateless
- real_time: bidirectional_streams

### event-driven
- protocol: message_queue
- serialization: event_payload
- state: event_sourcing
- real_time: native

---

## 自定义数据库策略

### sql-database
- type: postgresql_mysql
- schema: rigid_relational
- transactions: acid_compliant
- scaling: vertical_read_replicas

### nosql-document
- type: mongodb_firestore
- schema: flexible_documents
- transactions: eventual_consistency
- scaling: horizontal_sharding

### nosql-keyvalue
- type: redis_dynamodb
- schema: none
- transactions: atomic_operations
- scaling: horizontal_partitioning

### graph-database
- type: neo4j
- schema: graph_nodes_edges
- transactions: acid_properties
- scaling: horizontal_distribution

---

## 自定义认证方式

### session-auth
- method: cookie_sessions
- storage: server_side
- scaling: sticky_session_required
- security: csrf_protection_needed

### jwt-auth
- method: bearer_tokens
- storage: client_side
- scaling: stateless_horizontal
- security: token_validation_required

### oauth2-sso
- method: third_party_identity
- storage: provider_managed
- scaling: provider_infrastructure
- security: delegated_trust

### api-key-auth
- method: header_keys
- storage: database_lookup
- scaling: simple_verification
- security: key_rotation_needed

---

## 自定义错误处理

### throw-propagate
- strategy: exception_bubbling
- logging: catch_blocks
- user_message: generic
- debugging: stack_traces

### result-type
- strategy: explicit_result_objects
- logging: at_boundaries
- user_message: typed_results
- debugging: predictable

### problem-details
- strategy: rfc_7807_compliant
- logging: structured_logs
- user_message: machine_readable
- debugging: standardized

---

## 自定义缓存策略

### no-cache
- approach: always_fresh_data
- ttl: none
- invalidation: not_applicable
- performance: database_bound

### in-memory-cache
- approach: process_local_cache
- ttl: short_duration
- invalidation: time_based
- performance: fast_but_limited

### distributed-cache
- approach: redis_memcached
- ttl: configurable
- invalidation: event_based
- performance: fast_scalable

### cdn-cache
- approach: edge_caching
- ttl: long_duration
- invalidation: purging
- performance: global_speed

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 快速REST API
- architecture: mvc-pattern
- api: rest-api
- database: sql-database
- auth: jwt-auth
- errors: throw-propagate
- cache: no-cache

### 现代GraphQL服务
- architecture: clean-architecture
- api: graphql-api
- database: nosql-document
- auth: oauth2-sso
- errors: problem-details
- cache: distributed-cache

### 微服务架构
- architecture: microservices
- api: grpc-api
- database: sql-database_per_service
- auth: jwt-auth
- errors: result-type
- cache: in-memory-cache
