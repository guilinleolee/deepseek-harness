---
name: opf-patterns
description: OPF Custom Patterns - 自定义PII模式数据库
invokable: true
---
# OPF Custom Patterns - 自定义PII模式数据库

## 概念定义

OPF 内置8种标准PII类型（private_person/date/email/phone/address/account_number/private_url/secret）。
Custom Patterns 允许用户通过正则、字典、规则链扩展识别能力，支持企业级私有PII和领域特定敏感信息。

## 模式文件格式

### JSON格式（推荐）

```json
{
  "version": "1.0",
  "name": "custom-banking-pii",
  "description": "金融行业PII扩展",
  "author": "security-team",
  "created": "2026-01-01",
  "patterns": [
    {
      "id": "bank_card",
      "type": "private_financial",
      "priority": "high",
      "match": {
        "regex": "\\b\\d{16}(?:\\d{2,4})?\\b",
        "context_keywords": ["卡号", "银行卡", "信用卡", "card", "credit"],
        "validator": "luhn"
      },
      "sanitize": {
        "typed": "<PRIVATE_BANK_CARD>",
        "untyped": "<PII>",
        "redacted": "****-****-****-****"
      },
      "test_cases": [
        { "input": "我的卡号是6222021234567890", "should_match": true },
        { "input": "共1234567890123456个用户", "should_match": false }
      ],
      "false_positive_guard": {
        "excludes": ["\\d{16}号段", "学号", "订单号"]
      }
    },
    {
      "id": "id_card_cn",
      "type": "private_identity",
      "priority": "critical",
      "match": {
        "regex": "\\b[1-9]\\d{5}(?:19|20)\\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\\d|3[01])\\d{3}[\\dXx]\\b",
        "context_keywords": ["身份证", "证件号", "ID号"]
      },
      "sanitize": {
        "typed": "<PRIVATE_ID_CARD>",
        "untyped": "<PII>",
        "redacted": "******************"
      }
    },
    {
      "id": "passport_cn",
      "type": "private_identity",
      "priority": "high",
      "match": {
        "regex": "\\b[EGFG]\\d{8,9}\\b",
        "context_keywords": ["护照", "passport"]
      },
      "sanitize": {
        "typed": "<PRIVATE_PASSPORT>",
        "untyped": "<PII>",
        "redacted": "G*********"
      }
    },
    {
      "id": "ip_address",
      "type": "private_infrastructure",
      "priority": "medium",
      "match": {
        "regex": "\\b(?:(?:25[0-5]|2[0-4]\\d|[01]?\\d\\d?)\\.){3}(?:25[0-5]|2[0-4]\\d|[01]?\\d\\d?)\\b",
        "context_keywords": ["IP", "地址", "ip_address"]
      },
      "sanitize": {
        "typed": "<PRIVATE_IP>",
        "untyped": "<PII>",
        "redacted": "xxx.xxx.xxx.xxx"
      }
    },
    {
      "id": "mac_address",
      "type": "private_infrastructure",
      "priority": "low",
      "match": {
        "regex": "\\b[0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5}\\b",
        "context_keywords": ["MAC", "mac_address"]
      },
      "sanitize": {
        "typed": "<PRIVATE_MAC>",
        "untyped": "<PII>",
        "redacted": "XX:XX:XX:XX:XX:XX"
      }
    },
    {
      "id": " iban",
      "type": "private_financial",
      "priority": "high",
      "match": {
        "regex": "\\b[A-Z]{2}\\d{2}[A-Z0-9]{11,30}\\b",
        "context_keywords": ["IBAN", "银行账户", "iban"]
      },
      "sanitize": {
        "typed": "<PRIVATE_IBAN>",
        "untyped": "<PII>",
        "redacted": "XX**XX******"
      }
    },
    {
      "id": "swift_code",
      "type": "private_financial",
      "priority": "medium",
      "match": {
        "regex": "\\b[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\\b",
        "context_keywords": ["SWIFT", "BIC", "银行代码"]
      },
      "sanitize": {
        "typed": "<PRIVATE_SWIFT>",
        "untyped": "<PII>",
        "redacted": "XXXXXX**"
      }
    },
    {
      "id": "tax_id_cn",
      "type": "private_identity",
      "priority": "high",
      "match": {
        "regex": "\\b\\d{15}|\\d{18}|\\d{20}\\b",
        "context_keywords": ["税务登记号", "税号", "纳税人识别号"]
      },
      "sanitize": {
        "typed": "<PRIVATE_TAX_ID>",
        "untyped": "<PII>",
        "redacted": "*************"
      }
    },
    {
      "id": "driver_license_cn",
      "type": "private_identity",
      "priority": "high",
      "match": {
        "regex": "\\b[1-9]\\d{5}\\d{10,12}[A-Z0-9]\\b",
        "context_keywords": ["驾驶证", "驾照号", "行驶证"]
      },
      "sanitize": {
        "typed": "<PRIVATE_DRIVER_LICENSE>",
        "untyped": "<PII>",
        "redacted": "******************"
      }
    },
    {
      "id": "latitude_longitude",
      "type": "private_location",
      "priority": "medium",
      "match": {
        "regex": "\\-?\\d{1,3}\\.\\d{4,10}",
        "context_keywords": ["坐标", "GPS", "经纬度", "latitude", "longitude", "lat", "lng"]
      },
      "sanitize": {
        "typed": "<PRIVATE_LOCATION>",
        "untyped": "<PII>",
        "redacted": "XX.XXXX, XX.XXXX"
      }
    },
    {
      "id": "medical_record_id",
      "type": "private_medical",
      "priority": "critical",
      "match": {
        "regex": "\\b(MR|mr|HIS|his|病历)[\\-_]?\\d{6,12}\\b",
        "context_keywords": ["病历号", "就诊号", "住院号", "门诊号"]
      },
      "sanitize": {
        "typed": "<PRIVATE_MEDICAL_ID>",
        "untyped": "<PII>",
        "redacted": "MR**********"
      }
    },
    {
      "id": "social_security_us",
      "type": "private_identity",
      "priority": "critical",
      "match": {
        "regex": "\\b\\d{3}-\\d{2}-\\d{4}\\b",
        "context_keywords": ["SSN", "social security", "社保号"]
      },
      "sanitize": {
        "typed": "<PRIVATE_SSN>",
        "untyped": "<PII>",
        "redacted": "***-**-****"
      }
    },
    {
      "id": "api_key_generic",
      "type": "secret",
      "priority": "critical",
      "match": {
        "regex": "(?i)(?:api[_-]?key|apikey|api[_-]?secret|api[_-]?token|secret[_-]?key|access[_-]?token)\\s*[:=]\\s*['\"]?([a-zA-Z0-9_\\-]{20,64})['\"]?",
        "context_keywords": [],
        "group": 1
      },
      "sanitize": {
        "typed": "<PRIVATE_API_KEY>",
        "untyped": "<SECRET>",
        "redacted": "sk-*******"
      }
    },
    {
      "id": "jwt_token",
      "type": "secret",
      "priority": "critical",
      "match": {
        "regex": "eyJ[a-zA-Z0-9_\\-]+\\.[a-zA-Z0-9_\\-]+\\.[a-zA-Z0-9_\\-]+",
        "context_keywords": ["jwt", "bearer", "token"]
      },
      "sanitize": {
        "typed": "<PRIVATE_JWT>",
        "untyped": "<SECRET>",
        "redacted": "eyJ*****.*****.*****"
      }
    }
  ]
}
```

