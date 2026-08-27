# Validator EXTEND.md

## 默认代码验证配置

---

## 自定义验证维度

### critical-bugs
- focus: crashes_data_loss
- severity: blocking
- testing: edge_cases
- automation: full_regression

### security-audit
- focus: owasp_top_10
- severity: high
- tools: [snyk, eslint-security]
- reporting: vulnerability_report

### performance-review
- focus: load_time_memory
- severity: medium
- tools: [lighthouse, profiler]
- reporting: performance_metrics

### code-quality
- focus: maintainability_readability
- severity: low
- tools: [sonarqube, eslint]
- reporting: technical_debt

---

## 自定义测试深度

### smoke-testing
- scope: critical_paths
- time: quick_check
- coverage: 20%
- focus: happy_path

### integration-testing
- scope: module_boundaries
- time: medium_duration
- coverage: 60%
- focus: data_flow

### stress-testing
- scope: limits_breaking
- time: extended_duration
- coverage: 90%
- focus: edge_cases

---

## 自定义报告格式

### concise
- format: summary_only
- metrics: pass_fail_rate
- details: high_level
- audience: stakeholders

### detailed
- format: full_report
- metrics: comprehensive_coverage
- details: step_by_step
- audience: developers

### executive
- format: dashboard_visual
- metrics: risk_score_trends
- details: business_impact
- audience: management

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 快速冒烟测试
- config: smoke-testing
- report: concise

### 安全审计
- config: security-audit
- report: detailed

### 性能验证
- config: performance-review
- testing: integration-testing
- report: executive
