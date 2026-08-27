"""
手动测试脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent

# 设置包名
package_name = "wechat_skills_unified"

# 如果项目根目录不在sys.path，添加它
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root.parent))

# 导入包
import wechat_skills_unified

def test_article_model():
    """测试Article模型"""
    print("Testing Article model...")

    Article = wechat_skills_unified.Article

    article = Article(
        url="https://mp.weixin.qq.com/s/test123",
        url_hash="",
        title="测试文章",
        author="测试作者",
        account_name="测试公众号",
        content_text="这是一篇测试文章" * 100,
        source="test"
    )

    assert article.title == "测试文章"
    assert article.word_count > 0
    assert article.url_hash != ""

    # 测试序列化
    data = article.to_dict()
    assert 'url' in data

    # 测试反序列化
    article2 = Article.from_dict(data)
    assert article2.url == article.url

    print("  [OK] Article model works")


def test_config():
    """测试Config"""
    print("Testing Config...")

    Config = wechat_skills_unified.Config

    config = Config()
    assert config.cache_enabled is True
    assert config.timeout == 30

    # 测试环境变量配置
    import os
    os.environ['WECHAT_TIMEOUT'] = '60'
    config2 = Config.from_env()
    assert config2.timeout == 60

    print("  [OK] Config works")


def test_lru_cache():
    """测试LRU缓存"""
    print("Testing LRUCache...")

    from wechat_skills_unified.core.cache import LRUCache
    Article = wechat_skills_unified.Article

    cache = LRUCache(capacity=3)

    # 添加3个元素
    for i in range(3):
        article = Article(
            url=f"https://test.com/{i}",
            url_hash=f"hash{i}",
            title=f"Article {i}",
            author="Author",
            account_name="Account"
        )
        cache.set(f"hash{i}", article)

    assert cache.size == 3

    # 添加第4个元素，应该驱逐第1个
    article4 = Article(
        url="https://test.com/4",
        url_hash="hash4",
        title="Article 4",
        author="Author",
        account_name="Account"
    )
    cache.set("hash4", article4)

    assert cache.get("hash0") is None
    assert cache.get("hash4") is not None

    print("  [OK] LRUCache works")


def test_http_utils():
    """测试HTTP工具"""
    print("Testing HTTP utils...")

    from wechat_skills_unified.utils.http import validate_url, extract_url_hash

    # 测试URL验证
    assert validate_url("https://mp.weixin.qq.com/s/test123") is True
    assert validate_url("https://example.com") is False

    # 测试哈希提取
    hash1 = extract_url_hash("https://mp.weixin.qq.com/s/test")
    hash2 = extract_url_hash("https://mp.weixin.qq.com/s/test")
    assert hash1 == hash2

    print("  [OK] HTTP utils work")


def test_html_parser():
    """测试HTML解析器"""
    print("Testing HTML parser...")

    from wechat_skills_unified.utils.html import HTMLParser

    parser = HTMLParser()

    # 测试简单HTML
    html = """
    <html>
        <meta property="og:title" content="测试标题" />
        <meta property="og:article:author" content="测试作者" />
        <div id="js_content">
            <p>这是正文内容</p>
        </div>
    </html>
    """

    result = parser.parse(html)
    assert result.get('title') == '测试标题'
    assert result.get('author') == '测试作者'

    print("  [OK] HTML parser works")


if __name__ == "__main__":
    print("=" * 50)
    print("Manual Testing Script")
    print("=" * 50)

    try:
        test_article_model()
        test_config()
        test_lru_cache()
        test_http_utils()
        test_html_parser()

        print("\n" + "=" * 50)
        print("All tests passed!")
        print("=" * 50)

    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