### YAML格式（可读性更好）

```yaml
# custom-patterns-finance.yaml
version: "1.0"
name: "finance-pii"
description: "金融行业PII扩展模式库"

patterns:
  - id: bank_card
    type: private_financial
    priority: high
    match:
      regex: "\\b\\d{16}(?:\\d{2,4})?\\b"
      context_keywords: ["卡号", "银行卡", "信用卡"]
      validator: luhn
    sanitize:
      typed: "<PRIVATE_BANK_CARD>"
      untyped: "<PII>"
      redacted: "****-****-****-****"
    test_cases:
      - input: "我的卡号是6222021234567890"
        should_match: true
      - input: "共1234567890123456个用户"
        should_match: false

  - id: id_card_cn
    type: private_identity
    priority: critical
    match:
      regex: "\\b[1-9]\\d{5}(?:19|20)\\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\\d|3[01])\\d{3}[\\dXx]\\b"
      context_keywords: ["身份证", "证件号"]
    sanitize:
      typed: "<PRIVATE_ID_CARD>"
      untyped: "<PII>"
      redacted: "******************"

  - id: medical_record_id
    type: private_medical
    priority: critical
    match:
      regex: "\\b(MR|病历)[\\-_]?\\d{6,12}\\b"
      context_keywords: ["病历号", "就诊号", "住院号"]
    sanitize:
      typed: "<PRIVATE_MEDICAL_ID>"
      untyped: "<PII>"
      redacted: "MR**********"
```

### 字典格式（高精度场景）

```json
{
  "name": "company-confidential",
  "type": "dictionary",
  "entries": [
    { "value": "季度净利润", "category": "financial", "sensitivity": "high" },
    { "value": "核心算法", "category": "technical", "sensitivity": "critical" },
    { "value": "高管通讯录", "category": "personnel", "sensitivity": "critical" },
    { "value": "竞品分析报告", "category": "strategy", "sensitivity": "high" },
    { "value": "用户画像数据库", "category": "data", "sensitivity": "high" }
  ]
}
```

## 规则链（Rule Chain）

复杂场景支持多规则组合：

```json
{
  "id": "composite-insurance-policy",
  "type": "composite",
  "rules": [
    { "field": "document_type", "operator": "equals", "value": "保险单" },
    { "field": "content", "operator": "contains_any", "patterns": ["险种", "保额", "受益人"] },
    { "field": "amount", "operator": "matches", "regex": "\\d{5,}" }
  ],
  "action": "mark_section",
  "sanitize": {
    "typed": "<PRIVATE_INSURANCE_SECTION>",
    "untyped": "<SENSITIVE>"
  }
}
```

## 优先级与性能

