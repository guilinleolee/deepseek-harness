---
name: opf-etl
description: OPF ETL Command - 数据工程专用
invokable: true
---
# OPF ETL Command - 数据工程专用

## 命令信息

**触发词**: `/opf-etl`, `ETL隐私`, `数据脱敏`

**权限**: 19数据工程师, 05安全师

**说明**: ETL流程中的隐私过滤节点，支持ODS/DWD/DWS/ADS四层架构

## 语法

```
/opf-etl <layer> [--config <config_file>] [--dry-run] [--report json|markdown]
/opf-etl <layer> --input <input> --output <output> [--mode typed|untyped|redacted]
```

## 参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `<layer>` | enum | ✓ | 数据层（ods/dwd/dws/ads） |
| `--config` | 路径 | ✗ | ETL配置文件 |
| `--dry-run` | flag | ✗ | 预览模式，不执行写入 |
| `--input` | 路径 | ✗ | 输入数据路径 |
| `--output` | 路径 | ✗ | 输出数据路径 |
| `--mode` | enum | ✗ | 脱敏模式 |

## 四层隐私架构

```
┌─────────────────────────────────────────────────────────────┐
│                   数据仓库隐私分层                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐ │
│   │   ODS   │ →  │   DWD   │ →  │   DWS   │ →  │   ADS   │ │
│   │ 原始层  │    │ 明细层  │    │ 汇总层  │    │ 应用层  │ │
│   └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘ │
│        │              │              │              │           │
│   ┌────▼────┐    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐ │
│   │ PII标注 │    │ PII脱敏 │    │ 聚合脱敏│    │ 业务脱敏│   │
│   │ 保留原始│    │ 敏感字段│    │ 统计级  │    │ 规则脱敏│   │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 各层策略

### ODS层 - 原始数据层
| 策略 | 描述 |
|------|------|
| PII标注 | 保留原始数据，仅标注PII位置 |
| 时间戳记录 | 记录数据进入ODS时间 |
| 血缘追踪 | 保持与上游数据血缘关系 |

### DWD层 - 明细宽表层
| 策略 | 描述 |
|------|------|
| PII脱敏 | 对敏感字段执行脱敏处理 |
| 字段加密 | 高敏感字段加密存储 |
| 访问控制 | 基于角色的字段级访问 |

### DWS层 - 汇总宽表层
| 策略 | 描述 |
|------|------|
| 聚合脱敏 | 统计时进行脱敏处理 |
| 差分隐私 | 添加噪声保护个体隐私 |
| K-匿名 | 确保每组至少K条记录 |

### ADS层 - 应用数据层
| 策略 | 描述 |
|------|------|
| 业务脱敏 | 按业务规则定制脱敏 |
| 动态脱敏 | 根据查询上下文动态脱敏 |
| 脱敏审计 | 记录所有敏感数据访问 |

## 使用示例

### ODS层预览
```
/opf-etl ods --config ./etl/privacy_config.yaml --dry-run
```

### DWD层执行
```
/opf-etl dwd --input ./data/raw/users.csv --output ./data/processed/users.csv --mode typed
```

### DWS层聚合脱敏
```
/opf-etl dws --input ./data/dwd/sales_summary.csv --output ./data/dws/sales_safe.csv
```

### ADS层业务规则
```
/opf-etl ads --input ./data/dws/ --output ./data/ads/ --config ./etl/ads_rules.yaml
```

## 配置文件格式

```yaml
# etl/privacy_config.yaml
etl:
  layer: dwd
  input:
    type: csv
    path: ./data/raw/users.csv
    encoding: utf-8

  output:
    type: csv
    path: ./data/processed/users_safe.csv
    mode: typed

  privacy_rules:
    private_email:
      action: redact
      mode: typed
    private_phone:
      action: redact
      mode: typed
    private_person:
      action: hash
      algorithm: sha256
    private_address:
      action: generalize
      level: district

  data_quality:
    check_duplicates: true
    check_nulls: true
    min_records: 100

  audit:
    enabled: true
    log_path: ./logs/etl_audit.log
```

## 输出格式

### JSON输出
```json
{
  "status": "etl_complete",
  "layer": "dwd",
  "input": "./data/raw/users.csv",
  "output": "./data/processed/users_safe.csv",
  "mode": "typed",
  "stats": {
    "total_records": 10000,
    "processed_records": 10000,
    "pii_detected": 3420,
    "pii_by_type": {
      "private_email": 890,
      "private_phone": 1230,
      "private_person": 456,
      "private_address": 844
    },
    "processing_time_ms": 2341
  },
  "quality_metrics": {
    "deduplication_rate": "0.2%",
    "null_check": "passed",
    "schema_validation": "passed"
  },
  "audit": {
    "job_id": "etl_20260101_143022",
    "user": "data_engineer",
    "timestamp": "2026-01-01T14:30:22Z"
  }
}
```

## 数据工程师工作流

```
数据采集 → /opf-etl ods (原始标注)
    ↓
数据清洗 → /opf-etl dwd (敏感脱敏)
    ↓
汇总统计 → /opf-etl dws (聚合保护)
    ↓
应用发布 → /opf-etl ads (业务规则)
    ↓
质量报告 → /opf-report monthly
```

## 质量保证

| 指标 | ODS | DWD | DWS | ADS |
|------|-----|-----|-----|-----|
| PII识别率 | >98% | >99% | >95% | >90% |
| 误报率 | <2% | <1% | <3% | <5% |
| 脱敏完整率 | N/A | >99% | >97% | >95% |
| 处理速度 | >1000/s | >500/s | >2000/s | >100/s |

## 命令文件

- 主文件: `commands/opf-etl.md`
- 实现脚本: `skills/privacy-filter/scripts/etl.py`
- 配置模板: `skills/privacy-filter/config/etl_template.yaml`
