---
license: UNKNOWN
triggers: ["n8n ai security scanner", "n8n-ai-security-scanner"]
---
# n8n-ai-security-scanner

## L0: 一句话描述 (≤15字)
AI-BOM安全扫描，n8n工作流漏洞检测

## L1: 使用场景 (50-100字)
当用户分享或导入n8n workflow JSON时，自动进行AI-BOM安全扫描，检测凭证明文、SSRF、命令注入、SQL注入、XSS、Prompt注入等15类安全风险，并在发现严重漏洞时阻止执行。

## L2: 详细文档

### 核心能力

`n8n-ai-security-scanner` 读取workflow JSON，对照 `detection_rules.json` 中的15条AI-BOM规则进行全量扫描，输出漏洞报告和修复建议。

### 目录结构

```
n8n-ai-security-scanner/
├── SKILL.md              # 本文件
├── detection_rules.json   # AI-BOM规则库（15条规则）
└── scripts/
    └── scanner.py       # Python扫描器
```

### AI-BOM规则总览

| 规则ID | 严重度 | 标题 | 检测类型 |
|--------|--------|------|---------|
| AI-BOM-001 | 🔴 critical | 凭证明文存储 | credentials |
| AI-BOM-002 | 🔴 critical | SSRF漏洞 | ssrf |
| AI-BOM-003 | 🟠 high | 命令注入风险 | injection |
| AI-BOM-004 | 🟠 high | 敏感数据泄露 | data_leak |
| AI-BOM-005 | 🟠 high | SQL注入风险 | injection |
| AI-BOM-006 | 🟡 medium | Webhook未授权访问 | auth |
| AI-BOM-007 | 🟡 medium | 错误信息泄露 | config |
| AI-BOM-008 | 🟡 medium | 无限循环/死循环 | performance |
| AI-BOM-009 | 🟡 medium | 文件操作安全 | path_traversal |
| AI-BOM-010 | 🟢 low | 日志记录过度 | verbose_log |
| AI-BOM-011 | 🔴 critical | AI Prompt注入 | injection |
| AI-BOM-012 | 🟠 high | OAuth/认证配置错误 | auth |
| AI-BOM-013 | 🟠 high | XSS风险 | injection |
| AI-BOM-014 | 🟡 medium | 依赖外部不可控服务 | dependency |
| AI-BOM-015 | 🟡 medium | 节点版本不兼容 | compatibility |

### CLI命令

```bash
# 扫描workflow文件
python scripts/scanner.py scan workflow.json

# 扫描并输出详细报告
python scripts/scanner.py scan workflow.json --verbose

# 仅检测critical漏洞
python scripts/scanner.py scan workflow.json --min-severity critical

# 扫描多个文件
python scripts/scanner.py batch workflows/*.json

# 从stdin扫描
cat workflow.json | python scripts/scanner.py scan --stdin
```

### scanner.py 实现参考

```python
#!/usr/bin/env python3
"""n8n AI-BOM 安全扫描器"""
import json
import sys
import re
from pathlib import Path

RULES_PATH = Path(__file__).parent.parent / "detection_rules.json"

def load_rules():
    with open(RULES_PATH, encoding="utf-8") as f:
        return json.load(f)["rules"]

def scan_workflow(workflow: dict, rules: list, min_severity: str = "low") -> list:
    """扫描workflow，返回漏洞列表"""
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    min_level = severity_order.get(min_severity, 3)

    findings = []
    for rule in rules:
        if severity_order.get(rule["severity"], 3) < min_level:
            continue
        for pattern in rule["patterns"]:
            if match_pattern(workflow, pattern):
                findings.append({
                    "rule_id": rule["id"],
                    "severity": rule["severity"],
                    "title": rule["title"],
                    "description": rule["description"],
                    "recommendation": rule["recommendation"],
                    "matched_pattern": pattern
                })
    return sorted(findings, key=lambda x: severity_order[x["severity"]])

def match_pattern(workflow: dict, pattern: dict) -> bool:
    """在workflow中匹配单个pattern"""
    field = pattern["field"]
    regex = pattern.get("regex", ".*")
    nested = pattern.get("nested")

    # 字段路径解析，如 nodes[].parameters.jsCode
    value = resolve_field(workflow, field)
    if value is None:
        return False

    if isinstance(value, str):
        return bool(re.search(regex, value, re.IGNORECASE))
    elif isinstance(value, list):
        return any(
            isinstance(v, str) and re.search(regex, v, re.IGNORECASE)
            for v in value
        )
    return False

def resolve_field(obj: dict, field: str):
    """解析字段路径，返回值"""
    parts = re.split(r'\.\.|\[.*?\]', field)
    current = obj
    for part in parts:
        part = part.strip('.')
        if not part:
            continue
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
        if current is None:
            return None
    return current
```

### 天龙适配

| 天龙岗位 | 适配方式 |
|---------|---------|
| **05安全师** | 直接调用扫描，发现critical立即阻断 |
| **04验证师** | CI/CD流水线集成，扫描不通过则阻止发布 |
| **01调研师** | 导入workflow前先扫描安全风险 |
| **19-01数据工程师** | 数据管道workflow安全审查 |

### 天龙集成示例

```yaml
# 在workflow天龙适配块中嵌入安全扫描
天龙适配:
  security_scan: true
  min_severity: high
  block_on_critical: true
  scanner: n8n-ai-security-scanner
  rules: AI-BOM-001,AI-BOM-002,AI-BOM-003,AI-BOM-005,AI-BOM-011
```

### 输出格式

```json
{
  "workflow_name": "CRM客户数据同步",
  "scan_time": "2026-05-05T12:00:00Z",
  "total_rules": 15,
  "rules_checked": 15,
  "findings": [
    {
      "rule_id": "AI-BOM-001",
      "severity": "critical",
      "title": "凭证明文存储",
      "node_id": "n2",
      "node_name": "查询CRM客户",
      "recommendation": "使用n8n凭据管理系统(Credentials Manager)替代硬编码凭证"
    }
  ],
  "summary": {
    "critical": 1,
    "high": 0,
    "medium": 2,
    "low": 1
  },
  "pass": false,
  "block_message": "发现1个critical漏洞，请修复后重试"
}
```

### 集成到天龙引擎

1. **05安全师工作流集成**：任何涉及n8n workflow的操作，自动触发AI-BOM扫描
2. **CI/CD流水线**：`n8n-scan --min-severity high` 扫描通过后才允许部署
3. **workflow导入拦截**：用户导入workflow时，critical漏洞直接阻止
4. **报告生成**：`n8n-scan --format markdown` 输出天龙报告格式

### 依赖

- Python 3.8+
- 标准库：`json`, `re`, `pathlib`（无外部依赖）