| Priority | 处理方式 | 适用场景 |
|----------|---------|---------|
| critical | 先验匹配 + 立即脱敏 | SSN/身份证/医疗ID |
| high | 并行检测 + 上下文辅助 | 银行卡/护照/驾照 |
| medium | 后验匹配 + 阈值控制 | IP地址/MAC/坐标 |
| low | 按需检测 + 手动触发 | 内部代码/非敏感ID |

## False Positive Guard

减少误报的关键机制：

```json
{
  "id": "bank_card",
  "false_positive_guard": {
    "exclude_patterns": ["\\d{16}号段", "学号\\d{10}", "订单号"],
    "context_required": ["卡号", "银行卡", "信用卡", "card", "credit", "账户"],
    "min_confidence": 0.7,
    "exclude_file_types": ["代码文件", "配置文件"]
  }
}
```

## 验证器（Validator）

内置验证器列表：

| 验证器 | 适用类型 | 算法 |
|--------|---------|------|
| luhn | 银行卡号 | Luhn算法 |
| mod97 | IBAN | ISO 7064 Mod 97-10 |
| checksum | 身份证 | 出生日期+校验位 |
| format | 手机号 | 国家格式正则 |

自定义验证器：

```javascript
// custom-validators.js
module.exports = {
  // 快递单号验证（顺丰/中通/圆通）
  express_number: (text) => {
    const patterns = [
      /SF\d{12}/,  // 顺丰
      /\d{12,15}/,  // 中通/圆通
    ];
    return patterns.some(p => p.test(text));
  },

  // 内部工号验证
  employee_id: (text, context) => {
    return /^EMP\d{6,8}$/.test(text) && context.includes('工号');
  }
};
```

## 内置 + 自定义模式优先级

```
检测顺序（按优先级）:
  1. 内置 critical (email/phone/idcard/ssn)
  2. 自定义 critical
  3. 内置 high (person/address)
  4. 自定义 high
  5. 内置 medium (url/date)
  6. 自定义 medium
  7. 内置 low (account)
  8. 自定义 low
  9. 内置 secret (api_key/jwt)
  10. 自定义 secret
```

## 模式管理命令

```bash
# 加载自定义模式库
python scripts/opf_pattern_manager.py load --file ./patterns/finance-pii.json

# 验证模式语法
python scripts/opf_pattern_manager.py validate --file ./patterns/custom.yaml

# 列出已加载模式
python scripts/opf_pattern_manager.py list

# 测试单条规则
python scripts/opf_pattern_manager.py test --id bank_card --input "卡号6222021234567890"

# 导入行业预设包
python scripts/opf_pattern_manager.py import --package finance      # 金融行业
python scripts/opf_pattern_manager.py import --package healthcare  # 医疗行业
python scripts/opf_pattern_manager.py import --package government  # 政府机构

# 导出当前配置
python scripts/opf_pattern_manager.py export --output ./my-patterns.json
```

## 行业预设包

### 金融行业 (finance)

- 银行卡号 (Luhn校验)
- 信用卡号
- IBAN
- SWIFT/BIC代码
- 税务登记号
- 保险单号
- 证券账户号

### 医疗行业 (healthcare)

- 病历号
- 就诊卡号
- 住院号
- 医保卡号
- 处方编号
- 检测报告编号

### 政府机构 (government)

- 身份证号
- 护照号
- 驾驶证号
- 社保号
- 税务登记号
- 警官证/军官证号

### 电商行业 (ecommerce)

- 订单号 (特定格式)
- 快递单号
- 会员ID (手机/邮箱)
- 收货地址
- 支付账号

### 社交媒体 (social)

- 用户ID
- 私信内容标记
- 分享位置
- 设备ID (IMEI/IMSI)

## 性能优化

| 优化策略 | 效果 |
|---------|------|
| 预编译正则 (re2/go) | 匹配速度 +200% |
| 模式懒加载 | 启动时间 -60% |
| 并行检测 (critical组) | 检测延迟 -40% |
| 缓存上下文 (滑动窗口) | 重复检测开销 -80% |
| 模式分组 + Early Exit | 无匹配时提前退出 |

## 与OPF内置类型的映射

| 自定义类型 | 映射到内置类型 |
|-----------|--------------|
| private_identity | private_person (扩展) |
| private_financial | account_number (扩展) |
| private_medical | private_person (扩展) |
| private_location | private_address (扩展) |
| private_infrastructure | private_url (扩展) |
| secret | secret (直接扩展) |

## 文件路径

- 主文件: `commands/opf-patterns.md`
- 实现脚本: `skills/privacy-filter/scripts/pattern_manager.py`
- 内置预设: `skills/privacy-filter/config/industry-presets/`
- 自定义模式库: `skills/privacy-filter/config/custom-patterns/`

## 示例命令

```bash
# 加载金融行业PII模式
/opf-pattern load --package finance

# 测试自定义模式
/opf-pattern test --id bank_card --text "我的招行卡号是6222021234567890"

// 导出自定义模式
/opf-pattern export --output ./my-pii-patterns.json

// 验证模式文件
/opf-pattern validate ./patterns/medical.yaml
```