#!/usr/bin/env python3
"""
Firecrawl Interact Client - 浏览器自动化交互
支持自然语言动作描述和代码执行
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

def init_session(url: str, api_key: str = None):
    """初始化浏览器会话"""
    try:
        from firecrawl import Firecrawl
        key = api_key or load_api_key()
        if not key:
            raise ValueError("FIRECRAWL_API_KEY not set")

        app = Firecrawl(api_key=key)
        result = app.scrape(url)
        scrape_id = result.get('metadata', {}).get('id')
        return app, scrape_id
    except ImportError:
        print("❌ firecrawl-py 未安装")
        print("   请运行: pip install firecrawl-py")
        sys.exit(1)

def interact(session_id: str, app, action: str = None, code: str = None, language: str = 'python', api_key: str = None):
    """执行交互"""
    try:
        if action:
            return app.interact(session_id, prompt=action)
        elif code:
            return app.interact(session_id, code=code, language=language)
        else:
            raise ValueError("必须指定 --action 或 --code")
    except Exception as e:
        return {'error': str(e)}

def main():
    parser = argparse.ArgumentParser(description='🔥 Firecrawl Interact - 浏览器自动化交互')
    parser.add_argument('url', help='目标URL')
    parser.add_argument('--action', '-a', help='自然语言动作描述')
    parser.add_argument('--code', '-c', help='代码执行')
    parser.add_argument('--language', '-l', default='python', help='代码语言')
    parser.add_argument('--session', help='使用现有会话ID (跳过初始化)')
    parser.add_argument('--api-key', help='Firecrawl API Key (可选)')
    parser.add_argument('--output', '-o', help='输出文件')
    args = parser.parse_args()

    if not args.action and not args.code:
        parser.print_help()
        print("\n💡 示例:")
        print("   自然语言: interact_client.py https://example.com -a '点击登录按钮'")
        print("   代码执行: interact_client.py https://example.com -c \"page.click('#submit')\"")
        print("   复用会话: interact_client.py https://example.com --session SESSION_ID -a '填写表单'")
        sys.exit(1)

    # 初始化或复用会话
    if args.session:
        from firecrawl import Firecrawl
        key = args.api_key or load_api_key()
        app = Firecrawl(api_key=key)
        session_id = args.session
        print(f"🔄 复用会话: {session_id}")
    else:
        print(f"🖥️  初始化浏览器会话: {args.url}")
        app, session_id = init_session(args.url, args.api_key)
        print(f"✅ 会话初始化成功: {session_id}")

    # 执行交互
    print()
    if args.action:
        print(f"🎯 执行动作: {args.action}")
        result = interact(session_id, app, action=args.action)
    else:
        print(f"💻 执行代码: {args.code[:50]}...")
        result = interact(session_id, app, code=args.code, language=args.language)

    # 输出结果
    if result:
        print("\n" + "="*60)
        print("执行结果:")
        print("="*60)

        if 'error' in result:
            print(f"❌ 错误: {result['error']}")
        else:
            if isinstance(result, dict):
                for key, value in result.items():
                    print(f"\n📌 {key}:")
                    if isinstance(value, str) and len(value) > 500:
                        print(value[:500] + "...")
                    else:
                        print(value)
            else:
                print(result)

        # 保存会话信息
        output_file = args.output or f"interact_session_{session_id}.json"
        session_info = {
            'session_id': session_id,
            'url': args.url,
            'action': args.action,
            'code': args.code,
            'result': result
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(session_info, f, indent=2, ensure_ascii=False)
        print(f"\n💾 会话信息已保存: {output_file}")
        print(f"   可使用 --session {session_id} 继续交互")
    else:
        print("❌ 交互执行失败")

if __name__ == '__main__':
    main()
