---
license: UNKNOWN
name: python-patterns
description: Pythonic idioms, PEP 8 standards, type hints, and best practices for building robust, efficient, and maintainable Python applications.
github_repo: affaan-m/everything-claude-code
github_hash: 4e66b2882da9afb9747468b08a253ca2f09c85f3
last_updated: 2026-04-25
source_type: derived
origin: ECC (everything-claude-code)
triggers: ["python patterns", "Python Development Patterns — Python开发模式"]
---

# Python Development Patterns — Python开发模式

> 来源: [affaan-m/everything-claude-code/skills/python-patterns](https://github.com/affaan-m/everything-claude-code)

## 功能概述

惯用Python模式与最佳实践，构建健壮、高效、可维护的Python应用程序。

## 何时使用

- 编写新Python代码
- 审查Python代码
- 重构现有Python代码
- 设计Python包/模块

## 核心原则

### 1. 可读性优先

Python优先考虑可读性。代码应该明显且易于理解。

```python
# ✅ Good: 清晰可读
def get_active_users(users: list[User]) -> list[User]:
    """Return only active users from the provided list."""
    return [user for user in users if user.is_active]

# ❌ Bad: 耍小聪明但令人困惑
def get_active_users(u):
    return [x for x in u if x.a]
```

### 2. 显式优于隐式

避免魔法；要清楚你的代码在做什么。

```python
# ✅ Good: 显式配置
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 3. EAFP - 求原谅而非求许可

Python偏好异常处理而非条件检查。

```python
# ✅ Good: EAFP风格
def get_value(dictionary: dict, key: str) -> Any:
    try:
        return dictionary[key]
    except KeyError:
        return default_value

# ❌ Bad: LBYL (先看后跳)风格
def get_value(dictionary: dict, key: str) -> Any:
    if key in dictionary:
        return dictionary[key]
    else:
        return default_value
```

## 类型提示

### 现代类型提示 (Python 3.9+)

```python
# Python 3.9+ - 使用内置类型
def process_items(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}
```

### TypeVar和Protocol

```python
from typing import Protocol

class Renderable(Protocol):
    def render(self) -> str:
        """Render the object to a string."""

def render_all(items: list[Renderable]) -> str:
    """Render all items that implement the Renderable protocol."""
    return "\n".join(item.render() for item in items)
```

## 错误处理模式

### 特定异常处理

```python
# ✅ Good: 捕获特定异常
def load_config(path: str) -> Config:
    try:
        with open(path) as f:
            return Config.from_json(f.read())
    except FileNotFoundError as e:
        raise ConfigError(f"Config file not found: {path}") from e
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in config: {path}") from e

# ❌ Bad: 空except
def load_config(path: str) -> Config:
    try:
        with open(path) as f:
            return Config.from_json(f.read())
    except:
        return None  # 静默失败!
```

### 自定义异常层次

```python
class AppError(Exception):
    """所有应用异常的基类。"""
    pass

class ValidationError(AppError):
    """输入验证失败时抛出。"""
    pass

class NotFoundError(AppError):
    """请求的资源未找到时抛出。"""
    pass
```

## 上下文管理器

### 资源管理

```python
# ✅ Good: 使用上下文管理器
def process_file(path: str) -> str:
    with open(path, 'r') as f:
        return f.read()
```

### 自定义上下文管理器

```python
from contextlib import contextmanager

@contextmanager
def timer(name: str):
    """计时代码块的上下文管理器。"""
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"{name} took {elapsed:.4f} seconds")

# 使用
with timer("data processing"):
    process_large_dataset()
```

## 推导式与生成器

### 生成器表达式

```python
# ✅ Good: 生成器惰性求值
total = sum(x * x for x in range(1_000_000))

# ❌ Bad: 创建大型中间列表
total = sum([x * x for x in range(1_000_000)])
```

### 生成器函数

```python
def read_large_file(path: str) -> Iterator[str]:
    """逐行读取大文件。"""
    with open(path) as f:
        for line in f:
            yield line.strip()
