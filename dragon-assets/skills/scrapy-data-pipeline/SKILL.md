---
license: UNKNOWN
github_repo: scrapy/scrapy
github_hash: fc4c57e7958dbbc9532a38f3c622dd990c18591e
triggers: ["scrapy data pipeline", "Scrapy Data Pipeline"]
---
# Scrapy Data Pipeline

## 元数据
- **名称**: scrapy-data-pipeline
- **版本**: 1.0.0
- **来源**: [scrapy/scrapy](https://github.com/scrapy/scrapy) - 60.8k ⭐
- **创建日期**: 2026-03-16
- **匹配岗位**: 17-01数据分析师、19-01数据工程师

## 功能描述
Scrapy 数据管道配置与优化，提供数据清洗、验证、去重、存储等完整 ETL 能力，支持多种存储后端。

## 核心能力

| 能力 | 说明 | 使用场景 |
|------|------|---------|
| **数据清洗** | 字段标准化、格式转换 | 脏数据处理 |
| **数据验证** | 字段校验、完整性检查 | 数据质量保证 |
| **数据去重** | URL 去重、内容去重 | 避免重复数据 |
| **多存储后端** | SQLite/MySQL/MongoDB/Redis | 持久化存储 |
| **增量采集** | 状态追踪、增量更新 | 定期更新数据 |
| **数据导出** | JSON/CSV/XML/Excel | 数据交换 |

## Pipeline 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Scrapy 数据管道架构                        │
├─────────────────────────────────────────────────────────────┤
│  Spider yield Item                                          │
│       ↓                                                     │
│  [100] ValidationPipeline ← 数据验证                        │
│       ↓                                                     │
│  [200] DeduplicationPipeline ← 数据去重                     │
│       ↓                                                     │
│  [300] CleaningPipeline ← 数据清洗                          │
│       ↓                                                     │
│  [400] EnrichmentPipeline ← 数据增强                        │
│       ↓                                                     │
│  [500] StoragePipeline ← 数据存储                           │
│       ↓                                                     │
│  Database/File                                              │
└─────────────────────────────────────────────────────────────┘
```

## Pipeline 实现模板

### 1. 验证 Pipeline
```python
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

class ValidationPipeline:
    """数据验证管道 - 优先级 100"""

    REQUIRED_FIELDS = ['url', 'title']

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # 检查必填字段
        for field in self.REQUIRED_FIELDS:
            if not adapter.get(field):
                raise DropItem(f"Missing required field: {field}")

        # URL 格式验证
        url = adapter.get('url', '')
        if not url.startswith(('http://', 'https://')):
            raise DropItem(f"Invalid URL format: {url}")

        return item
```

### 2. 去重 Pipeline
```python
import hashlib
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

class DeduplicationPipeline:
    """数据去重管道 - 优先级 200"""

    def __init__(self):
        self.seen_hashes = set()

    def _generate_hash(self, item: dict) -> str:
        """生成内容哈希"""
        content = str(sorted(item.items()))
        return hashlib.md5(content.encode()).hexdigest()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        item_hash = self._generate_hash(dict(adapter))

        if item_hash in self.seen_hashes:
            raise DropItem(f"Duplicate item: {adapter.get('url')}")

        self.seen_hashes.add(item_hash)
        return item
```

### 3. 清洗 Pipeline
```python
import re
from datetime import datetime
from itemadapter import ItemAdapter

class CleaningPipeline:
    """数据清洗管道 - 优先级 300"""

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # 字符串清理
        self._clean_strings(adapter)

        # 价格清理
        if 'price' in adapter:
            adapter['price'] = self._clean_price(adapter['price'])

        # 日期清理
        if 'date' in adapter:
            adapter['date'] = self._clean_date(adapter['date'])

        # 添加采集时间
        adapter['scraped_at'] = datetime.now().isoformat()

        return item

    def _clean_strings(self, adapter):
        """清理字符串字段"""
        for key, value in adapter.items():
            if isinstance(value, str):
                # 移除多余空白
                adapter[key] = ' '.join(value.split())

    def _clean_price(self, price_str: str) -> float:
        """清理价格"""
        if isinstance(price_str, (int, float)):
            return float(price_str)
        cleaned = re.sub(r'[^\d.]', '', str(price_str))
        return float(cleaned) if cleaned else 0.0

    def _clean_date(self, date_str: str) -> str:
        """标准化日期格式"""
        from dateutil import parser
        try:
            dt = parser.parse(date_str)
            return dt.isoformat()
        except:
            return date_str
```

### 4. 数据增强 Pipeline
```python
from itemadapter import ItemAdapter
import tldextract

class EnrichmentPipeline:
    """数据增强管道 - 优先级 400"""

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        url = adapter.get('url', '')
        if url:
            # 提取域名信息
            extracted = tldextract.extract(url)
            adapter['domain'] = extracted.registered_domain
            adapter['subdomain'] = extracted.subdomain
            adapter['tld'] = extracted.suffix

        # 添加 Spider 信息
        adapter['spider_name'] = spider.name

        return item
```

### 5. SQLite 存储 Pipeline
```python
import sqlite3
from itemadapter import ItemAdapter
from contextlib import contextmanager

class SQLitePipeline:
    """SQLite 存储管道 - 优先级 500"""

    def __init__(self, db_path: str, table_name: str = 'items'):
        self.db_path = db_path
        self.table_name = table_name
        self.conn = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db_path=crawler.settings.get('SQLITE_DB', 'scrapy.db'),
            table_name=crawler.settings.get('SQLITE_TABLE', 'items')
        )

    def open_spider(self, spider):
        self.conn = sqlite3.connect(self.db_path)
        self._create_table()

    def close_spider(self, spider):
        if self.conn:
            self.conn.close()

    def _create_table(self):
        self.conn.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                price REAL,
                content TEXT,
                domain TEXT,
                scraped_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        columns = ['url', 'title', 'price', 'content', 'domain', 'scraped_at']
        values = [adapter.get(col) for col in columns]
        placeholders = ','.join(['?' for _ in columns])

        try:
            self.conn.execute(
                f'INSERT OR REPLACE INTO {self.table_name} ({",".join(columns)}) VALUES ({placeholders})',
                values
            )
            self.conn.commit()
        except sqlite3.Error as e:
            spider.logger.error(f'SQLite error: {e}')

        return item
