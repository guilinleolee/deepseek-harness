# GraphQL Schema EXTEND.md

## 默认GraphQL配置

---

## 自定义查询复杂度

### simple-queries
- depth: 3_levels_max
- fields: 20_per_query
- complexity: linear
- estimation: static

### complex-queries
- depth: 7_levels_max
- fields: 50_per_query
- complexity: calculated
- estimation: dynamic

### unbounded-queries
- depth: no_limit
- fields: unlimited
- complexity: not_enforced
- estimation: none

---

## 自定义类型生成

### basic-types
- scalars: [String, Int, Boolean, Float, ID]
- enums: none
- unions: none
- interfaces: none

### rich-types
- scalars: [all_primitives_plus_custom]
- enums: defined
- unions: selective
- interfaces: minimal

### schema-first
- scalars: comprehensive_custom
- enums: extensive
- unions: frequent
- interfaces: heavily_used

---

## 自定义解析策略

### per-field-resolvers
- approach: field_level_functions
- batching: none
- caching: resolver_scope
- performance: n_plus_1_risk

### dataloader-pattern
- approach: batched_resolvers
- batching: automatic
- caching: built_in
- performance: optimized

### delegated-resolving
- approach: schema_stitching
- batching: cross_service
- caching: distributed
- performance: variable

---

## 自定义认证方式

### public-schema
- auth: none
- protection: open_access
- validation: none
- rate_limit: none

### api-key-auth
- auth: header_based_key
- protection: schema_level
- validation: key_validation
- rate_limit: per_key

### directive-auth
- auth: field_level_directives
- protection: granular
- validation: custom_logic
- rate_limit: per_user_role

---

## 自定义错误处理

### expose-errors
- strategy: raw_errors
- masking: none
- debugging: detailed
- security: low

### sanitized-errors
- strategy: safe_messages
- masking: filtered_paths
- debugging: general
- security: medium

### generic-errors
- strategy: uniform_response
- masking: complete
- debugging: minimal
- security: high

---

## 自定义分页方式

### offset-pagination
- method: limit_offset
- cursor: none
- bi_directional: no
- complexity: simple

### cursor-pagination
- method: opaque_cursor
- cursor: encoded
- bi_directional: optional
- complexity: moderate

### relay-pagination
- method: connection_spec
- cursor: base64_encoded
- bi_directional: yes
- complexity: complex_but_complete

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 简单API
- queries: simple-queries
- types: basic-types
- resolving: per-field-resolvers
- auth: public-schema
- errors: expose-errors
- pagination: offset-pagination

### 生产GraphQL
- queries: complex-queries
- types: rich-types
- resolving: dataloader-pattern
- auth: directive-auth
- errors: sanitized-errors
- pagination: cursor-pagination

### 微服务GraphQL
- queries: complex-queries
- types: schema-first
- resolving: delegated-resolving
- auth: directive-auth
- errors: generic-errors
- pagination: relay-pagination
