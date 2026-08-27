---
license: UNKNOWN
triggers: ["privacy filter", "Privacy Filter Skill — OPF集成封装"]
---
# Privacy Filter Skill — OPF集成封装

## L0: 一句话描述
OpenAI Privacy Filter PII检测与脱敏能力封装，支持8类隐私信息检测、文本重编辑、批量处理与微调。

## L1: 使用场景

### 核心场景

| 场景 | 命令示例 | 触发条件 |
|------|---------|----------|
| **即时PII扫描** | `opf "文本"` | 快速检测文本中的隐私信息 |
| **日志脱敏** | `cat logs/app.log \| opf > clean.log` | 生产日志隐私处理 |
| **批量文档脱敏** | `opf -f ./docs/*.txt` | 文档库批量处理 |
| **合规评估** | `opf eval dataset.jsonl` | 隐私合规审计 |
| **模型微调** | `opf train data.jsonl --output-dir ./finetuned` | 自定义PII识别 |

### 天龙引擎岗位协同

| 天龙岗位 | 使用方式 | 协同效果 |
|---------|---------|---------|
| **05安全师** | `[@安全师] 扫描这段文本中的PII` | 隐私合规审计 |
| **19数据工程师** | ETL管道节点 | 数据脱敏管道 |
| **04验证师** | 测试数据脱敏 | 隐私保护验证 |
| **17数据分析师** | 分析前脱敏 | 报告隐私过滤 |

## L2: 详细文档

### 1. OPF安装

```bash
# 推荐：pip安装
pip install privacy-filter  # 等待官方发布

# 当前：源码安装
cd ~/.claude/skills/privacy-filter
pip install -e .
```

### 2. 核心命令

```bash
# === 即时检测 ===
opf "张三的邮箱是 zhangsan@example.com，电话 13812345678"

# === 文件批量处理 ===
opf -f ./input.txt                           # 单文件
opf -f ./input1.txt -f ./input2.txt         # 多文件
opf -f ./docs/*.txt                          # 通配符

# === 管道输入 ===
cat logs/app.log | opf > clean.log
grep "ERROR" logs/app.log | opf

# === 评估模式 ===
opf eval ./dataset.jsonl --eval-mode typed

# === 训练微调 ===
opf train ./train.jsonl --validation-dataset ./dev.jsonl --output-dir ./finetuned

# === 高级选项 ===
opf --device cpu "text"                      # CPU模式
opf --output-mode redacted "text"            # 统一标签模式
opf --checkpoint /path/to/model "text"       # 指定模型
```

### 3. Python API封装

```python
from opf_core.opf_wrapper import OPFWrappedModel

# 初始化
opf = OPFWrappedModel()

# 即时脱敏
result = opf.redact("张三邮箱 zhangsan@example.com")
print(result["redacted_text"])  # 张三邮箱 <PRIVATE_EMAIL>
print(result["summary"])       # {"span_count": 1, "by_label": {"private_email": 1}}

# 批量处理
results = opf.batch_redact(["文本1", "文本2", "文本3"])

# 自定义模式
opf_typed = OPFWrappedModel(mode="typed")
opf_redacted = OPFWrappedModel(mode="redacted")
```

### 4. 8类PII检测类型

| 标签 | 中文说明 | 示例 |
|------|---------|------|
| `private_person` | 私人人员信息 | 张三、李四、王五 |
| `private_date` | 私人日期 | 1990-01-02、生日 |
| `private_email` | 私人邮箱 | user@example.com |
| `private_phone` | 私人电话 | 138-1234-5678 |
| `private_address` | 私人地址 | 北京市朝阳区xxx |
| `account_number` | 账户号码 | 银行卡号、账号 |
| `private_url` | 私人URL | 个人网站链接 |
| `secret` | 密钥/密码 | API密钥、密码 |

### 5. 输出格式

```json
{
  "schema_version": 1,
  "summary": {
    "output_mode": "typed",
    "span_count": 2,
    "by_label": {
      "private_person": 1,
      "private_email": 1
    },
    "decoded_mismatch": false
  },
  "text": "张三的邮箱是 zhangsan@example.com",
  "detected_spans": [
    {"label": "private_person", "start": 0, "end": 2, "text": "张三", "placeholder": "<PRIVATE_PERSON>"},
    {"label": "private_email", "start": 6, "end": 26, "text": "zhangsan@example.com", "placeholder": "<PRIVATE_EMAIL>"}
  ],
  "redacted_text": "<PRIVATE_PERSON>的邮箱是 <PRIVATE_EMAIL>"
}
```

