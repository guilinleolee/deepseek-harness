---
name: opf-audit
description: OPF Audit Command - 安全审计（安全师专用）
invokable: true
---
# OPF Audit Command - 安全审计（安全师专用）

## 命令信息

**触发词**: `/opf-audit`, `隐私审计`, `安全扫描`

**权限**: 05安全师, 19数据工程师

**说明**: 系统级PII数据安全扫描，发现敏感数据泄露风险

## 语法

```
/opf-audit <target> [--scope file|dir|database] [--severity high|medium|low] [--report json|markdown] [--output <file>]
```

## 参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `<target>` | 路径/URL | ✓ | 审计目标（文件/目录/数据库） |
| `--scope` | enum | ✗ | 审计范围（默认dir） |
| `--severity` | enum | ✗ | 严重级别过滤（默认high） |
| `--report` | enum | ✗ | 输出格式（默认json） |
| `--output` | 路径 | ✗ | 输出文件路径 |

## 审计范围

| 范围 | 描述 | 适用场景 |
|------|------|---------|
| `file` | 单文件深度审计 | 配置文件、日志文件 |
| `dir` | 目录递归扫描 | 代码库、文档目录 |
| `database` | 数据库连接审计 | 数据库表、字段扫描 |

## 严重级别

| 级别 | 描述 | 阈值 |
|------|------|------|
| `high` | 高风险PII泄露 | 邮箱、手机、身份证等 |
| `medium` | 中风险信息泄露 | 地址、日期、账号 |
| `low` | 低风险信息 | 一般文本匹配 |

## 使用示例

### 目录扫描
```
/opf-audit ./src --scope dir --severity high --report markdown
```

### 数据库审计
```
/opf-audit mysql://localhost:3306/users --scope database --severity high
```

### 单文件审计
```
/opf-audit ./config/secrets.yaml --scope file --report json --output ./reports/security_audit.json
```

## 输出格式

### JSON输出
```json
{
  "status": "audit_complete",
  "target": "./src",
  "scope": "dir",
  "duration_ms": 1234,
  "total_files": 156,
  "scanned_files": 156,
  "total_findings": 23,
  "by_severity": {
    "high": 8,
    "medium": 12,
    "low": 3
  },
  "findings": [
    {
      "file": "src/config.yaml",
      "line": 23,
      "type": "private_email",
      "severity": "high",
      "context": "admin_email: john@example.com",
      "risk_score": 85,
      "recommendation": "使用环境变量替代硬编码邮箱"
    }
  ],
  "risk_summary": {
    "overall_risk": 72,
    "critical_areas": ["config files", "test data"],
    "top_types": ["private_email", "private_phone"]
  },
  "recommendations": [
    "将配置文件的敏感信息迁移到环境变量",
    "测试数据使用脱敏数据",
    "启用Git hooks防止敏感信息提交"
  ]
}
```

### Markdown报告
```markdown
# OPF 安全审计报告

## 审计摘要
| 指标 | 值 |
|------|-----|
| 审计目标 | ./src |
| 扫描文件数 | 156 |
| 发现问题 | 23 |
| 高风险 | 8 |
| 中风险 | 12 |
| 低风险 | 3 |

## 高风险发现

### 🔴 private_email (5处)
| 文件 | 行号 | 上下文 |
|------|------|--------|
| config.yaml | 23 | admin_email: john@example.com |
| settings.py | 45 | contact = "test@test.com" |

### 🔴 private_phone (3处)
| 文件 | 行号 | 上下文 |
|------|------|--------|
| users.csv | 12 | phone: 13812345678 |

## 风险分布
- 配置文件: 15处 (65%)
- 测试数据: 5处 (22%)
- 文档: 3处 (13%)

## 修复建议
1. 将config.yaml中的硬编码邮箱迁移到环境变量
2. 使用脱敏测试数据替代真实手机号
3. 添加.pre-commit-config.yaml防止敏感信息提交
```

## 审计覆盖类型

| PII类型 | 风险分数 | 检测规则 |
|---------|---------|---------|
| private_email | 85 | 正则匹配+上下文分析 |
| private_phone | 80 | 国内手机号正则 |
| private_person | 90 | NER命名实体识别 |
| private_address | 70 | 地址模式+POI数据库 |
| account_number | 95 | 银行账号/信用卡格式 |
| private_url | 60 | URL正则+IP暴露检测 |
| private_date | 40 | 日期格式识别 |
| secret | 100 | API Key/Secret/Token |

## 安全师工作流

```
/opf-audit ./src --scope dir --severity high
    ↓
发现高风险泄露 → 立即脱敏处理
    ↓
生成审计报告 → /opf-report quarterly
    ↓
制定修复计划 → 更新安全策略
```

## 与其他命令协同

| 流程 | 命令序列 |
|------|---------|
| 发现→脱敏 | /opf-audit → /opf-redact → /opf-verify |
| 审计→报告 | /opf-audit → /opf-report |
| 扫描→验证 | /opf-scan → /opf-audit → /opf-verify |

## 命令文件

- 主文件: `commands/opf-audit.md`
- 实现脚本: `skills/privacy-filter/scripts/audit.py`
- 规则配置: `skills/privacy-filter/config/audit_rules.yaml`
