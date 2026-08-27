# Python Code Node 示例 - 数据处理

## 概述

n8n Python Code 节点使用 Python 3.10 处理数据转换、计算和逻辑操作。

## 基础示例

### 1. 数据映射

```python
# 将输入数据转换为大写键名
import json

items = $input.all()

new_items = []
for item in items:
    new_item = {}
    for key, value in item.json.items():
        new_item[key.upper()] = value
    new_items.append({"json": new_item})

return new_items
```

### 2. 数据过滤

```python
# 只保留状态为 active 的记录
items = $input.all()

filtered_items = [
    item for item in items
    if item.json.get('status') == 'active'
]

if not filtered_items:
    return [{"json": {"message": "No active items found"}}]

return filtered_items
```

### 3. 数据聚合

```python
# 计算统计数据
from statistics import mean

items = $input.all()

values = [item.json.get('amount', 0) for item in items]
total = sum(values)
count = len(values)
average = mean(values) if count > 0 else 0

return [{
    "json": {
        "total": total,
        "count": count,
        "average": round(average, 2),
        "min": min(values) if values else 0,
        "max": max(values) if values else 0
    }
}]
```

### 4. 数据分组

```python
from collections import defaultdict

items = $input.all()

grouped = defaultdict(list)
for item in items:
    category = item.json.get('category', 'uncategorized')
    grouped[category].append(item.json)

result = []
for category, items_list in grouped.items():
    result.append({
        "json": {
            "category": category,
            "items": items_list,
            "count": len(items_list)
        }
    })

return result
```

## 高级示例

### 5. 日期时间处理

```python
from datetime import datetime, timedelta
import pytz

items = $input.all()

result = []
for item in items:
    created_at = item.json.get('created_at')
    if created_at:
        # 解析日期字符串
        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

        # 计算与现在的时间差
        now = datetime.now(pytz.UTC)
        delta = now - dt

        result.append({
            "json": {
                **item.json,
                "days_ago": delta.days,
                "hours_ago": delta.total_seconds() / 3600,
                "is_recent": delta.days < 7,
                "formatted_date": dt.strftime('%Y-%m-%d %H:%M:%S')
            }
        })

return result
```

### 6. 字符串处理

```python
import re

items = $input.all()

result = []
for item in items:
    text = item.json.get('text', '')

    result.append({
        "json": {
            "original": text,
            "trimmed": text.strip(),
            "uppercase": text.upper(),
            "lowercase": text.lower(),
            "word_count": len(text.split()),
            "char_count": len(text),
            "has_numbers": bool(re.search(r'\d', text)),
            "has_emails": bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)),
            "slug": re.sub(r'[^\w\s-]', '', text.lower()).strip().replace(' ', '-')
        }
    })

return result
```

### 7. 数据验证

```python
import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone):
    pattern = r'^\+?[\d\s\-\(\)]+$'
    return bool(re.match(pattern, phone)) and len(re.sub(r'[^\d]', '', phone)) >= 10

items = $input.all()

result = []
for item in items:
    email = item.json.get('email', '')
    phone = item.json.get('phone', '')

    result.append({
        "json": {
            **item.json,
            "email_valid": validate_email(email),
            "phone_valid": validate_phone(phone),
            "has_valid_contact": validate_email(email) or validate_phone(phone)
        }
    })

return result
```

### 8. JSON 数据处理

```python
import json
from copy import deepcopy

items = $input.all()

result = []
for item in items:
    data = item.json

    # 深拷贝数据
    data_copy = deepcopy(data)

    # 展开嵌套的配置对象
    if 'config' in data_copy and isinstance(data_copy['config'], dict):
        for key, value in data_copy['config'].items():
            data_copy[f'config_{key}'] = value
        del data_copy['config']

    # 格式化 JSON 字符串
    if 'raw_json' in data_copy:
        try:
            parsed = json.loads(data_copy['raw_json'])
            data_copy['parsed_json'] = parsed
        except json.JSONDecodeError as e:
            data_copy['parse_error'] = str(e)

    result.append({"json": data_copy})

return result
```

### 9. 条件逻辑与分支

```python
items = $input.all()

result = []
for item in items:
    score = item.json.get('score', 0)

    # 多条件评分
    if score >= 90:
        grade = 'A'
        status = '优秀'
        bonus = 10
    elif score >= 80:
        grade = 'B'
        status = '良好'
        bonus = 5
    elif score >= 70:
        grade = 'C'
        status = '中等'
        bonus = 2
    elif score >= 60:
        grade = 'D'
        status = '及格'
        bonus = 0
    else:
        grade = 'F'
        status = '不及格'
        bonus = -5

    final_score = max(0, min(100, score + bonus))

    result.append({
        "json": {
            **item.json,
            "grade": grade,
            "status": status,
            "bonus": bonus,
            "final_score": final_score
        }
    })

return result
```

### 10. 批量数据处理

```python
import math

def chunk_list(lst, chunk_size):
    """将列表分块"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

items = $input.all()

# 获取所有 ID
ids = [item.json.get('id') for item in items if item.json.get('id')]

# 分批处理（每批 100 个）
batches = chunk_list(ids, 100)

result = []
for i, batch in enumerate(batches, 1):
    result.append({
        "json": {
            "batch_number": i,
            "batch_size": len(batch),
            "ids": batch,
            "total_batches": len(batches)
        }
    })

return result
```