```

## 数据类

### 数据类与验证

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    """带自动__init__, __repr__, __eq__的用户实体。"""
    id: str
    name: str
    email: str
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

    def __post_init__(self):
        if "@" not in self.email:
            raise ValueError(f"Invalid email: {self.email}")
```

## 装饰器

### 函数装饰器

```python
import functools
import time

def timer(func: Callable) -> Callable:
    """计时函数执行的装饰器。"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
```

## 并发模式

### I/O密集型: Threading

```python
import concurrent.futures

def fetch_all_urls(urls: list[str]) -> dict[str, str]:
    """使用线程并发获取多个URL。"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(fetch_url, url): url for url in urls}
        results = {}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                results[url] = future.result()
            except Exception as e:
                results[url] = f"Error: {e}"
    return results
```

### CPU密集型: Multiprocessing

```python
def process_data(data: list[int]) -> int:
    """CPU密集型计算。"""
    return sum(x ** 2 for x in data)

def process_all(datasets: list[list[int]]) -> list[int]:
    """使用多进程处理多个数据集。"""
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(executor.map(process_data, datasets))
    return results
```

### 异步: Async/Await

```python
import asyncio

async def fetch_async(url: str) -> str:
    """异步获取URL。"""
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def fetch_all(urls: list[str]) -> dict[str, str]:
    """并发获取多个URL。"""
    tasks = [fetch_async(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return dict(zip(urls, results))
```

## 包组织

### 标准项目布局

```
myproject/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       ├── main.py
│       ├── api/
│       ├── models/
│       └── utils/
├── tests/
├── pyproject.toml
└── .gitignore
```

## 内存与性能

### 使用__slots__节省内存

```python
# ✅ Good: __slots__减少内存使用
class Point:
    __slots__ = ['x', 'y']

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
```

## Python工具链集成

### 必需命令

```bash
# 代码格式化
black .
isort .

# 代码检查
ruff check .
pylint mypackage/

# 类型检查
mypy .

# 测试
pytest --cov=mypackage --cov-report=html

# 安全扫描
bandit -r .
pip-audit
```

## 惯用语速查

| 惯用语 | 说明 |
|--------|------|
| EAFP | 求原谅而非求许可 |
| 上下文管理器 | 用`with`管理资源 |
| 列表推导 | 简单转换用推导式 |
| 生成器 | 惰性求值和大数据集 |
| 类型提示 | 注解函数签名 |
| 数据类 | 自动生成方法的数据容器 |

## 天龙引擎集成

### 适用岗位

| 岗位 | 集成方式 | 增强能力 |
|------|---------|---------|
| **03构建师** | Python实现 | 惯用模式 + 类型提示 + 异步 |
| **04验证师** | Python测试 | pytest + 异步测试 |
| **10-03算法工程师** | 数据处理Python | 向量化 + 性能优化 |

### 天龙引擎增强

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎 Python开发体系                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Python开发流程:                                           │
│   ├── 03构建师 → 类型提示 + 数据类 + 异步                   │
│   ├── 04验证师 → pytest + 覆盖率                           │
│   └── 算法工程师 → numpy/pandas向量化                     │
│                                                             │
│   协同技能:                                                 │
│   ├── /database-migrations → Django迁移                   │
│   ├── /scrapy-spider-developer → Scrapy爬虫                │
│   └── /enterprise-docs-search → RAG数据管道               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 核心命令

```bash
# Python开发
[@构建师] 使用python-patterns实现这个数据处理模块
[@构建师] 添加异步HTTP请求

# 测试
[@验证师] 编写pytest单元测试

# 性能
[@算法工程师] 向量化优化这个数据处理管道
```

---

**版本**: V1.0 | **兼容性**: 天龙引擎 V8.68+ | **来源**: ECC
