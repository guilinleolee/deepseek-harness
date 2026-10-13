---
name: opf-scan
description: OPF Privacy Filter Commands - 天龙九部统一命令
invokable: true
---
# OPF Privacy Filter Commands - 天龙九部统一命令

## 概述

OPF（OpenAI Privacy Filter）天龙九部统一命令封装，提供标准化隐私过滤操作接口。

## 命令列表

### `/opf-scan` - 隐私数据扫描

**用途**: 扫描文本中的PII数据

**语法**:
```
/opf-scan <text> [--mode typed|untyped|redacted] [--types <types>]
```

**示例**:
```
/opf-scan "请联系 john@example.com 或 13812345678"
/opf-scan "用户地址：北京市朝阳区" --mode redacted
/opf-scan "订单号 ABC123 客户邮箱 test@test.com" --types private_email,account_number
```

**输出格式**:
```json
{
  "status": "success",
  "pii_count": 2,
  "detections": [
    {"type": "private_email", "value": "john@example.com", "start": 7, "end": 21},
    {"type": "private_phone", "value": "13812345678", "start": 27, "end": 37}
  ],
  "sanitized": "请联系 <PRIVATE_EMAIL> 或 <PRIVATE_PHONE>"
}
```

---

### `/opf-redact` - 隐私数据脱敏

**用途**: 批量脱敏文本中的PII

**语法**:
```
/opf-redact <file> [--output <output_file>] [--mode typed|untyped|redacted]
```

**示例**:
```
/opf-redact ./data/user_data.csv --output ./data/sanitized.csv
/opf-redact ./logs/access.log --mode redacted
```

**输出格式**:
```json
{
  "status": "success",
  "total_records": 100,
  "redacted_count": 85,
  "output_file": "./data/sanitized.csv"
}
```

---

### `/opf-verify` - 隐私验证（验证师专用）

**用途**: 四态验证测试 - Loading/Error/Empty/Success + PII检测

**语法**:
```
/opf-verify <test_suite> [--report json|markdown] [--output <file>]
```

**示例**:
```
/opf-verify ./tests/privacy_suite.yaml --report markdown --output ./reports/privacy_test.md
/opf-verify quick --report json
```

**四态测试矩阵**:
| 状态 | 描述 | 预期结果 |
|------|------|---------|
| Loading | 模型加载中 | 显示加载进度 |
| Error | 模型加载失败 | 优雅降级 + 错误提示 |
| Empty | 空输入检测 | 返回空结果（不报错） |
| Success | 正常检测 | 返回检测结果 |
| PII_Detected | 发现PII | 标注位置和类型 |
| PII_Clean | 无PII | 返回clean标记 |

---

### `/opf-audit` - 安全审计（安全师专用）

**用途**: 系统级PII数据安全扫描

**语法**:
```
/opf-audit <target> [--scope file|dir|database] [--severity high|medium|low]
```

**示例**:
```
/opf-audit ./src --scope dir --severity high
/opf-audit ./config/secrets.yaml --scope file
```

**输出格式**:
```json
{
  "status": "audit_complete",
  "total_files": 156,
  "pii_findings": [
    {"file": "config.yaml", "line": 23, "type": "private_email", "severity": "high"}
  ],
  "risk_score": 75,
  "recommendations": ["脱敏配置中的邮箱字段", "移除硬编码凭证"]
}
```

---

### `/opf-etl` - 数据工程专用

**用途**: ETL流程中的隐私过滤节点

**语法**:
```
/opf-etl <layer> [--config <config_file>] [--dry-run]
```

**示例**:
```
/opf-etl ods --config ./etl/privacy_config.yaml --dry-run
/opf-etl dwd --dry-run
```

**四层隐私节点**:
| 层级 | 描述 | 过滤策略 |
|------|------|---------|
| ODS | 原始数据层 | 全量保留原始，标注PII位置 |
| DWD | 明细宽表层 | 脱敏敏感字段 |
| DWS | 汇总层 | 聚合时脱敏 |
| ADS | 应用层 | 业务脱敏规则 |

---

### `/opf-pre` - 分析前预处理（分析师专用）

**用途**: 数据分析前的隐私预处理

**语法**:
```
/opf-pre <dataset> [--rules <rule_file>] [--output <output_dir>]
```

**示例**:
```
/opf-pre ./data/sales.csv --rules ./rules/analysis_privacy.yaml
/opf-pre ./data/customer_feedback.csv
```

**隐私工作流**:
```
数据加载 → OPF预扫描 → PII识别 → 自动脱敏 → 分析就绪
```

---

### `/opf-report` - 合规报告生成

**用途**: 生成隐私合规报告（GDPR/CCPA）

**语法**:
```
/opf-report <period> [--format pdf|html|markdown] [--output <file>]
```

**示例**:
```
/opf-report monthly --format pdf --output ./reports/privacy_monthly.pdf
/opf-report quarterly --format markdown
```

**报告内容**:
- PII检测统计
- 脱敏覆盖率
- 违规风险评估
- 合规建议

---

## 全局选项

| 选项 | 描述 | 默认值 |
|------|------|-------|
| `--mode` | 输出模式 | typed |
| `--verbose` | 详细输出 | false |
| `--dry-run` | 模拟运行 | false |
| `--format` | 输出格式 | json |

---

## 隐私质量指标

| 指标 | 目标值 | 告警阈值 |
|------|-------|---------|
| PII识别率 | >98% | <95% |
| 误报率 | <2% | >5% |
| 漏报率 | <0.5% | >1% |
| 脱敏完整率 | >99% | <97% |

---

## 权限矩阵

| 命令 | 05安全师 | 04验证师 | 17分析师 | 19工程师 | 其他岗位 |
|------|---------|---------|---------|---------|---------|
| `/opf-scan` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/opf-redact` | ✓ | ✓ | ✓ | ✓ | ✗ |
| `/opf-verify` | ✓ | ✓ | ✗ | ✗ | ✗ |
| `/opf-audit` | ✓ | ✗ | ✗ | ✓ | ✗ |
| `/opf-etl` | ✓ | ✗ | ✗ | ✓ | ✗ |
| `/opf-pre` | ✓ | ✓ | ✓ | ✓ | ✗ |
| `/opf-report` | ✓ | ✓ | ✗ | ✗ | ✗ |

---

## 示例工作流

### 数据工程师ETL工作流
```bash
1. /opf-etl ods --dry-run  # 预览ODS层脱敏
2. /opf-etl ods             # 执行ODS脱敏
3. /opf-etl dwd             # 执行DWD脱敏
4. /opf-report monthly     # 生成合规报告
```

### 安全师审计工作流
```bash
1. /opf-audit ./src --scope dir --severity high
2. /opf-verify ./tests/privacy_suite.yaml --report markdown
3. /opf-report quarterly --format pdf
```

### 数据分析师工作流
```bash
1. /opf-pre ./data/customer_data.csv
2. /opf-scan "分析结果摘要" --mode redacted
3. 生成分析报告（无PII泄露）
```

---

## 文件位置

- 命令定义: `.claude/commands/opf-*.md`
- 配置模板: `skills/privacy-filter/config/`
- 测试套件: `skills/privacy-filter/tests/`
- 合规报告: `reports/privacy/`