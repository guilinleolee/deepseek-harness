# n8n Skill EXTEND.md

## 默认 n8n 工作流配置

---

## 自定义节点类型 (Custom Node Types)

### core-nodes
- built_in: [trigger, action, flow]
- custom_nodes: none
- community_nodes: disabled
- version: latest_stable

### extended-nodes
- built_in: all_core
- custom_nodes: enabled
- community_nodes: curated_list
- version: controlled

### full-ecosystem
- built_in: all_available
- custom_nodes: unlimited
- community_nodes: all_community
- version: bleeding_edge

---

## 自定义触发器 (Custom Triggers)

### time-based
- type: schedule
- precision: minute
- timezone: utc
- recurrence: cron_expression

### event-based
- type: webhook
- authentication: none
- rate_limit: none
- validation: basic

### hybrid-trigger
- type: polling_plus_webhook
- authentication: optional
- rate_limit: configured
- validation: strict

---

## 自定义数据流 (Custom Data Flow)

### linear-flow
- structure: sequential
- branching: none
- parallel: disabled
- error_handling: stop_on_error

### branching-flow
- structure: conditional
- branching: if_else_switch
- parallel: disabled
- error_handling: error_output

### complex-flow
- structure: graph
- branching: complex_logic
- parallel: split_in_batches
- error_handling: retry_continue

---

## 自定义数据转换 (Custom Data Transformation)

### pass-through
- transformation: none
- mapping: direct_passthrough
- validation: none
- enrichment: disabled

### basic-transform
- transformation: set_function
- mapping: field_mapping
- validation: type_check
- enrichment: basic_lookup

### advanced-transform
- transformation: code_mode
- mapping: complex_logic
- validation: schema_validation
- enrichment: api_enrichment

---

## 自定义认证管理 (Custom Auth Management)

### hardcoded-auth
- storage: credentials_in_node
- encryption: none
- rotation: manual
- sharing: not_recommended

### credential-store
- storage: centralized_vault
- encryption: encrypted_at_rest
- rotation: manual
- sharing: workspace_scoped

### external-vault
- storage: external_secret_manager
- encryption: aes_256
- rotation: automatic_policies
- sharing: role_based

---

## 自定义错误处理 (Custom Error Handling)

### fail-fast
- strategy: stop_workflow
- logging: error_log_only
- retry: 0
- recovery: manual_restart

### retry-strategy
- strategy: retry_with_backoff
- logging: attempt_logs
- retry: 3_attempts
- recovery: automatic

### resilient-execution
- strategy: continue_on_error
- logging: comprehensive
- retry: exponential_backoff
- recovery: error_branch

---

## 自定义版本控制 (Custom Version Control)

### no-versioning
- git: disabled
- history: none
- rollback: manual
- collaboration: overwrite

### basic-versioning
- git: read_only_snapshot
- history: current_only
- rollback: to_previous_version
- collaboration: locking

### full-versioning
- git: full_integration
- history: complete_history
- rollback: any_version
- collaboration: branch_merge

---

## 自定义监控告警 (Custom Monitoring & Alerting)

### no-monitoring
- metrics: none
- execution: silent
- failures: logged_only
- notifications: disabled

### basic-monitoring
- metrics: execution_count
- execution: success_rate
- failures: error_logs
- notifications: email_on_failure

### full-monitoring
- metrics: all_metrics
- execution: performance_dashboard
- failures: error_analytics
- notifications: multi_channel_alerts

---

## 自定义部署环境 (Custom Deployment Environment)

### self-hosted
- hosting: on_premise
- scaling: manual
- high_availability: single_instance
- security: network_isolated

### cloud-instance
- hosting: managed_cloud
- scaling: vertical
- high_availability: basic_redundancy
- security: provider_managed

### enterprise-cluster
- hosting: kubernetes_cluster
- scaling: auto_horizontal
- high_availability: multi_region
- security: enterprise_grade

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/n8n-skill/EXTEND.md`
- **用户级**: `~/.claude/skills/n8n-skill/EXTEND.md`
- **默认级**: `skills/n8n-skill/EXTEND.md`

---

## 使用示例

### 简单自动化
```markdown
## Simple Automation

### simple-automation
- nodes: core-nodes
- triggers: time-based
- flow: linear-flow
- transform: pass-through
- auth: hardcoded-auth
- errors: fail-fast
- versioning: no-versioning
- monitoring: no-monitoring
- deployment: self-hosted
```

### 业务工作流
```markdown
## Business Workflow

### business-workflow
- nodes: extended-nodes
- triggers: event-based
- flow: branching-flow
- transform: basic-transform
- auth: credential-store
- errors: retry-strategy
- versioning: basic-versioning
- monitoring: basic-monitoring
- deployment: cloud-instance
```

### 企业级集成
```markdown
## Enterprise Integration

### enterprise-integration
- nodes: full-ecosystem
- triggers: hybrid-trigger
- flow: complex-flow
- transform: advanced-transform
- auth: external-vault
- errors: resilient-execution
- versioning: full-versioning
- monitoring: full-monitoring
- deployment: enterprise-cluster
```
