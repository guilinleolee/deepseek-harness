---
name: opf-redact
description: OPF Redact Command - 隐私数据脱敏
invokable: true
---
# OPF Redact Command - 隐私数据脱敏

## 命令信息

**触发词**: `/opf-redact`, `脱敏`, `批量脱敏`

**权限**: 05安全师, 04验证师, 17数据分析师, 19数据工程师

## 语法

```
/opf-redact <input> [--output <output>] [--mode typed|untyped|redacted] [--format csv|json|log]
```

## 参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `<input>` | 文件/目录 | ✓ | 待脱敏文件或目录 |
| `--output` | 路径 | ✗ | 输出路径（默认覆盖原文件） |
| `--mode` | enum | ✗ | 输出模式（默认typed） |
| `--format` | enum | ✗ | 输出格式（默认继承输入格式） |

## 输出模式

| 模式 | 示例 | 用途 |
|------|------|------|
| `typed` | `<PRIVATE_EMAIL>` | 标准脱敏，保留类型标注 |
| `untyped` | `<PII>` | 简化脱敏，隐藏类型 |
| `redacted` | `***` | 完全遮盖，无标记 |

## 批量处理选项

| 选项 | 描述 |
|------|------|
| `--batch-size <n>` | 批量大小（默认100） |
| `--parallel <n>` | 并行数（默认4） |
| `--progress` | 显示进度条 |
| `--dry-run` | 预览模式，不写入 |

## 使用示例

### 单文件脱敏
```
/opf-redact ./data/user_records.csv --output ./data/sanitized_records.csv
```

### 目录批量脱敏
```
/opf-redact ./logs/ --mode redacted --progress
```

### 预览模式
```
/opf-redact ./data/customers.json --dry-run --verbose
```

## 输出格式

### JSON输出
```json
{
  "status": "success",
  "input": "./data/user_records.csv",
  "output": "./data/sanitized_records.csv",
  "mode": "typed",
  "stats": {
    "total_records": 1000,
    "redacted_records": 847,
    "pii_types": {
      "private_email": 234,
      "private_phone": 312,
      "private_address": 156,
      "private_date": 89,
      "account_number": 56
    },
    "processing_time_ms": 1234
  }
}
```

### CSV输出
```csv
id,name,email,phone,address,sanitized
1,张三,<PRIVATE_EMAIL>,<PRIVATE_PHONE>,<PRIVATE_ADDRESS>,false
2,李四,<PRIVATE_EMAIL>,<PRIVATE_PHONE>,<PRIVATE_ADDRESS>,false
```

## 与天龙九部协同

### 数据工程师工作流
```
/opf-etl ods --dry-run
    ↓
/opf-redact ./data/raw/*.csv --output ./data/sanitized/
    ↓
/opf-etl dwd --config ./etl/dwd_config.yaml
```

### 安全师批量处理
```
/opf-audit ./src --scope dir --severity high
    ↓ 发现问题
/opf-redact ./src/**/*.txt --mode redacted
```

### 数据分析师预处理
```
/opf-pre ./data/survey_responses.csv
    ↓ 分析就绪
/opf-redact ./data/clean_responses.csv
```

## 隐私质量保证

| 指标 | 目标 | 告警 |
|------|------|------|
| 脱敏完整率 | >99% | <97% |
| 误报率 | <2% | >5% |
| 处理速度 | >1000条/秒 | <500条/秒 |

## 错误处理

| 错误码 | 描述 | 处理建议 |
|--------|------|---------|
| E001 | 文件不存在 | 检查路径 |
| E002 | 格式不支持 | 转换格式后重试 |
| E003 | 权限不足 | 申请权限 |
| E004 | 模型加载失败 | 使用缓存或重试 |

## 命令文件

- 主文件: `commands/opf-redact.md`
- 实现脚本: `skills/privacy-filter/scripts/redact.py`
- 配置模板: `skills/privacy-filter/config/redact_template.yaml`