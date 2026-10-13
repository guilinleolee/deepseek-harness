---
license: UNKNOWN
triggers: ["wechat skills unified", "微信公众号文章获取 SKILL"]
---
# 微信公众号文章获取 SKILL

> 一个高性能、可靠的微信公众号文章获取工具，三层缓存 + 智能降级

## 快速开始

### 安装依赖

```bash
cd ~/.claude/skills/wechat-skills-unified
pip install -r requirements/minimal.txt
```

### 基本使用

```python
import wechat_skills_unified as ws

# 获取单篇文章
article = ws.fetch_article("https://mp.weixin.qq.com/s/xxxxx")

if article:
    print(f"标题: {article.title}")
    print(f"作者: {article.author}")
    print(f"字数: {article.word_count}")
```

## 核心功能

### 1. 获取文章

```python
# 单篇文章
article = ws.fetch_article(url)

# 不使用缓存
article = ws.fetch_article(url, use_cache=False)

# 批量获取
urls = ["url1", "url2", "url3"]
articles = ws.fetch_batch(urls, concurrent=3)
```

### 2. 数据访问

```python
# 元数据
print(article.title)
print(article.author)
print(article.account_name)
print(article.publish_time)

# 内容
print(article.content_html)       # HTML格式
print(article.content_markdown)   # Markdown格式
print(article.content_text)       # 纯文本

# 媒体
print(article.images)            # 图片列表
print(article.cover_image)       # 封面图

# 元信息
print(article.source)            # 来源: 'cache'/'direct'/'api'
print(article.fetch_time)        # 获取时间
print(article.word_count)        # 字数
```

### 3. 数据导出

```python
# 导出JSON
json_str = article.to_json()
article.save_json("article.json")

# 导出Markdown
article.save_markdown("article.md")
```

### 4. 缓存管理

```python
# 清理所有缓存
ws.clear_cache()

# 清理过期缓存
from datetime import datetime, timedelta
week_ago = datetime.now() - timedelta(days=7)
ws.clear_cache(before_date=week_ago)

# 查看缓存统计
fetcher = ws.get_default_fetcher()
stats = fetcher.get_cache_stats()
print(stats)
```

## 高级配置

### 环境变量

```bash
export WECHAT_CACHE_PATH="./cache/articles.db"
export WECHAT_CACHE_TTL_DAYS=30
export WECHAT_TIMEOUT=30
export WECHAT_API_KEY="your_key"  # 可选，启用API降级
```

### 配置文件

```python
from wechat_skills_unified import Config, fetch_article

# 创建配置
config = Config(
    cache_enabled=True,
    cache_path="./cache/articles.db",
    cache_ttl_days=30,
    timeout=30,
    api_key="optional"  # 可选
)

# 使用配置
article = fetch_article(url, config=config)
```

## 错误处理

```python
from wechat_skills_unified import (
    URLValidationError,
    CaptchaDetectedError,
    AllStrategiesFailedError
)

try:
    article = ws.fetch_article(url)
except URLValidationError:
    print("URL格式错误")
except CaptchaDetectedError:
    print("检测到验证码")
except AllStrategiesFailedError as e:
    print(f"所有策略失败: {e.failures}")
```

## 命令行使用

```bash
# 获取单篇文章
python -m wechat_skills_unified fetch <url>

# 批量获取
python -m wechat_skills_unified batch -f urls.txt

# 清理缓存
python -m wechat_skills_unified cache clear
```

## 性能优化

### 缓存命中率

- **L1内存**: <1ms（最热数据）
- **L2SQLite**: 5-15ms（历史数据）
- **L3网络**: 500-2000ms（冷数据）

### 降级策略

1. **直接访问**: 85%成功率，0成本
2. **API降级**: 65%成功率，低成本（需要API Key）

## 常见问题

### Q: 如何提高可靠性？

A: 配置API Key作为降级方案：

```bash
export WECHAT_API_KEY="your_api_key"
```

### Q: 缓存占用多少空间？

A: 每篇文章约10-50KB，1000篇文章约10-50MB

### Q: 如何清理旧缓存？

A: 使用`clear_cache()`函数：

```python
from datetime import timedelta
ws.clear_cache(before_date=datetime.now() - timedelta(days=30))
```

## 技术架构

```
用户请求
    ↓
缓存层 (L1→L2→L3)
    ↓
降级控制器 (直接访问 → API降级)
    ↓
内容处理 (解析 → 提取 → Markdown)
    ↓
Article模型 + 缓存写入
```

## 依赖说明

- **必需**: `requests>=2.28.0`
- **可选**: `beautifulsoup4>=4.11.0`（HTML解析）
- **可选**: `html2text>=2020.1.16`（Markdown转换）

## 版本

当前版本: v1.0.0

## 许可证

MIT License

---

**作者**: 03构建师
**日期**: 2026-02-26
