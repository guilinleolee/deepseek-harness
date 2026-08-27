---
name: opf-report
description: OPF Report Command - 合规报告生成
invokable: true
---
# OPF Report Command - 合规报告生成

## 命令信息

**触发词**: `/opf-report`, `合规报告`, `隐私报告`

**权限**: 05安全师, 04验证师

**说明**: 生成隐私合规报告（GDPR/CCPA），支持定期报告自动化

## 语法

```
/opf-report <period> [--format pdf|html|markdown] [--output <file>] [--template <template>]
/opf-report custom --data <data_file> [--template <template>] [--output <file>]
```

## 参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `<period>` | enum | ✓ | 报告周期（daily/weekly/monthly/quarterly/yearly） |
| `--format` | enum | ✗ | 输出格式（默认markdown） |
| `--output` | 路径 | ✗ | 输出文件路径 |
| `--template` | 路径 | ✗ | 报告模板 |
| `--data` | 路径 | ✗ | 自定义数据文件 |

## 报告周期

| 周期 | 描述 | 触发时间 |
|------|------|---------|
| `daily` | 日报告 | 每日00:00 |
| `weekly` | 周报告 | 每周一00:00 |
| `monthly` | 月报告 | 每月1日00:00 |
| `quarterly` | 季报告 | 每季度首日00:00 |
| `yearly` | 年报告 | 每年1月1日00:00 |

## 报告内容

### 合规概览
- PII检测统计（按类型分布）
- 脱敏覆盖率趋势
- 违规风险评估
- 合规评分（GDPR/CCPA）

### 详细分析
- 高风险发现清单
- 敏感数据访问日志
- ETL处理统计
- 异常事件追踪

### 建议措施
- 技术改进建议
- 流程优化建议
- 合规差距分析
- 行动计划

## 使用示例

### 月度报告
```
/opf-report monthly --format markdown --output ./reports/privacy_monthly.md
```

### 季度PDF报告
```
/opf-report quarterly --format pdf --output ./reports/privacy_q1_2026.pdf
```

### 自定义数据报告
```
/opf-report custom --data ./audit_results.json --template ./templates/custom_report.yaml --output ./reports/custom_audit.md
```

## 报告模板

```yaml
# templates/quarterly_report.yaml
report:
  type: quarterly
  period: Q1 2026
  version: "1.0"
  generated: "2026-04-01T00:00:00Z"

sections:
  - name: executive_summary
    title: 执行摘要
    required: true

  - name: pii_statistics
    title: PII检测统计
    required: true
    charts:
      - type: pie
        title: PII类型分布
      - type: line
        title: 月度趋势

  - name: sanitization_coverage
    title: 脱敏覆盖率
    required: true
    metrics:
      - total_records
      - sanitized_records
      - coverage_rate

  - name: risk_assessment
    title: 风险评估
    required: true
    levels:
      - critical
      - high
      - medium
      - low

  - name: compliance_check
    title: 合规检查
    required: true
    frameworks:
      - GDPR
      - CCPA
      - PIPL

  - name: recommendations
    title: 改进建议
    required: true
    priority: high

  - name: appendix
    title: 附录
    required: false
```

## 输出格式

### Markdown报告结构
```markdown
# 隐私合规报告 - 2026年Q1

## 执行摘要
本报告涵盖2026年第一季度隐私保护合规情况...

## PII检测统计
| 指标 | 数值 | 环比变化 |
|------|------|---------|
| 总检测次数 | 1,234,567 | +12% |
| 发现PII | 45,678 | +8% |
| 脱敏成功 | 45,123 | +8% |
| 脱敏覆盖率 | 98.8% | +0.2% |

### PII类型分布
- private_email: 15,234 (33%)
- private_phone: 12,456 (27%)
- private_person: 8,901 (19%)
- private_address: 5,678 (12%)
- 其他: 3,409 (9%)

## 合规评分

| 框架 | 评分 | 状态 |
|------|------|------|
| GDPR | 92/100 | ✅ 符合 |
| CCPA | 88/100 | ⚠️ 需改进 |
| PIPL | 85/100 | ⚠️ 需改进 |

## 高风险发现

### 1. 配置文件敏感信息泄露
- 发现时间: 2026-01-15
- 影响范围: 23个配置文件
- 严重程度: 高
- 状态: 已修复

### 2. 测试数据包含真实PII
- 发现时间: 2026-02-20
- 影响范围: 5个测试数据集
- 严重程度: 中
- 状态: 处理中

## 改进建议

### 高优先级
1. 完善配置文件扫描机制
2. 建立测试数据脱敏标准
3. 加强员工隐私培训

### 中优先级
1. 优化ETL处理性能
2. 扩展PII检测规则库
3. 自动化报告生成流程

## 附录

### A. 报告生成信息
- 报告生成时间: 2026-04-01T00:00:00Z
- 数据来源: OPF Privacy Filter v1.0
- 报告版本: v1.0

### B. 合规框架说明
- GDPR: 欧盟通用数据保护条例
- CCPA: 加州消费者隐私法
- PIPL: 中国个人信息保护法
```

## 合规检查矩阵

| 合规项 | GDPR | CCPA | PIPL | 状态 |
|--------|------|------|------|------|
| 数据最小化 | ✓ | ✓ | ✓ | ✅ |
| 目的限制 | ✓ | ✓ | ✓ | ✅ |
| 存储限制 | ✓ | ✓ | ✓ | ⚠️ |
| 安全保障 | ✓ | ✓ | ✓ | ✅ |
| 主体权利 | ✓ | ✓ | ✓ | ⚠️ |
| 数据泄露通知 | ✓ | ✓ | ✓ | ✅ |

## 安全师工作流

```
日志收集 → /opf-audit ./src
    ↓
验证测试 → /opf-verify ./tests/suite.yaml
    ↓
数据统计 → /opf-scan (定期扫描)
    ↓
报告生成 → /opf-report monthly
    ↓
审计归档 → 合规存档
```

## 命令文件

- 主文件: `commands/opf-report.md`
- 实现脚本: `skills/privacy-filter/scripts/report.py`
- 报告模板: `skills/privacy-filter/templates/`
