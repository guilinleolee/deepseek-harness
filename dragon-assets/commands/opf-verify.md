---
name: opf-verify
description: OPF Verify Command - 隐私验证（验证师专用）
invokable: true
---
# OPF Verify Command - 隐私验证（验证师专用）

## 命令信息

**触发词**: `/opf-verify`, `隐私验证`, `四态测试`

**权限**: 05安全师, 04验证师

**说明**: 执行四态验证测试 - Loading/Error/Empty/Success + PII检测

## 语法

```
/opf-verify <test_suite> [--report json|markdown] [--output <file>]
/opf-verify quick [--report json|markdown]
/opf-verify <test_file> [--verbose] [--output <file>]
```

## 参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `<test_suite>` | 路径/名称 | ✓ | 测试套件文件或名称 |
| `--report` | enum | ✗ | 输出格式（默认json） |
| `--output` | 路径 | ✗ | 输出文件路径 |
| `--verbose` | flag | ✗ | 详细输出 |

## 四态测试矩阵

| 状态 | 描述 | 预期结果 |
|------|------|---------|
| Loading | 模型加载中 | 显示加载进度 |
| Error | 模型加载失败 | 优雅降级 + 错误提示 |
| Empty | 空输入检测 | 返回空结果（不报错） |
| Success | 正常检测 | 返回检测结果 |
| PII_Detected | 发现PII | 标注位置和类型 |
| PII_Clean | 无PII | 返回clean标记 |

## 测试套件格式

```yaml
# privacy_suite.yaml
test_cases:
  - name: "加载测试"
    input: ""
    expected_state: "Loading"

  - name: "空输入测试"
    input: ""
    expected_state: "Empty"

  - name: "邮箱检测"
    input: "联系 john@example.com"
    expected_state: "Success"
    expected_pii_types: ["private_email"]

  - name: "手机号检测"
    input: "拨打 13812345678"
    expected_state: "Success"
    expected_pii_types: ["private_phone"]

  - name: "混合PII"
    input: "张三 13812345678 联系 test@test.com"
    expected_state: "Success"
    expected_pii_types: ["private_person", "private_phone", "private_email"]

  - name: "无PII文本"
    input: "今天天气很好"
    expected_state: "PII_Clean"
```

## 使用示例

### 快速测试
```
/opf-verify quick --report markdown
```

### 指定测试套件
```
/opf-verify ./tests/privacy_suite.yaml --report markdown --output ./reports/privacy_test.md
/opf-verify integration --report json
```

### 详细输出
```
/opf-verify ./tests/full_suite.yaml --verbose --output ./reports/test_result.json
```

## 输出格式

### JSON输出
```json
{
  "status": "test_complete",
  "suite": "./tests/privacy_suite.yaml",
  "total_tests": 6,
  "passed": 5,
  "failed": 1,
  "duration_ms": 1234,
  "results": [
    {
      "name": "邮箱检测",
      "state": "Success",
      "passed": true,
      "detected_types": ["private_email"],
      "expected_types": ["private_email"],
      "match": true
    },
    {
      "name": "混合PII",
      "state": "PII_Detected",
      "passed": false,
      "detected_types": ["private_email"],
      "expected_types": ["private_person", "private_phone", "private_email"],
      "match": false
    }
  ],
  "summary": {
    "detection_rate": "83.3%",
    "false_positive_rate": "0%",
    "recommendation": "修复private_person和private_phone检测"
  }
}
```

### Markdown报告
```markdown
# OPF 四态测试报告

## 测试摘要
| 指标 | 值 |
|------|-----|
| 总测试数 | 6 |
| 通过 | 5 |
| 失败 | 1 |
| 通过率 | 83.3% |

## 四态测试结果

### ✓ Success 状态
- 邮箱检测: PASSED
- 手机号检测: PASSED
- 无PII文本: PASSED

### ✗ Failed 状态
- 混合PII: FAILED
  - 预期检测: private_person, private_phone, private_email
  - 实际检测: private_email
  - **漏报**: private_person, private_phone

## 建议
修复person和phone的NER标签识别
```

## 与天龙九部协同

### 验证师工作流
```
/opf-verify quick --report markdown
    ↓
发现问题 → 调整模型/规则
    ↓
/opf-verify full --report markdown --output report.md
    ↓
/opf-report monthly --format markdown
```

### 安全师工作流
```
/opf-audit ./src --scope dir --severity high
    ↓
/opf-verify security_suite.yaml --verbose
    ↓
生成安全报告 → /opf-report quarterly
```

## 命令文件

- 主文件: `commands/opf-verify.md`
- 测试套件: `skills/privacy-filter/tests/`
- 实现脚本: `skills/privacy-filter/scripts/verify.py`