```

### 6. MySQL 存储 Pipeline
```python
import pymysql
from itemadapter import ItemAdapter
from contextlib import contextmanager

class MySQLPipeline:
    """MySQL 存储管道"""

    def __init__(self, host, port, user, password, database, table):
        self.config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database,
            'charset': 'utf8mb4'
        }
        self.table = table
        self.conn = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST', 'localhost'),
            port=crawler.settings.get('MYSQL_PORT', 3306),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            database=crawler.settings.get('MYSQL_DATABASE'),
            table=crawler.settings.get('MYSQL_TABLE', 'items')
        )

    def open_spider(self, spider):
        self.conn = pymysql.connect(**self.config)

    def close_spider(self, spider):
        if self.conn:
            self.conn.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        columns = list(adapter.keys())
        values = [adapter[col] for col in columns]
        placeholders = ','.join(['%s' for _ in columns])

        with self.conn.cursor() as cursor:
            sql = f'''
                INSERT INTO {self.table} ({','.join(columns)})
                VALUES ({placeholders})
                ON DUPLICATE KEY UPDATE
                {','.join([f'{col}=VALUES({col})' for col in columns])}
            '''
            cursor.execute(sql, values)
            self.conn.commit()

        return item
```

### 7. MongoDB 存储 Pipeline
```python
import pymongo
from itemadapter import ItemAdapter

class MongoDBPipeline:
    """MongoDB 存储管道"""

    def __init__(self, uri, database, collection):
        self.uri = uri
        self.database = database
        self.collection = collection
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            uri=crawler.settings.get('MONGODB_URI', 'mongodb://localhost:27017'),
            database=crawler.settings.get('MONGODB_DATABASE', 'scrapy'),
            collection=crawler.settings.get('MONGODB_COLLECTION', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.uri)
        self.db = self.client[self.database]

    def close_spider(self, spider):
        if self.client:
            self.client.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # 使用 url 作为唯一标识
        url = adapter.get('url')
        if url:
            self.db[self.collection].update_one(
                {'url': url},
                {'$set': dict(adapter)},
                upsert=True
            )
        else:
            self.db[self.collection].insert_one(dict(adapter))

        return item
