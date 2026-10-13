---
license: UNKNOWN
triggers: ["multi schema normalizer", "multi-schema-normalizer — 多结构归一化引擎"]
---
# multi-schema-normalizer — 多结构归一化引擎

> 来源: blogger-distiller/scripts/crawl_blogger.py _extract_supplement_entry() 通用化提取
> 版本: V1.0 | 状态: P1 实现完成

---

## 一句话描述

通用多结构 API 响应归一化引擎，支持同一平台 4 种响应格式的自动探测与统一输出。

---

## 核心能力

### 1. 四结构归一化（D→B→A→C 优先级链）

从 blogger-distiller 源码提取的 4 种响应结构，D 优先级最高、C 最低：

```
┌─────────────────────────────────────────────────────────────┐
│  优先级链: D → B → A → C（首个匹配的结构生效）            │
├─────────────────────────────────────────────────────────────┤
│  D: items[0].noteCard       最高  Router 归一化后的web_v3  │
│  B: note_list[0]+comment_list    中等  标准双字段结构       │
│  A: note+comments.list          中等  经典嵌套结构         │
│  C: detail本身即note对象          最低  降级兜底结构         │
└─────────────────────────────────────────────────────────────┘
```

### 2. 结构 D（Router 归一化 web_v3）

优先级最高，来自 Router 归一化后的格式：

```python
# 源格式
detail = {
    "items": [{
        "noteCard": { ... },      # 核心笔记对象
        "note_card": { ... },      # 蛇形变体
        "note": { ... },           # 直接笔记
        "_comments": { "list": [...] }
    }]
}

# 归一化输出
{"note": noteCard, "comments": {"list": [...]}, "_feed_id": note_id}
```

**关键字段**：`items[0].noteCard` — Router 层已做统一映射。

### 3. 结构 B（标准双字段结构）

```python
# 源格式
detail = {
    "note_list": [{ ... }],        # 笔记列表
    "comment_list": [...]           # 评论列表（平铺）
}

# 归一化输出
{"note": note_list[0], "comments": {"list": comment_list}, "_feed_id": note_id}
```

**识别特征**：`note_list` + `comment_list` 并存。

### 4. 结构 A（经典嵌套结构）

```python
# 源格式
detail = {
    "note": { ... },              # 笔记对象
    "noteData": { ... },           # 变体
    "comments": {
        "list": [...],             # 评论列表
        "comments": [...]          # 别名
    }
}

# 归一化输出
{"note": note, "comments": {"list": comments.list}, "_feed_id": note_id}
```

**识别特征**：`note` + `comments.list` 嵌套。

### 5. 结构 C（降级兜底结构）

```python
# 源格式
detail = {
    "noteId": "...",              # 小红书ID
    "note_id": "...",              # 蛇形变体
    "desc": "...",                 # 正文内容
    # 无note嵌套，detail本身即笔记对象
}

# 归一化输出
{"note": detail, "comments": {"list": []}, "_feed_id": noteId}
```

**触发条件**：`noteId` 或 `note_id` 或 `desc` 存在且前三种结构均无有效 `note_obj`。

### 6. 评论提取三层回退

评论数据可能在多个位置，回退顺序：

```python
# 第一层: noteCard._comments
inner_comments = note_obj.get("_comments")

# 第二层: items[0]._comments
if not inner_comments:
    inner_comments = first_item.get("_comments") or first_item.get("comments")

# 第三层: 解析评论列表
if isinstance(inner_comments, dict):
    comment_list_raw = inner_comments.get("list") or inner_comments.get("comments")
elif isinstance(inner_comments, list):
    comment_list_raw = inner_comments
```

### 7. 返回结构

所有结构统一输出：

```python
{
    "note": note_obj,              # 笔记主体（dict）
    "comments": {"list": [...]},   # 评论列表（统一包装）
    "_feed_id": note_id             # 笔记ID（溯源用）
}
```

---

## 二、通用化改造要点

从 blogger-distiller 源码提取时做了以下通用化：