### 6. 数据格式（微调/评估）

```jsonl
{"text": "张三的邮箱是 zhangsan@example.com", "spans": [[0, 2, "private_person"], [6, 26, "private_email"]]}
{"text": "李四的电话是 13812345678", "spans": [[0, 2, "private_person"], [8, 18, "private_phone"]]}
```

### 7. 自定义标签空间微调

```bash
# 创建自定义标签配置
cat > custom_labels.json << 'EOF'
{
  "category_version": "custom_v1",
  "span_class_names": ["O", "chinese_name", "chinese_phone", "chinese_id"]
}
EOF

# 微调
opf train ./train.jsonl \
  --validation-dataset ./dev.jsonl \
  --label-space-json custom_labels.json \
  --output-dir ./finetuned_chinese
```

### 8. ETL管道集成

```python
from opf_core.batch_processor import ETLRedactionNode

# 数据管道脱敏节点
class PIIRedactionNode:
    def __init__(self, mode="typed"):
        self.opf = OPFWrappedModel(mode=mode)

    def process_record(self, record: dict) -> dict:
        text = record.get("content", "")
        result = self.opf.redact(text)
        record["content_clean"] = result["redacted_text"]
        record["pii_count"] = result["summary"]["span_count"]
        record["pii_types"] = result["summary"]["by_label"]
        return record

    def process_batch(self, records: list) -> list:
        return [self.process_record(r) for r in records]

# 使用
node = PIIRedactionNode()
clean_records = node.process_batch(dirty_records)
```

### 9. 合规审计报告

```python
def privacy_audit_report(dataset_path: str) -> dict:
    """生成隐私合规审计报告"""
    result = subprocess.run(
        ["opf", "eval", dataset_path, "--eval-mode", "typed"],
        capture_output=True, text=True
    )

    # 解析评估结果
    # 生成审计报告：PII覆盖率、误报率、漏报率
    return {
        "total_samples": len(dataset),
        "pii_detected": summary["span_count"],
        "coverage_by_type": summary["by_label"],
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1": metrics["f1"]
    }
```

## L3: 天龙引擎协同命令

```bash
# 05安全师 - 隐私合规审计
[@安全师] 使用privacy-filter扫描这段文本中的PII
[@安全师] 检测日志文件中的隐私信息并脱敏
[@安全师] 隐私合规审查：评估8类PII检测覆盖率

# 19数据工程师 - ETL脱敏
[@数据工程师] 在数据管道中添加PII脱敏节点
[@数据工程师] 构建日志脱敏ETL管道

# 04验证师 - 测试数据保护
[@验证师] 脱敏测试数据集
[@验证师] 验证输出数据不含PII

# 17数据分析师 - 报告脱敏
[@数据分析师] 生成分析报告前脱敏原始数据
[@数据分析师] 统计报告中的PII分布情况
```

## L4: 注意事项

### ⚠️ 重要声明

> OPF是一个数据最小化辅助工具，不应作为唯一的匿名化或合规保证手段。

### 使用限制

1. **高风险场景**：医疗、法律、金融等场景需人工复核
2. **准确率限制**：模型非100%准确，可能存在漏检/误检
3. **语境依赖**：某些隐私信息需要上下文判断（如"北京"可能是地点也可能是公司名）
4. **中文扩展**：默认模型针对英文优化，中文PII建议微调

### 性能考虑

| 场景 | 延迟 | 建议 |
|------|------|------|
| 单条即时检测 | ~100ms | 实时交互 |
| 批量处理(100条) | ~10s | 异步任务 |
| 大文件(>1MB) | ~1min | 分块处理 |

## L5: 扩展方向

### 中文PII扩展

```python
# 中文姓名检测（基于现有private_person）
custom_labels = ["O", "chinese_name", "chinese_phone", "chinese_id", "chinese_address"]

# 微调命令
opf train chinese_pii.jsonl \
  --label-space-json chinese_labels.json \
  --output-dir ./chinese_pii_model
```

### 行业定制

| 行业 | 自定义标签 | 应用场景 |
|------|-----------|---------|
| **金融** | account_number, card_number, transaction_id | 银行卡号、交易流水 |
| **医疗** | patient_id, medical_record, prescription | 病历、处方脱敏 |
| **电商** | order_id, shipping_address, phone | 订单数据脱敏 |

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-01 | 初始集成，OPF核心封装 |