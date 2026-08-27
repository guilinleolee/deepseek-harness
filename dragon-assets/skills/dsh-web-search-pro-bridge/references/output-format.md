# 输出格式规范 · dsh-web-search-pro V0.1.8

> **目的**：天龙侧 LLM 在展示 `dsh-web-search-pro` 工具输出时，应按本规范的 3 种 markdown 模板之一呈现，避免把 raw JSON dump / API 调试日志直接抛给用户。
> **来源**：上游 README § 配置 + § 工具调用样例。

---

## 三种 markdown 模板（按工具）

### 模板 A · web_search_pro 输出（搜索列表）

```markdown
## 🔍 搜索：<query>

**引擎**：`ddg`（fallback: bing → exa） · **结果数**：8 · **耗时**：1.2s · **缓存命中**：✅

### 来源

1. **<title 1>** — <domain1.com>
   <summary line 1>
   <summary line 2>
   🔗 <url1>

2. **<title 2>** — <domain2.com>
   ...
```

**DO**：
- 每条来源带标题 + 域名 + 1-2 行摘要 + URL
- 注明用了哪个引擎 + 是否命中缓存
- 跨引擎结果按 RRF 融合分排序

**DON'T**：
- 不要直接 dump JSON 数组
- 不要暴露 `__cred` / `__cookie` 等内部字段

---

### 模板 B · web_fetch_pro 输出（单页正文）

```markdown
## 📄 抓取：<url>

**来源**：<url> · **模式**：jina → http → playwright · **抓取耗时**：850ms · **字数**：12,450

### 正文（≤ 5,000 字）

> <正文 markdown 化>
> 
> （中间省略 5,000 字，已落快照 ID <snapshot-id>，需要全文跑 `web_snapshot`）

### 元数据

- **标题**：<page title>
- **作者 / 发布日期**：<author> / <published at>
- **语言**：<zh-CN | en | ...>
```

**DO**：
- 默认截断到 5,000 字，提示用户跑 `web_snapshot` 看完整
- 标注抓取模式 + 耗时 + 字数
- 元数据只列核心 3 项（标题/作者/日期 + 语言）

**DON'T**：
- 不要展示 HTTP headers / cookies / 重定向链
- 不要把整个 HTML 转储（即使 markdown 化）

---

### 模板 C · web_platform_search 输出（平台结果）

```markdown
## 📱 <platform> 搜索：<query>

**平台**：<platform> · **账号态**：✅ / ❌ · **结果数**：<N>

### 帖子

1. **<title>** — @<author>
   <1 行摘要>
   ❤️ <likes> · 💬 <comments> · 🔁 <shares>
   🔗 <url>

2. **<title>** — @<author>
   ...
```

**DO**：
- 平台字段头部说明账号态
- 每条带作者 + 互动数据（likes/comments/shares）
- 如果平台不返回互动数据，省略该行

**DON'T**：
- 不要展示 cookie / auth token
- 不要展示平台原始 JSON（`items[].raw`）

---

## 元信息 DO/DON'T 速查

| 维度 | DO | DON'T |
|------|-----|-------|
| 时间 | ISO 8601 → "2 小时前" / "3 天前" | 暴露 epoch 时间戳 |
| URL | 展示完整 https URL | 暴露 tracking 参数（utm_*/fbclid）|
| 标题 | 截断 ≤ 80 字 + "..." | 完整复制 SEO keyword stuffing |
| 摘要 | 1-2 行 human-readable | 复制 description meta 完整值 |
| 引擎 | "ddg / bing / exa（按 RRF 融合）" | "engine: ddg, bing, exa, seam, jina" 全列 |
| 缓存命中 | "✅ 命中" / "❌ 重算" | "cache_key: search:abc123..." |
| 平台账号态 | "✅ 已登录" / "❌ 需 save-login" | 暴露 storageState 路径 |
| 错误 | "❌ 限流，已切 bing" / "❌ 需登录，跑 save-login.mjs" | 完整堆栈 + API 响应 |

---

## 时间转人话规则（4 边界 case）

```python
def iso_to_human(iso_str: str) -> str:
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    t = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
    delta = now - t
    if delta.total_seconds() < 60:
        return "刚刚"
    if delta.total_seconds() < 3600:
        return f"{int(delta.total_seconds() // 60)} 分钟前"
    if delta.total_seconds() < 86400:
        return f"{int(delta.total_seconds() // 3600)} 小时前"
    if delta.days < 30:
        return f"{delta.days} 天前"
    if delta.days < 365:
        return f"{delta.days // 30} 个月前"
    return f"{delta.days // 365} 年前"
```

**边界 case**：

| 输入 | 输出 |
|------|------|
| `2026-08-24T09:30:00Z`（now=10:00）| "30 分钟前" |
| `2026-08-24T01:00:00Z`（now=10:00 同日）| "9 小时前" |
| `2026-08-20T10:00:00Z`（4 天前）| "4 天前" |
| `2026-01-01T00:00:00Z`（236 天前）| "7 个月前" |
| `2024-08-24T00:00:00Z`（2 年前）| "2 年前" |

---

## 错误展示规范

```markdown
## ❌ 搜索失败：<query>

**原因**：<用户可读描述>
**建议**：<下一步动作>

**调试信息**（仅当用户主动要求时展开）

<details>
<raw API response>
</details>
```

**DO**：
- 默认只展示用户可读原因 + 建议
- 调试信息用 `<details>` 折叠

**DON'T**：
- 不要把整个 stack trace 暴露在主区域
- 不要让用户在主区域看到"ECONNREFUSED"等技术细节（除非开发者模式）

---

## title / title_en 规则（双语场景）

当 `web_platform_search` 返回的标题是英文/中文时：

| 场景 | 展示方式 |
|------|---------|
| 标题是英文 + 用户说中文 | "**Title**（<机器翻译中文>）" |
| 标题是中文 + 用户说英文 | "**标题**（<machine translated English>）" |
| 标题是英文 + 用户说英文 | "**Title**" |
| 标题是中文 + 用户说中文 | "**标题**" |

不要双行重复展示（浪费 token）。

---

## 上游参考

- 上游 README § 工具样例：https://github.com/anweat/dsh-web-search-pro#工具11-个
- 天龙 aihot V1.0 references/output-format.md（参照范式）
- 天龙 anysearch references/output-format.md（参照范式）
