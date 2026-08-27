---
name: opf-pre
description: OPF Pre Command - 分析前预处理（分析师专用）
invokable: true
---
# OPF Pre Command - 分析前预处理（分析师专用）

## 命令信息

**触发词**: `/opf-pre`, `预处理`, `分析脱敏`

**权限**: 17数据分析师, 05安全师, 04验证师

**说明**: 数据分析前的隐私预处理，确保分析结果不含PII泄露风险

## 语法

```
/opf-pre <dataset> [--rules <rule_file>] [--output <output_dir>] [--report json|markdown]
/opf-pre <dataset> --quick [--preview]
```

## 参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `<dataset>` | 路径 | ✓ | 待处理数据集 |
| `--rules` | 路径 | ✗ | 自定义脱敏规则文件 |
| `--output` | 路径 | ✗ | 输出目录（默认覆盖原文件） |
| `--quick` | flag | ✗ | 快速模式（仅高风险） |
| `--preview` | flag | ✗ | 预览模式，显示但不写入 |

## 预处理流程

```
┌─────────────────────────────────────────────────────────────┐
│              OPF 分析前预处理工作流                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   数据加载 → OPF预扫描 → PII识别 → 自动脱敏 → 分析就绪      │
│       ↓           ↓           ↓           ↓          ↓       │
│   原始数据   发现PII    分类统计    脱敏处理    安全数据集  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 使用示例

### 快速预处理
```
/opf-pre ./data/survey_responses.csv --quick
```

### 自定义规则预处理
```
/opf-pre ./data/customer_data.csv --rules ./rules/analysis_privacy.yaml --output ./data/prepared/
```

### 预览模式
```
/opf-pre ./data/sales_data.csv --preview
```

### 批量预处理
```
/opf-pre ./data/analysis/*.csv --output ./data/safe/
```

## 预处理模式

| 模式 | 描述 | 适用场景 |
|------|------|---------|
| `standard` | 标准脱敏（默认） | 通用数据分析 |
| `strict` | 严格脱敏 | 合规要求高 |
| `quick` | 快速脱敏（仅高风险） | 大数据量预览 |
| `custom` | 自定义规则 | 特定业务需求 |

## 预处理报告

```json
{
  "status": "preprocess_complete",
  "dataset": "./data/survey_responses.csv",
  "mode": "standard",
  "pre_scan": {
    "total_records": 5000,
    "columns": 25,
    "total_cells": 125000,
    "pii_cells": 3420,
    "pii_rate": "2.7%",
    "pii_by_column": {
      "email": 1234,
      "phone": 890,
      "address": 456,
      "name": 840
    }
  },
  "sanitization": {
    "processed_records": 5000,
    "sanitized_cells": 3420,
    "mode_used": "typed",
    "replacements": {
      "<PRIVATE_EMAIL>": 1234,
      "<PRIVATE_PHONE>": 890,
      "<PRIVATE_ADDRESS>": 456,
      "<PRIVATE_PERSON>": 840
    }
  },
  "output": {
    "path": "./data/survey_responses_sanitized.csv",
    "format": "csv",
    "encoding": "utf-8"
  },
  "quality_check": {
    "no_data_loss": true,
    "pii_removed": true,
    "structure_preserved": true,
    "ready_for_analysis": true
  }
}
```

## 分析前检查清单

| 检查项 | 标准 | 状态 |
|--------|------|------|
| PII识别率 | >98% | ✓ |
| 误报率 | <2% | ✓ |
| 数据完整性 | 无丢失 | ✓ |
| 字段结构 | 保持不变 | ✓ |
| 编码格式 | UTF-8 | ✓ |

## 数据分析师工作流

```
数据加载 → /opf-pre ./data/raw.csv
    ↓
扫描报告 → 确认PII类型和数量
    ↓
脱敏处理 → 生成安全数据集
    ↓
分析执行 → 数据分析（无PII风险）
    ↓
报告生成 → 分析报告（不含敏感信息）
```

## 预处理规则配置

```yaml
# rules/analysis_privacy.yaml
preprocess:
  mode: standard
  rules:
    email:
      action: redact
      marker: "<PRIVATE_EMAIL>"
      preserve_format: false
    phone:
      action: redact
      marker: "<PRIVATE_PHONE>"
      preserve_format: true
    name:
      action: anonymize
      method: hash
    address:
      action: generalize
      level: city
    date:
      action: redact
      marker: "<PRIVATE_DATE>"

  quality:
    verify_completeness: true
    check_pii_residue: true
    preserve_analytics: true
```

## 与其他命令协同

| 流程 | 命令序列 |
|------|---------|
| 分析全流程 | /opf-pre → 分析 → /opf-scan |
| ETL集成 | /opf-etl ods → /opf-pre → /opf-etl dwd |
| 审计配合 | /opf-pre → /opf-audit |

## 命令文件

- 主文件: `commands/opf-pre.md`
- 实现脚本: `skills/privacy-filter/scripts/preprocess.py`
- 规则模板: `skills/privacy-filter/config/preprocess_rules.yaml`
