---
license: UNKNOWN
github_repo: scrapy/scrapy
github_hash: fc4c57e7958dbbc9532a38f3c622dd990c18591e
last_updated: 2026-04-25
source_type: derived
triggers: ["scrapy spider developer", "Scrapy Spider Developer"]
---
# Scrapy Spider Developer

## 元数据
- **名称**: scrapy-spider-developer
- **版本**: 1.0.0
- **来源**: [scrapy/scrapy](https://github.com/scrapy/scrapy) - 60.8k ⭐
- **创建日期**: 2026-03-16
- **匹配岗位**: 01调研师、03构建师、19-01数据工程师

## 功能描述
Scrapy Spider 开发与优化，提供企业级网络爬虫开发能力，包括 Spider 类开发、选择器、Item 定义、Pipeline 配置、Middleware 编写等。

## 核心能力

| 能力 | 说明 | 使用场景 |
|------|------|---------|
| **Spider 开发** | 自定义 Spider 类，解析响应提取数据 | 网站数据采集 |
| **选择器** | XPath/CSS 选择器提取数据 | 结构化数据提取 |
| **Item 定义** | 定义数据结构，类型验证 | 数据模型设计 |
| **Pipeline** | 数据处理管道配置 | 数据清洗、存储 |
| **Middleware** | 请求/响应中间件 | 反爬虫、代理设置 |
| **Shell 调试** | 交互式调试环境 | 快速验证选择器 |

## 安装与验证

```bash
# 安装
pip install scrapy

# 验证
scrapy version
# Scrapy 2.11.0+

# 创建项目
scrapy startproject demo_project
```

## 命令速查

### 项目管理
```bash
# 创建项目
scrapy startproject <project_name>

# 创建 Spider
scrapy genspider <spider_name> <domain>

# 列出所有 Spider
scrapy list

# 运行 Spider
scrapy crawl <spider_name>

# 检查 Spider
scrapy check
```

### 数据导出
```bash
# 导出 JSON
scrapy crawl <spider> -o items.json

# 导出 JSON Lines
scrapy crawl <spider> -o items.jl

# 导出 CSV
scrapy crawl <spider> -o items.csv

# 导出 XML
scrapy crawl <spider> -o items.xml
```

### 调试工具
```bash
# Scrapy Shell
scrapy shell <url>

# 查看请求
scrapy fetch <url>

# 查看页面结构
scrapy view <url>

# 解析测试
scrapy parse <url> --callback=parse
```

## Spider 模板

### 基础 Spider
```python
import scrapy
from typing import Iterator, Any

class BasicSpider(scrapy.Spider):
    name = "basic"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com"]

    def parse(self, response: scrapy.http.Response) -> Iterator[dict[str, Any]]:
        """解析页面，提取数据"""
        for item in response.css('div.item'):
            yield {
                'title': item.css('h2::text').get(),
                'price': item.css('.price::text').get(),
                'url': response.urljoin(item.css('a::attr(href)').get()),
            }

        # 分页
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
```

### CrawlSpider（爬取整站）
```python
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class WholeSiteSpider(CrawlSpider):
    name = "wholesite"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com"]

    rules = (
        # 匹配所有链接，用 parse_item 解析
        Rule(
            LinkExtractor(allow=r'/products/'),
            callback='parse_item',
            follow=True
        ),
    )

    def parse_item(self, response):
        yield {
            'title': response.css('h1::text').get(),
            'url': response.url,
        }
```

### XMLFeedSpider（解析 XML/ RSS）
```python
from scrapy.spiders import XMLFeedSpider

class RSSSpider(XMLFeedSpider):
    name = "rss"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/feed.xml"]
    iterator = "iternodes"  # 或 'html'
    itertag = "item"

    def parse_node(self, response, node):
        yield {
            'title': node.xpath('title/text()').get(),
            'link': node.xpath('link/text()').get(),
            'pubDate': node.xpath('pubDate/text()').get(),
        }
```

## Item 定义

```python
import scrapy
from itemadapter import ItemAdapter

class ProductItem(scrapy.Item):
    """商品数据模型"""
    name = scrapy.Field()
    price = scrapy.Field()
    stock = scrapy.Field()
    tags = scrapy.Field()
    last_updated = scrapy.SerializerField(serializer=str)

    def __repr__(self) -> str:
        adapter = ItemAdapter(self)
        return f"<Product: {adapter.get('name', 'N/A')}>"
```

## Pipeline 示例

### 数据清洗 Pipeline
```python
from itemadapter import ItemAdapter

class CleaningPipeline:
    """数据清洗管道"""

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # 清理价格
        if price := adapter.get('price'):
            adapter['price'] = self._clean_price(price)

        # 清理标题
        if title := adapter.get('title'):
            adapter['title'] = title.strip()

        return item

    def _clean_price(self, price_str: str) -> float:
        """清理价格字符串"""
        import re
        cleaned = re.sub(r'[^\d.]', '', price_str)
        return float(cleaned) if cleaned else 0.0
```

### 存储 Pipeline
```python
import sqlite3
from itemadapter import ItemAdapter

class SQLitePipeline:
    """SQLite 存储管道"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db_path=crawler.settings.get('SQLITE_DB', 'items.db')
        )

    def open_spider(self, spider):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                url TEXT UNIQUE,
                title TEXT,
                price REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        self.conn.execute(
            'INSERT OR REPLACE INTO items (url, title, price) VALUES (?, ?, ?)',
            (adapter.get('url'), adapter.get('title'), adapter.get('price'))
        )
        self.conn.commit()
        return item
```

## Middleware 示例

### User-Agent 中间件
```python
import random

class RandomUserAgentMiddleware:
    """随机 User-Agent 中间件"""

    def __init__(self, user_agents: list[str]):
        self.user_agents = user_agents

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            user_agents=crawler.settings.getlist('USER_AGENTS')
        )

    def process_request(self, request, spider):
        request.headers['User-Agent'] = random.choice(self.user_agents)
```

### 代理中间件
```python
class ProxyMiddleware:
    """代理中间件"""

    def __init__(self, proxy_list: list[str]):
        self.proxy_list = proxy_list
        self.current = 0

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            proxy_list=crawler.settings.getlist('PROXY_LIST')
        )

    def process_request(self, request, spider):
        if self.proxy_list:
            proxy = self.proxy_list[self.current % len(self.proxy_list)]
            request.meta['proxy'] = proxy
            self.current += 1
```

## settings.py 配置

```python
# Scrapy settings.py

BOT_NAME = "myproject"

SPIDER_MODULES = ["myproject.spiders"]
NEWSPIDER_MODULE = "myproject.spiders"

# 并发设置
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_REQUESTS_PER_IP = 0

# 下载延迟
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = True

# 超时设置
DOWNLOAD_TIMEOUT = 30

# 重试设置
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408]

# 缓存设置
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400
HTTPCACHE_DIR = "httpcache"

# Pipeline
ITEM_PIPELINES = {
    "myproject.pipelines.CleaningPipeline": 300,
    "myproject.pipelines.SQLitePipeline": 400,
}

# 中间件
DOWNLOADER_MIDDLEWARES = {
    "myproject.middlewares.RandomUserAgentMiddleware": 400,
    "myproject.middlewares.ProxyMiddleware": 410,
}
```

## 与天龙引擎协同

### 调用方式

```bash
# 自然语言触发
[@调研师] 使用 Scrapy 采集某电商网站商品数据
[@数据工程师] 开发一个 Scrapy Spider 采集新闻数据

# Skill 调用
/scrapy-spider-developer create --domain example.com --type crawl
/scrapy-spider-developer run --spider products --output json
```

### 与现有 Skill 协同

| 天龙 Skill | 协同方式 |
|-----------|---------|
| **dragon-scraper** | 简单采集用 dragon-scraper，复杂采集用 Scrapy |
| **Agent-Reach** | 公开数据用 Agent-Reach，定制采集用 Scrapy |
| **Chrome CDP** | 动态渲染用 Chrome CDP，静态页面用 Scrapy |
| **ecommerce-monitor** | Scrapy 采集数据，ecommerce-monitor 分析 |

## 最佳实践

### 1. Spider 开发流程
1. `scrapy shell <url>` 测试选择器
2. 创建 Spider 文件
3. 定义 Item 数据结构
4. 实现 parse 方法
5. 配置 Pipeline
6. 测试运行

### 2. 性能优化
```python
# settings.py
CONCURRENT_REQUESTS = 32
DOWNLOAD_DELAY = 0.25
COOKIES_ENABLED = False
DNSCACHE_ENABLED = True
```

### 3. 错误处理
```python
def parse(self, response):
    try:
        data = response.css('::text').get()
    except Exception as e:
        self.logger.error(f"Parse error: {e}")
        yield {'error': str(e), 'url': response.url}
```

## 参考资料
- [Scrapy 官方文档](https://docs.scrapy.org/)
- [Scrapy GitHub](https://github.com/scrapy/scrapy)
- [选择器文档](https://docs.scrapy.org/en/latest/topics/selectors.html)
- [Pipeline 文档](https://docs.scrapy.org/en/latest/topics/item-pipeline.html)

## 更新日志
- **v1.0.0** (2026-03-16): 初始版本，Spider 开发核心功能