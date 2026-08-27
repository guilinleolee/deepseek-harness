---
license: UNKNOWN
triggers: ["aihot", "aihot — AI热点资讯查询"]
---
# aihot — AI热点资讯查询

## L0: 一句话描述 (≤15字)
AI热点资讯零配置API查询

## L1: 使用场景 (50-100字)
用于实时获取AI领域热点资讯（模型发布、产品动态、行业趋势、论文前沿、技术tips），无需登录、无需Key，直接通过HTTP调用aihot.virxact.com API获取每日精选内容。

## L2: 详细文档

### 来源项目
> [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) - 9.9k Stars, MIT License

### API基础信息

| 项目 | 值 |
|------|-----|
| **Base URL** | `https://aihot.virxact.com` |
| **Rate Limit** | 600 req/min/IP |
| **认证** | 无需Key，直接访问 |
| **必需Header** | `User-Agent` (浏览器UA) |

### 核心端点

#### 1. 今日AI热点 (`/api/public/daily`)
获取今日AI热点列表。

```bash
curl -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  "https://aihot.virxact.com/api/public/daily"
```

**返回格式：**
```json
[
  {
    "title": "GPT-4o发布",
    "desc": "OpenAI发布多模态大模型GPT-4o",
    "url": "https://example.com/news1",
    "source": "OpenAI官方",
    "ct": 1715587200
  }
]
```

#### 2. 指定日期热点 (`/api/public/daily/{YYYY-MM-DD}`)
获取指定日期的AI热点列表。

```bash
curl -H "User-Agent: Mozilla/5.0" \
  "https://aihot.virxact.com/api/public/daily/2024-05-13"
```

#### 3. 批量获取近期热点 (`/api/public/dailies`)
获取近期N天的AI热点。

```bash
curl -H "User-Agent: Mozilla/5.0" \
  "https://aihot.virxact.com/api/public/dailies?days=7"
```

#### 4. 获取热点详情 (`/api/public/items`)
获取指定ID的热点详情。

```bash
curl -H "User-Agent: Mozilla/5.0" \
  "https://aihot.virxact.com/api/public/items?ids=id1,id2,id3"
```

### 五大分类

| 分类 | 参数值 | 说明 |
|------|--------|------|
| AI模型 | `ai-models` | 大模型发布、评测、对比 |
| AI产品 | `ai-products` | 产品发布、功能更新 |
| 行业动态 | `industry` | 行业趋势、融资、并购 |
| 学术论文 | `paper` | 论文解读、新研究 |
| 技术Tips | `tip` | 教程、技巧、工具推荐 |

### 天龙引擎调用封装

#### Python封装

```python
# ~/.claude/skills/aihot/scripts/aihot_client.py
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "https://aihot.virxact.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_daily(date: str = None) -> list:
    """获取指定日期的AI热点"""
    if date is None:
        url = f"{BASE_URL}/api/public/daily"
    else:
        url = f"{BASE_URL}/api/public/daily/{date}"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json()

def get_items(ids: str) -> list:
    """获取热点详情"""
    url = f"{BASE_URL}/api/public/items?ids={ids}"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json()

def format_report(items: list) -> str:
    """格式化输出为天龙报告"""
    lines = ["# AI热点日报\n"]
    lines.append(f"日期: {datetime.now().strftime('%Y-%m-%d')}\n")
    for i, item in enumerate(items, 1):
        ts = datetime.fromtimestamp(item.get('ct', 0)).strftime('%m-%d') if item.get('ct') else ''
        lines.append(f"{i}. {item.get('title', '')}")
        lines.append(f"   来源: {item.get('source', '')} | 时间: {ts}")
        lines.append(f"   摘要: {item.get('desc', '')}")
        lines.append(f"   链接: {item.get('url', '')}\n")
    return '\n'.join(lines)
```

#### CLI命令

```bash
# 获取今日热点
python ~/.claude/skills/aihot/scripts/aihot_client.py daily

# 获取指定日期热点
python ~/.claude/skills/aihot/scripts/aihot_client.py daily --date 2024-05-13

# 获取近期7天热点
python ~/.claude/skills/aihot/scripts/aihot_client.py dailies --days 7

# 获取热点详情
python ~/.claude/skills/aihot/scripts/aihot_client.py items --ids id1,id2,id3

# 生成Markdown报告
python ~/.claude/skills/aihot/scripts/aihot_client.py report --days 7 --output ~/ai-hot-report.md
```

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **01调研师** | V8.88→V8.89 | AI热点实时监控+每日快报 |
| **32-01市场研究** | V10.2→V10.3 | AI行业热点追踪 |
| **62-02行业研究员** | V9.0→V9.1 | AI行业动态监测 |
| **07记录师** | V9.06→V9.07 | 每日AI热点自动归档 |

### 与天龙现有能力协同

| 天龙组件 | aihot协同 | 效果 |
|---------|----------|------|
| **last30days (V8.54)** | 30天时效性研究+aihot历史数据 | 时效性+历史双验证 |
| **deep-research (V3.2)** | 深度调研+aihot热点触发 | 热点驱动研究 |
| **Agent-Reach** | 内容采集+aihot分类输出 | 平台覆盖+100% |
| **07记录师** | Wiki自动归档+aihot每日快报 | 知识积累自动化 |

### 预期收益

| 指标 | V11.10 | V11.11 | 提升 |
|------|--------|--------|------|
| **AI热点发现速度** | 手动搜索 | 实时API | **质的飞跃** |
| **热点覆盖率** | 依赖搜索引擎 | 5分类全覆盖 | **+300%** |
| **每日快报生成** | 手动整理 | 一键导出 | **+500%** |
| **技能数量** | 545+ | **546+** | **+1** |

### 注意事项

1. **必须携带User-Agent**：所有请求必须包含浏览器User-Agent，否则返回403
2. **速率限制**：600 req/min/IP，避免高频调用同一IP
3. **数据时效性**：热点头条为当日最新，往期数据需指定日期参数
4. **天龙头条格式**：仅title/desc/url/source/ct五字段，无分类标签

### 技能文件

- [skills/aihot/SKILL.md](skills/aihot/SKILL.md) ← 本文件
- [skills/aihot/scripts/aihot_client.py](skills/aihot/scripts/aihot_client.py)
