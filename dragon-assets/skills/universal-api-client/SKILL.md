---
license: UNKNOWN
triggers: ["universal api client", "universal-api-client — 通用API适配器客户端"]
---
# universal-api-client — 通用API适配器客户端

## L0: 一句话描述
通过适配器归一化层 + 端点池路由器，实现任意REST API的多端点自动降级调用。

## L1: 使用场景
- 调用TikHub/第三方API时，需要自动降级和结果归一化
- 多endpoint实现同一功能，需要故障转移
- API返回结构不一致，需要统一转换为内部格式
- 启动时探测可用端点，按延迟动态排序

## L2: 详细文档

### 核心架构

```
┌─────────────────────────────────────────────────────────────┐
│                UniversalApiClient 三层架构                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 3: 调用层 (caller code)                             │
│    client.call("pool_name", {"arg": value})                │
│                                                             │
│  Layer 2: 路由层 (EndpointRouter)                          │
│    ├── 从 endpoints.json 加载端点池配置                    │
│    ├── 按优先级尝试端点（健康检查后动态排序）              │
│    ├── 失败时自动降级到下一个端点                         │
│    ├── 会话内缓存死链（同group同category级联标记）         │
│    └── 调用 Adapter 归一化返回                             │
│                                                             │
│  Layer 1: 适配器层 (adapters.py)                          │
│    ├── 注册各端点专用的 response → internal 转换函数       │
│    ├── 检测"假成功"（HTTP 200 但数据为空）                │
│    └── 返回统一 internal 格式                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### endpoints.json 配置格式

```json
{
  "pools": {
    "pool_name": [
      {
        "group": "primary",
        "path": "/api/v1/resource",
        "method": "GET",
        "params": {"key": "${arg_key}"},
        "adapter": "adapter_name_in_adapters_py",
        "_note": "2026-04-23 实测200，提为首选"
      },
      {
        "group": "fallback",
        "path": "/api/v1/v2/resource",
        "method": "GET",
        "params": {"key": "${arg_key}"},
        "adapter": "adapter_name_in_adapters_py",
        "_note": "实测400，降为备选"
      }
    ]
  }
}
```

### 适配器注册（adapters.py）

```python
# adapters.py 格式
ADAPTERS = {}

def register(name):
    """装饰器：注册适配器"""
    def decorator(func):
        ADAPTERS[name] = func
        return func
    return decorator

@register("user_notes_web_v3")
def user_notes_web_v3(raw, args):
    """web_v3 用户笔记适配器 — 将TikHub响应归一化为内部格式"""
    items = raw.get("data", {}).get("notes", [])
    return {"items": items, "total": raw.get("data", {}).get("total", 0)}
```

### 路由器核心用法

```python
from utils.endpoint_router import EndpointRouter

# 初始化
router = EndpointRouter(request_func)  # request_func: (method, path, params) → raw_response

# 标准调用
result = router.call("fetch_user_notes", {
    "user_id": "xxx",
    "cursor": ""
})

# 获取结果中的元信息（用于轮次2补调排除已用端点）
endpoint_used = result.get("_endpoint_used")  # "web_v3:/api/v1/..."
endpoint_group = result.get("_endpoint_group")  # "web_v3"

# 启动时探测 + 动态排序
router.auto_probe_and_reorder()

# 重置死链缓存（手动恢复）
router.reset_dead_cache()
router.reset_category_cache("comments")
```

### 降级策略（EndpointRouter.DEGRADABLE_CODES）

| 状态码 | 行为 |
|--------|------|
| 400 | 同端点连续3次→标死链（不走category级联） |
| 500/502/503/504/404 | 立即标死链 + category级联标记 |
| 429 | 记录错误，继续降级，不标死链 |
| 401/402/403 | 不降级，直接抛出 |
| HTTP 200+空数据 | 软失败计数，阈值触发后标死链 |

### 类别独立探测（auto_probe_and_reorder）

```python
# 每个 category（search/user/detail/comments）用自己类别的端点探测
# detail 端点400不会误杀 search 端点
_cat_repr = {}
for pn, eps in self._pools.items():
    cat = self._pool_categories.get(pn, pn)
    if cat not in _cat_repr and eps:
        _cat_repr[cat] = eps  # 每个category只选一个代表池

for cat, eps in _cat_repr.items():
    result = _probe_pool(eps, cat)  # 独立探测，互不影响
```

### 死链缓存三层结构

```
_dead_endpoints           # 精确匹配: "group:path" → True
_dead_category_groups     # category级联: "category:group" → True
_http400_counts           # 连续400计数: "group:path" → int（触发阈值才标死）
```

### 核心命令

```bash
# 健康检查（输出所有池可用性报告）
python scripts/health_check.py

# 探测 + 重排序
python scripts/auto_probe.py

# 手动重置缓存
python scripts/reset_cache.py --category comments

# 端点池管理
python scripts/pool_manager.py list
python scripts/pool_manager.py add search_notes --group web_v4 --path /api/v1/...
```

### 与天龙引擎现有技能协同

| 天龙技能 | 协同方式 |
|---------|---------|
| `claude-api` | 调用方用 Sonnet/Opus，UniversalApiClient 内部路由到 TikHub |
| `api-design` | endpoints.json 即 API 端点池设计的声明式配置 |
| `retry-pattern` | 路由器自带 retry，替代手动 retry 逻辑 |
| `xhs-images` / `twitter-operations` | 替换为 UniversalApiClient 统一管理 |

### 质量标准

- [ ] endpoints.json 语法校验（缺少字段/无效adapter抛出 ValueError）
- [ ] 适配器注册完整性检查（启动时校验所有 adapter 存在）
- [ ] 探测时记录延迟和状态
- [ ] 死链缓存跨会话不持久化（仅会话内有效）
- [ ] category 独立探测验证（detail 400 不影响 search）

### 适用岗位

| 岗位 | 用途 |
|------|------|
| **35-06 博主蒸馏分析师** ⭐新增 | 底层API客户端 |
| **01调研师** | 通用API调用 |
| **03构建师** | 封装为可复用SDK |

### 依赖文件

```
scripts/
├── adapters.py              # 适配器归一化层（22个已注册适配器）
├── endpoint_router.py       # 端点池路由器（461行）
├── utils/
│   ├── endpoints.json       # 端点池配置（7池×4端点）
│   └── quality.py           # 数据质量分级
└── crawl_blogger.py         # 调用示例（完整3轮采集流水线）
```

### 预期收益

| 指标 | 效果 |
|------|------|
| API调用成功率 | 99%+（多端点降级） |
| 端点切换延迟 | <2s（自动降级） |
| Token节省 | 重试次数-70%（路由器内重试而非调用方重试） |
| 代码复用 | 任意REST API接入时间从天级→时级 |