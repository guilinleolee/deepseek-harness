#!/usr/bin/env python3
"""
Firecrawl Crawl Client - 全站爬取
异步大规模网站爬取
"""

import argparse
import json
import os
import sys
import time
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

def start_crawl(url: str, limit: int = 50, formats=None, api_key: str = None):
    """启动全站爬取"""
    if formats is None:
        formats = ['markdown']

    try:
        from firecrawl import Firecrawl
        key = api_key or load_api_key()
        if not key:
            raise ValueError("FIRECRAWL_API_KEY not set")

        app = Firecrawl(api_key=key)
        job_id = app.start_crawl(url, limit=limit, formats=formats)
        return job_id, app
    except ImportError:
        print("❌ firecrawl-py 未安装")
        print("   请运行: pip install firecrawl-py")
        sys.exit(1)

def get_crawl_status(job_id: str, app=None, api_key: str = None):
    """获取爬取状态"""
    try:
        if app is None:
            from firecrawl import Firecrawl
            key = api_key or load_api_key()
            app = Firecrawl(api_key=key)
        return app.get_crawl_status(job_id)
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def main():
    parser = argparse.ArgumentParser(description='🔥 Firecrawl Crawl - 全站爬取')
    parser.add_argument('url', nargs='?', help='目标网站URL')
    parser.add_argument('--limit', type=int, default=50, help='爬取页面数量限制')
    parser.add_argument('--format', '-f', default='markdown', help='输出格式')
    parser.add_argument('--api-key', help='Firecrawl API Key (可选)')
    parser.add_argument('--output', '-o', help='输出目录')
    parser.add_argument('--status', help='查询任务状态 (job_id)')
    parser.add_argument('--wait', action='store_true', help='等待任务完成')
    parser.add_argument('--poll-interval', type=int, default=5, help='轮询间隔(秒)')
    args = parser.parse_args()

    # 查询状态模式
    if args.status:
        print(f"📋 查询任务状态: {args.status}")
        status = get_crawl_status(args.status, api_key=args.api_key)

        if status:
            print(f"\n状态: {status.get('status', 'unknown')}")

            if status.get('status') == 'completed' and 'data' in status:
                pages = status['data']
                print(f"完成页面数: {len(pages)}")

                # 保存结果
                output_file = args.output or f"crawl_{args.status}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump({'job_id': args.status, 'pages': pages}, f, indent=2, ensure_ascii=False)
                print(f"💾 结果已保存: {output_file}")

                # 显示摘要
                print("\n📄 页面摘要:")
                for i, page in enumerate(pages[:5], 1):
                    meta = page.get('metadata', {})
                    title = meta.get('title', 'N/A')[:50]
                    url = page.get('url', 'N/A')[:60]
                    print(f"   {i}. [{title}]")
                    print(f"      {url}")

            elif status.get('status') == 'failed':
                print(f"❌ 爬取失败: {status.get('error', 'Unknown error')}")
            else:
                print(f"进度: {status.get('current', 0)} / {status.get('total', '?')}")
        else:
            print("❌ 无法获取任务状态")
        return

    # 启动爬取模式
    if not args.url:
        parser.print_help()
        print("\n💡 示例:")
        print("   启动爬取: crawl_client.py https://example.com --limit 100")
        print("   查询状态: crawl_client.py --status JOB_ID")
        sys.exit(1)

    print(f"🌐 正在启动全站爬取: {args.url}")
    print(f"   限制: {args.limit} 页")
    print(f"   格式: {args.format}")

    job_id, app = start_crawl(args.url, args.limit, [args.format], args.api_key)
    print(f"\n📋 任务ID: {job_id}")
    print(f"   查询命令: python {__file__} --status {job_id}")
    print(f"   等待完成: python {__file__} --status {job_id} --wait")
    print()

    if args.wait:
        print("⏳ 等待爬取完成...")
        while True:
            status = get_crawl_status(job_id, app)
            status_str = status.get('status', 'unknown')
            current = status.get('current', 0)
            total = status.get('total', '?')

            print(f"\r   状态: {status_str} | 进度: {current}/{total}", end='', flush=True)

            if status_str == 'completed':
                print()  # 换行
                pages = status.get('data', [])
                print(f"\n✅ 爬取完成! 共 {len(pages)} 页")

                # 保存结果
                output_dir = Path(args.output) if args.output else Path(f"crawl_{job_id}")
                output_dir.mkdir(exist_ok=True)
                output_file = output_dir / "pages.json"

                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'job_id': job_id,
                        'url': args.url,
                        'page_count': len(pages),
                        'pages': pages
                    }, f, indent=2, ensure_ascii=False)
                print(f"💾 结果已保存: {output_file}")

                # 保存每个页面
                for i, page in enumerate(pages):
                    url = page.get('url', f'page_{i}')
                    filename = output_dir / f"page_{i}_{hash(url)}.md"
                    content = page.get('markdown', page.get('html', ''))
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                print(f"💾 页面文件已保存: {output_dir}/")

                break

            elif status_str == 'failed':
                print()
                print(f"❌ 爬取失败: {status.get('error', 'Unknown error')}")
                break

            time.sleep(args.poll_interval)

if __name__ == '__main__':
    main()