| 原字段 | 通用化 |
|--------|--------|
| `items[0].noteCard` | 任意 `primary_list[0].primary_key` |
| `note_list[0]` | 任意 `items_list_key` |
| `comment_list` | 任意 `comments_key` |
| `_feed_id` | 任意 `item_id_field` |
| `noteId`/`note_id`/`desc` | 任意 C 结构识别字段 |

---

## 三、API 参考

```python
from multi_schema_normalizer import (
    normalize_entry,
    AutoSchemaDetector,
    NORMALIZER_CONFIG,
    STRUCTURE_D,
    STRUCTURE_B,
    STRUCTURE_A,
    STRUCTURE_C
)

# 基础归一化
result = normalize_entry(raw_data, note_id="12345")
# → {"note": {...}, "comments": {"list": [...]}, "_feed_id": "12345"}

# 自动探测结构类型
detector = AutoSchemaDetector()
structure_type = detector.detect(raw_data)
# → "D" | "B" | "A" | "C"

# 配置化归一化（通用平台）
config = {
    "primary_list_key": "items",
    "primary_obj_key": "noteCard",
    "items_list_key": "note_list",
    "comments_list_key": "comment_list",
    "note_key": "note",
    "comments_nested_key": "comments.list",
    "fallback_note_fields": ["noteId", "note_id", "desc"],
    "id_field": "_feed_id"
}
result = normalize_with_config(raw_data, note_id, config)
```

### 核心函数

```python
def normalize_entry(raw: dict, note_id: str = None) -> dict:
    """归一化单条API响应，返回统一结构"""

def detect_structure(raw: dict) -> str:
    """探测响应所属结构类型: D/B/A/C"""

def normalize_with_config(raw: dict, note_id: str,
                          config: dict) -> dict:
    """基于配置归一化（通用平台适配）"""

def extract_comments(obj: dict, note_obj: dict = None) -> list:
    """从任意位置提取评论列表"""

class AutoSchemaDetector:
    def detect(self, raw: dict) -> str:
        """自动识别结构类型"""

    def get_priority_order(self) -> list:
        """返回结构优先级列表"""

    def is_structure_d(self, raw: dict) -> bool:
    def is_structure_b(self, raw: dict) -> bool:
    def is_structure_a(self, raw: dict) -> bool:
    def is_structure_c(self, raw: dict) -> bool:
```

---

## 四、天龙岗位集成

| 岗位 | 集成方式 |
|------|---------|
| **19-01 数据工程师** | 数据管道核心依赖，API 响应标准化 |
| **17-01 数据分析师** | 采集后数据归一化，质量分级前置 |
| **35-06 博主蒸馏分析师** | Engine 1 数据采集管道，P0 universal-api-client 下游 |

---

## 五、CLI 命令

```bash
# 探测结构类型
schema-detect ./response.json

# 归一化转换
schema-normalize ./raw_data.json --output normalized.json

# 批量归一化
schema-normalize-batch ./data/*.json --output ./normalized/

# 结构分析报告
schema-analyze ./data.json --format report

# 配置化归一化（通用平台）
schema-normalize --config ./xiaohongshu.json ./data.json
```

---

## 六、预期收益

| 指标 | 提升 |
|------|------|
| API 响应解析成功率 | 60%（单结构）→ 99%（4结构回退） |
| 数据解析崩溃率 | ~15% → 0%（C 结构兜底） |
| 代码复用率 | +300%（多平台通用） |

---

## 七、依赖关系

```
multi-schema-normalizer/
├── schema_detector.py     # AutoSchemaDetector 自动探测
├── normalizer.py         # normalize_entry 核心归一化
├── config.py             # 默认配置 NORMALIZER_CONFIG
├── adapters/
│   └── xiaohongshu.py  # 小红书平台适配器
└── templates/
    └── config.json      # 配置模板
```

---

*基于 blogger-distiller V1.5 crawl_blogger.py _extract_supplement_entry() 提取通用化*