```

### 8. Redis 存储 Pipeline
```python
import redis
import json
from itemadapter import ItemAdapter

class RedisPipeline:
    """Redis 存储/缓存管道"""

    def __init__(self, host, port, db, key_prefix):
        self.config = {'host': host, 'port': port, 'db': db}
        self.key_prefix = key_prefix
        self.redis = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('REDIS_HOST', 'localhost'),
            port=crawler.settings.get('REDIS_PORT', 6379),
            db=crawler.settings.get('REDIS_DB', 0),
            key_prefix=crawler.settings.get('REDIS_PREFIX', 'scrapy:')
        )

    def open_spider(self, spider):
        self.redis = redis.Redis(**self.config)

    def close_spider(self, spider):
        if self.redis:
            self.redis.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # 使用 Hash 存储完整数据
        url = adapter.get('url', '')
        if url:
            key = f"{self.key_prefix}item:{hashlib.md5(url.encode()).hexdigest()}"
            self.redis.hset(key, mapping={
                k: json.dumps(v) if not isinstance(v, str) else v
                for k, v in adapter.items()
            })

        # 也可添加到 List 用于批量处理
        self.redis.rpush(f"{self.key_prefix}queue", json.dumps(dict(adapter)))

        return item
```

## settings.py 配置

```python
# Pipeline 配置
ITEM_PIPELINES = {
    "myproject.pipelines.ValidationPipeline": 100,
    "myproject.pipelines.DeduplicationPipeline": 200,
    "myproject.pipelines.CleaningPipeline": 300,
    "myproject.pipelines.EnrichmentPipeline": 400,
    "myproject.pipelines.SQLitePipeline": 500,
}

# SQLite 配置
SQLITE_DB = "data/scraped.db"
SQLITE_TABLE = "products"

# MySQL 配置
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "scrapy"
MYSQL_PASSWORD = "password"
MYSQL_DATABASE = "scrapy_db"
MYSQL_TABLE = "items"

# MongoDB 配置
MONGODB_URI = "mongodb://localhost:27017"
MONGODB_DATABASE = "scrapy"
MONGODB_COLLECTION = "items"

# Redis 配置
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PREFIX = "scrapy:"
```

## 增量采集方案

```python
from datetime import datetime
from itemadapter import ItemAdapter

class IncrementalPipeline:
    """增量采集管道"""

    def __init__(self, state_file: str):
        self.state_file = state_file
        self.last_run = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            state_file=crawler.settings.get('STATE_FILE', 'state.json')
        )

    def open_spider(self, spider):
        import json
        import os

        if os.path.exists(self.state_file):
            with open(self.state_file) as f:
                state = json.load(f)
                self.last_run = datetime.fromisoformat(state.get('last_run', '1970-01-01'))

    def close_spider(self, spider):
        import json

        state = {'last_run': datetime.now().isoformat()}
        with open(self.state_file, 'w') as f:
            json.dump(state, f)

    def process_item(self, item, spider):
        # 只处理上次运行后的数据
        adapter = ItemAdapter(item)
        item_date = adapter.get('date')

        if item_date and self.last_run:
            try:
                dt = datetime.fromisoformat(item_date)
                if dt < self.last_run:
                    raise DropItem("Item older than last run")
            except:
                pass

        return item
```

## 与天龙引擎协同

```bash
# 自然语言触发
[@数据工程师] 配置 Scrapy 数据管道，数据存入 SQLite
[@数据分析师] 清洗采集的电商数据并导出 CSV

# Skill 调用
/scrapy-data-pipeline add --type cleaning
/scrapy-data-pipeline add --type storage --backend sqlite
/scrapy-data-pipeline export --format csv --output data.csv
```

## 参考资料
- [Item Pipeline 文档](https://docs.scrapy.org/en/latest/topics/item-pipeline.html)
- [Items 文档](https://docs.scrapy.org/en/latest/topics/items.html)

## 更新日志
- **v1.0.0** (2026-03-16): 初始版本，8种 Pipeline 模板