## 实用工具函数

### 数据清洗

```python
import re

def clean_text(text):
    """清洗文本数据"""
    if not isinstance(text, str):
        return text

    # 移除多余空格
    text = ' '.join(text.split())

    # 移除特殊字符（可选）
    # text = re.sub(r'[^\w\s\-\.]', '', text)

    # 标准化换行符
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    return text.strip()

def clean_data(data):
    """递归清洗数据结构中的所有字符串"""
    if isinstance(data, dict):
        return {k: clean_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_data(item) for item in data]
    elif isinstance(data, str):
        return clean_text(data)
    else:
        return data

items = $input.all()

result = []
for item in items:
    cleaned_data = clean_data(item.json)
    result.append({"json": cleaned_data})

return result
```

### 数据去重

```python
def deduplicate_items(items, key_field='id'):
    """根据指定字段去重"""
    seen = set()
    unique_items = []

    for item in items:
        key_value = item.json.get(key_field)
        if key_value not in seen:
            seen.add(key_value)
            unique_items.append(item)

    return unique_items

items = $input.all()

# 按 ID 去重
unique_items = deduplicate_items(items, 'id')

return [{
    "json": {
        "original_count": len(items),
        "unique_count": len(unique_items),
        "duplicates_removed": len(items) - len(unique_items)
    }
}]
```

### 数据合并

```python
from collections import defaultdict

def merge_data_by_key(items, key_field='id'):
    """合并具有相同键值的数据"""
    merged = defaultdict(dict)

    for item in items:
        key = item.json.get(key_field)
        if key:
            # 合并字典（后者覆盖前者）
            merged[key].update(item.json)

    return list(merged.values())

items = $input.all()

merged_data = merge_data_by_key(items, 'user_id')

return [{"json": item} for item in merged_data]
```

## 数据转换

### CSV 格式转换

```python
import csv
from io import StringIO

items = $input.all()

# 提取所有字段名
all_fields = set()
for item in items:
    all_fields.update(item.json.keys())

fieldnames = sorted(all_fields)

# 生成 CSV
output = StringIO()
writer = csv.DictWriter(output, fieldnames=fieldnames)
writer.writeheader()

for item in items:
    writer.writerow(item.json)

csv_data = output.getvalue()

return [{
    "json": {
        "csv": csv_data,
        "row_count": len(items),
        "field_count": len(fieldnames)
    }
}]
```

### XML 生成

```python
import dicttoxml
import xml.etree.ElementTree as ET

items = $input.all()

# 将字典转换为 XML
xml_data = dicttoxml.dicttoxml({
    'items': {
        'item': [item.json for item in items]
    }
})

# 美化 XML
root = ET.fromstring(xml_data)
pretty_xml = ET.tostring(root, encoding='unicode', method='xml')

return [{
    "json": {
        "xml": pretty_xml,
        "item_count": len(items)
    }
}]
```

## 性能优化

### 并行处理（使用生成器）

```python
def process_large_dataset(items):
    """处理大型数据集的生成器函数"""
    for item in items:
        # 处理每个项目
        processed = {
            **item.json,
            'processed': True,
            'timestamp': datetime.now().isoformat()
        }
        yield {"json": processed}

items = $input.all()

# 使用生成器逐个处理
return list(process_large_dataset(items))
```

### 内存高效处理

```python
def stream_process_items(items):
    """流式处理，减少内存占用"""
    result = []

    for i, item in enumerate(items):
        # 处理项目
        processed = {
            "json": {
                "index": i,
                "data": item.json,
                "processed": True
            }
        }

        result.append(processed)

        # 每 1000 个项目清理一次
        if i % 1000 == 0 and i > 0:
            yield result
            result = []

    if result:
        yield result

items = $input.all()

# 收集所有批次
all_results = []
for batch in stream_process_items(items):
    all_results.extend(batch)

return all_results
```

## 错误处理

### 安全数据处理

```python
import traceback

def safe_process_item(item):
    """安全处理单个项目，捕获所有异常"""
    try:
        # 尝试处理数据
        result = {
            **item.json,
            'value_doubled': item.json.get('value', 0) * 2,
            'status': 'success'
        }
        return {"json": result, "error": None}
    except Exception as e:
        # 返回错误信息
        return {
            "json": {
                **item.json,
                'status': 'error',
                'error_message': str(e)
            },
            "error": str(e)
        }

items = $input.all()

results = [safe_process_item(item) for item in items]

# 统计成功和失败
success_count = sum(1 for r in results if not r.get('error'))
error_count = len(results) - success_count

# 添加汇总信息
results.append({
    "json": {
        "summary": True,
        "total": len(items),
        "success": success_count,
        "errors": error_count
    }
})

return results
```

## 相关文档

- [JavaScript Code Node 示例](../javascript/data-transformation.md)
- [Code Node 最佳实践](../code-best-practices.md)
- [表达式语法](../../specs/expression-syntax.md)
