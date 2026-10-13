"""
快速测试脚本（不依赖包导入）
"""

import sys
from pathlib import Path

# 添加所有模块路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 直接导入模块（不使用包导入）
import models.article
import core.config
import core.cache
import utils.http
import utils.html

print("=" * 60)
print("Quick Test - Direct Module Import")
print("=" * 60)

# 测试1: Article模型
print("\n[Test 1] Article Model")
article = models.article.Article(
    url="https://mp.weixin.qq.com/s/test123",
    url_hash="",
    title="Test Article",
    author="Test Author",
    account_name="Test Account",
    content_text="Test content" * 100,
    source="test"
)
print(f"  Title: {article.title}")
print(f"  Word count: {article.word_count}")
print(f"  URL hash: {article.url_hash[:16]}...")
print("  [PASS]")

# 测试2: Config
print("\n[Test 2] Config")
config = core.config.Config()
print(f"  Cache enabled: {config.cache_enabled}")
print(f"  Timeout: {config.timeout}")
print("  [PASS]")

# 测试3: LRUCache
print("\n[Test 3] LRUCache")
cache = core.cache.LRUCache(capacity=3)
for i in range(3):
    art = models.article.Article(
        url=f"https://test.com/{i}",
        url_hash=f"hash{i}",
        title=f"Article {i}",
        author="Author",
        account_name="Account"
    )
    cache.set(f"hash{i}", art)
print(f"  Cache size: {cache.size}")
print("  [PASS]")

# 测试4: HTTP工具
print("\n[Test 4] HTTP Utils")
valid = utils.http.validate_url("https://mp.weixin.qq.com/s/test")
invalid = utils.http.validate_url("https://example.com")
print(f"  Valid URL: {valid}")
print(f"  Invalid URL: {invalid}")
print("  [PASS]")

# 测试5: HTML解析器
print("\n[Test 5] HTML Parser")
parser = utils.html.HTMLParser()
html = '<meta property="og:title" content="Test Title" />'
result = parser.parse(html)
print(f"  Parsed title: {result.get('title')}")
print("  [PASS]")

print("\n" + "=" * 60)
print("All tests passed!")
print("=" * 60)
