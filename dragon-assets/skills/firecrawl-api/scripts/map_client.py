#!/usr/bin/env python3
"""
Firecrawl Map Client - URL发现
将网站转换为URL列表，支持智能sitemap生成
"""

import argparse
import json
import os
import sys
from pathlib import Path

def load_api_key():
    """加载API Key"""
    api_key = os.environ.get('FIRECRAWL_API_KEY')
    if not api_key:
        config_path = Path.home() / ".claude" / "firecrawl_config.json"
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                api_key = config.get('api_key')
    return api_key

def map_url(url: str, limit: int = 100, api_key: str = None):
    """发现网站URL"""
    try:
        from firecrawl import Firecrawl
        key = api_key or load_api_key()
        if not key:
            raise ValueError("FIRECRAWL_API_KEY not set")

        app = Firecrawl(api_key=key)
        result = app.map(url, limit=limit)
        return result
    except ImportError:
        print("❌ firecrawl-py 未安装")
        print("   请运行: pip install firecrawl-py")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='🔥 Firecrawl Map - URL发现')
    parser.add_argument('url', help='目标网站URL')
    parser.add_argument('--limit', type=int, default=100, help='发现的URL数量限制')
    parser.add_argument('--api-key', help='Firecrawl API Key (可选，从环境变量读取)')
    parser.add_argument('--output', '-o', help='输出JSON文件')
    parser.add_argument('--format', choices=['list', 'json'], default='list', help='输出格式')
    args = parser.parse_args()

    print(f"🔍 正在发现 {args.url} 的URL...")
    print(f"   限制: {args.limit} URLs")

    result = map_url(args.url, args.limit, args.api_key)

    if result and 'urls' in result:
        urls = result['urls']
        print(f"\n✅ 成功发现 {len(urls)} 个URL:\n")

        for i, url in enumerate(urls[:50], 1):
            print(f"  {i:3}. {url}")

        if len(urls) > 50:
            print(f"\n  ... 还有 {len(urls) - 50} 个URL (已截断显示)")

        # 保存结果
        output_file = args.output or f"map_{urlparse(args.url).netloc}.json"
        output_data = {
            'url': args.url,
            'count': len(urls),
            'urls': urls,
            'discovered_at': str(Path(__file__).stat().st_mtime)
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 结果已保存: {output_file}")

        # 分类统计
        url_types = {'html': [], 'static': [], 'api': [], 'other': []}
        for url in urls:
            if '.html' in url:
                url_types['html'].append(url)
            elif '/api/' in url or '/v1/' in url:
                url_types['api'].append(url)
            elif any(ext in url for ext in ['.pdf', '.jpg', '.png', '.css', '.js']):
                url_types['static'].append(url)
            else:
                url_types['other'].append(url)

        print(f"\n📊 URL类型统计:")
        print(f"   页面: {len(url_types['html'])}")
        print(f"   API:  {len(url_types['api'])}")
        print(f"   静态: {len(url_types['static'])}")
        print(f"   其他: {len(url_types['other'])}")

    else:
        print(f"❌ URL发现失败")
        print(f"   响应: {result}")

def urlparse(url):
    """简单的URL解析"""
    import re
    match = re.match(r'https?://([^/]+)', url)
    return type('obj', (object,), {'netloc': match.group(1) if match else url})()

if __name__ == '__main__':
    main()
