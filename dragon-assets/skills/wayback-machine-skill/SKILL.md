---
license: UNKNOWN
triggers: ["wayback machine skill", "Wayback Machine SKILL"]
---
# Wayback Machine SKILL

> 互联网历史档案馆 —— 网页历史版本恢复与归档

## L0: 一句话描述 (≤15字)
恢复任意网页历史版本

## L1: 使用场景 (50-100字)
当用户需要查看网页的过去状态、恢复已删除内容、追踪页面演变历史，或需要引用某个时间点的网页快照时触发。支持所有公网URL的Wayback Machine存档查询。

## L2: 详细文档

### 核心能力

| 能力 | 说明 | 优先级 |
|------|------|--------|
| 快照查询 | 查询URL在Wayback Machine的存档时间线 | P0 |
| 版本恢复 | 获取指定日期的历史版本内容 | P0 |
| 可用性检测 | 检查URL是否有可用存档 | P1 |
| 批量归档 | 批量提交URL到Wayback Machine | P1 |
| 变更追踪 | 对比不同时间点的页面差异 | P2 |

### 工作流程

```
1. 接收URL → 2. 查询存档时间线 → 3. 获取历史版本 → 4. 内容处理 → 5. 交付结果
```

### API调用

**Archive.org CDX API** (查询存档列表):
```bash
curl "http://web.archive.org/cdx/search/cdx?url=example.com&output=json&limit=10"
```

**Wayback API** (获取快照):
```bash
# 获取最近版本
curl "https://web.archive.org/web/20240101/https://example.com"

# 获取指定日期版本
curl "https://web.archive.org/web/20240101120000/https://example.com"

# 获取第一个存档版本
curl "https://web.archive.org/web/0/https://example.com"

# 获取最后一个存档版本
curl "https://web.archive.org/web/2/https://example.com"
```

**Availability API** (检查是否存档):
```bash
curl "http://archive.org/wayback/available?url=https://example.com/page"
```

### 脚本实现

**wayback_search.py** - 存档查询:
```python
#!/usr/bin/env python3
"""Wayback Machine存档查询工具"""
import requests
import json
import sys
from datetime import datetime

ARCHIVE_CDX = "http://web.archive.org/cdx/search/cdx"
ARCHIVE_WAYBACK = "https://web.archive.org/web"
ARCHIVE_AVAIL = "http://archive.org/wayback/available"

def check_available(url: str) -> dict:
    """检查URL是否有可用存档"""
    resp = requests.get(ARCHIVE_AVAIL, params={"url": url}, timeout=10)
    data = resp.json()
    if data.get("archived_snapshots", {}).get("closest"):
        return data["archived_snapshots"]["closest"]
    return None

def search_snapshots(url: str, limit: int = 20) -> list:
    """搜索URL的存档时间线"""
    params = {
        "url": url,
        "output": "json",
        "limit": limit,
        "fl": "timestamp,statuscode,original"
    }
    resp = requests.get(ARCHIVE_CDX, params=params, timeout=15)
    if resp.status_code == 200:
        data = resp.json()
        if len(data) > 1:
            return data[1:]  # 跳过header行
    return []

def get_snapshot(url: str, timestamp: str = None) -> dict:
    """获取指定时间戳的快照"""
    if timestamp:
        wayback_url = f"{ARCHIVE_WAYBACK}/{timestamp}/{url}"
    else:
        wayback_url = f"{ARCHIVE_WAYBACK}/0/{url}"

    resp = requests.get(wayback_url, timeout=30, allow_redirects=True)
    return {
        "url": str(resp.url),
        "status": resp.status_code,
        "content": resp.text[:5000] if resp.status_code == 200 else None,
        "timestamp": timestamp
    }

def archive_url(url: str) -> dict:
    """提交URL到Wayback Machine归档"""
    save_url = f"https://web.archive.org/save/{url}"
    resp = requests.get(save_url, timeout=60, allow_redirects=True)
    return {"status": "submitted" if resp.status_code in [200, 301, 302] else "failed"}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    target = sys.argv[2] if len(sys.argv) > 2 else ""

    if cmd == "check" and target:
        result = check_available(target)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif cmd == "search" and target:
        result = search_snapshots(target)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif cmd == "get":
        ts = sys.argv[3] if len(sys.argv) > 3 else None
        result = get_snapshot(target, ts)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif cmd == "archive" and target:
        result = archive_url(target)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("用法: wayback_search.py [check|search|get|archive] <url> [timestamp]")
```

### 天龙引擎集成

| 天龙岗位 | 集成方式 |
|----------|-----------|
| 01调研师 | 调研时验证信息历史来源，存档失效页面 |
| 07记录师 | 归档重要文档的历史版本，知识持久化 |
| 06审查师 | 审查代码历史变更，追踪文档修改记录 |
| 09-02编排 | 批量归档工作流编排 |

### 使用命令

```bash
# 检查可用性
python3 ~/.claude/skills/wayback-machine-skill/scripts/wayback_search.py check "https://example.com"

# 搜索存档时间线
python3 ~/.claude/skills/wayback-machine-skill/scripts/wayback_search.py search "https://example.com"

# 获取历史版本
python3 ~/.claude/skills/wayback-machine-skill/scripts/wayback_search.py get "https://example.com" 20240101

# 提交归档
python3 ~/.claude/skills/wayback-machine-skill/scripts/wayback_search.py archive "https://example.com"
```

### 适用场景

- **信息核实**: 查看新闻页面原始版本，对比发布时间前后的内容变化
- **文档恢复**: 恢复误删的文档内容，追踪文档修改历史
- **历史研究**: 获取某个时间点的网页快照，用于研究分析
- **证据保全**: 将网页内容存档作为时间戳证据
- **竞品分析**: 追踪竞品页面的历史变更

### 限制与注意事项

1. **隐私限制**: Wayback Machine有 robots.txt 限制
2. **存档覆盖**: 并非所有页面都有存档，越老的URL存档率越低
3. **动态内容**: JavaScript渲染的内容可能无法完整存档
4. **提交限制**: 提交归档需要等待队列处理，非即时
5. **API限制**: 大规模查询需遵守CDX API使用规范

## 文件结构

```
wayback-machine-skill/
├── SKILL.md                    # 本文件
├── scripts/
│   └── wayback_search.py      # 核心脚本
└── README.md                   # 使用说明
```

## 版本信息

- **版本**: 1.0.0
- **更新日期**: 2026-05-07
- **来源**: Internet Archive Wayback Machine
- **_stars**: N/A