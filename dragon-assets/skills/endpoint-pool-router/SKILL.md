---
license: UNKNOWN
triggers: ["endpoint pool router", "endpoint-pool-router — 多端点API池路由引擎"]
---
# endpoint-pool-router — 多端点API池路由引擎

> 来源: blogger-distiller/scripts/utils/endpoints.json + router 逻辑通用化提取
> 版本: V1.0 | 状态: P1 提案

---

## 一句话描述

通用多端点 API 池路由 + 死链自动缓存 + 优先级探测降级系统。

---

## 核心能力

### 1. 端点池配置（`EndpointPool`）

支持 7 大 API 池，每个池含 4 个优先级链路：

| 池 | 用途 | 优先级 |
|----|------|--------|
| `search_notes` | 关键词搜索笔记 | web_v3 → app → web_v2 → app_v2 |
| `search_users` | 关键词搜索用户 | web_v3 → app → web_v2 → app_v2 |
| `fetch_user_info` | 获取用户信息 | web_v3 → app → web_v2 → app_v2 |
| `fetch_user_notes` | 获取用户笔记列表 | web_v3 → app → web_v2 → app_v2 |
| `fetch_note_detail_image` | 图文笔记详情 | app → web_v3 → web_v2 → app_v2 |
| `fetch_note_detail_video` | 视频笔记详情 | app → web_v3 → web_v2 → app_v2 |
| `fetch_note_comments` | 获取笔记评论 | app → web_v3 → app_v2 → web_v2 |

**配置格式**：

```json
{
  "pools": {
    "search_notes": [
      {
        "group": "web_v3",
        "path": "/api/v1/xiaohongshu/web_v3/fetch_search_notes",
        "method": "GET",
        "params": {"keyword": "${keyword}", "page": "${page}", "sort": "general", "note_type": 0, "num": 20},
        "adapter": "search_notes_web_v3"
      }
    ]
  }
}
```

### 2. 模板语法（`${arg_key}`）

参数占位符自动替换：

```python
# 模板
params = {"keyword": "${keyword}", "page": "${page}"}
# 注入
resolved = resolve_template(params, keyword="咖啡", page=1)
# → {"keyword": "咖啡", "page": 1, "sort": "general", "note_type": 0, "num": 20}
```

### 3. 适配器注册（`@register`）

每个端点指定 adapter，适配器负责解析响应：

```python
from endpoint_pool_router import router, register

@register("search_notes_web_v3")
def parse_search_notes_web_v3(response: dict) -> list[dict]:
    items = response.get("data", {}).get("items", [])
    return [{"id": i.get("id"), "title": i.get("title")} for i in items]
```

### 4. 死链缓存（3层）

```python
# 层1：单端点死链（HTTP 错误）
_dead_endpoints = set()  # {"group:path"}

# 层2：端点组死链（全组 400/500）
_dead_category_groups = set()  # {"group:pool"}

# 层3：HTTP 400 计数器（Token 失效检测）
_http400_counts = defaultdict(int)  # {(group, path): count}
```

### 5. 降级策略矩阵

| 错误类型 | 触发条件 | 降级动作 |
|---------|---------|---------|
| HTTP 400 | 响应 400 | 跳过当前端点，降级到下一优先级 |
| HTTP 500 | 响应 500 | 跳过当前端点，降级到下一优先级 |
| HTTP 429 | 速率限制 | 等待 2s 重试，仍失败则降级 |
| HTTP 401/403 | Token 失效 | 标记 `_http400_counts`，触发 Token 轮换 |
| 空响应 | data 为空 | 降级到下一端点 |
| 连接超时 | 超时 | 降级到下一端点 |

### 6. 探测路由（`probe`）

category-independent 自动探测当前可用端点：

```python
def probe(pool_name: str, **kwargs) -> tuple[dict, str]:
    """探测第一个可用端点，返回 (parsed_data, endpoint)"""
    for endpoint in pool_config[pool_name]:
        group = endpoint["group"]
        path = endpoint["path"]

        # 跳过已知死链
        if f"{group}:{path}" in _dead_endpoints:
            continue
        if group in _dead_category_groups:
            continue

        resolved_params = resolve_template(endpoint["params"], **kwargs)
        response = http_call(endpoint["method"], path, resolved_params)

        if is_success(response):
            parsed = endpoint["adapter"](response)
            return parsed, f"{group}:{path}"

        # 记录死链
        record_dead_link(response, group, path, pool_name)

    raise AllEndpointsDead(f"Pool '{pool_name}' all endpoints failed")
```

### 7. Token 轮换

```python
def rotate_token():
    """在 Token 失效时自动切换备用 Token"""
    global _active_token
    _active_token = _backup_tokens[_active_token]
    _http400_counts.clear()  # 重置计数器
```

---

## 二、通用化改造要点

从 blogger-distiller 提取时做了以下通用化：

| 原字段 | 通用化 |
|--------|--------|
| `TikHub URL` | 任意 API 基础 URL 可配置 |
| `/api/v1/xiaohongshu/...` | 任意 `path` 模板 |
| `_dead_endpoints` | 任意 `(group, path)` 元组缓存 |
| `search_notes` | 任意 pool name |
| `"_note": "..."` | 任意 adapter 解析函数 |

---

## 三、API 参考

```python
from endpoint_pool_router import (
    EndpointPool,
    resolve_template,
    probe,
    record_dead_link,
    rotate_token,
    register,
    DEFAULT_THRESHOLDS
)

# 初始化
pool = EndpointPool(config_path="./endpoints.json", base_url="https://...")
pool.set_token("YOUR_TOKEN")
pool.set_backup_tokens(["TOKEN_A", "TOKEN_B"])

# 探测调用
result, endpoint = pool.probe("search_notes", keyword="咖啡", page=1)
print(f"命中: {endpoint}, 数据条数: {len(result)}")

# 注册自定义适配器
@pool.register("custom_adapter")
def parse_custom(response: dict) -> list:
    return response.get("items", [])
```

---

## 四、天龙岗位集成

| 岗位 | 集成方式 |
|------|---------|
| **17-01 数据分析师** | 采集管道核心依赖，P0-1 universal-api-client 下游 |
| **35-06 博主蒸馏分析师** | Engine 2 端点路由，3轮采集管道 |
| **01 调研师** | 增强任意多端点 API 探测能力 |

---

## 五、CLI 命令

```bash
# 探测端点
endpoint-router probe search_notes --keyword "咖啡" --page 1

# 查看死链状态
endpoint-router status --pool search_notes

# 清除死链缓存
endpoint-router reset --pool search_notes --group web_v3

# Token 轮换
endpoint-router rotate-token

# 添加新池
endpoint-router add-pool fetch_note_comments ./new_pool.json
```

---

## 六、预期收益

| 指标 | 提升 |
|------|------|
| API 成功率 | 60-70% → 99%+（多端点回退） |
| 端点切换延迟 | 手动 → <2s 自动切换 |
| Token 节省 | -70%（避免无效请求） |
| 死链发现时间 | 小时级 → 秒级自动检测 |

---

## 七、依赖关系

```
endpoint-pool-router/
├── endpoints.json           # 端点池配置（可替换为任意平台）
├── router.py              # 核心路由逻辑
├── adapters/              # 适配器目录
│   ├── search_notes.py
│   ├── fetch_user_info.py
│   └── fetch_note_comments.py
└── cache.py               # 死链缓存（SQLite 持久化）
```

---

*基于 blogger-distiller V1.5 endpoints.json + router.py 提取通用化*
