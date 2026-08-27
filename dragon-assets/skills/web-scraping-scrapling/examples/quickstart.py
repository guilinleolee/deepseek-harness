"""
Web Scraping SKILL - 快速开始示例

这个示例展示了如何使用 Scrapling SKILL 进行基本的网页爬取
"""

import sys
from pathlib import Path

# 添加核心模块路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.fetcher import ScraplingFetcher


def example_1_simple_fetch():
    """示例 1: 简单的网页爬取"""
    print("=" * 60)
    print("示例 1: 简单的网页爬取")
    print("=" * 60)

    fetcher = ScraplingFetcher()

    # 爬取单个页面
    url = "https://example.com"
    print(f"🎯 目标: {url}")

    try:
        result = fetcher.fetch_single(url)
        print(f"✅ 成功爬取，内容长度: {len(result)} 字符")
        print(f"📄 前200个字符:\n{result[:200]}...")
    except Exception as e:
        print(f"❌ 爬取失败: {e}")


def example_2_select_element():
    """示例 2: 使用 CSS 选择器提取特定元素"""
    print("\n" + "=" * 60)
    print("示例 2: 使用 CSS 选择器提取元素")
    print("=" * 60)

    fetcher = ScraplingFetcher()

    url = "https://example.com"
    selector = "h1"  # 提取所有 h1 标签

    print(f"🎯 目标: {url}")
    print(f"🔍 选择器: {selector}")

    try:
        result = fetcher.fetch_single(url, selector=selector)
        print(f"✅ 找到 {len(result)} 个元素:")
        for i, elem in enumerate(result, 1):
            print(f"  {i}. {elem}")
    except Exception as e:
        print(f"❌ 爬取失败: {e}")


def example_3_batch_fetch():
    """示例 3: 批量爬取多个页面"""
    print("\n" + "=" * 60)
    print("示例 3: 批量爬取")
    print("=" * 60)

    fetcher = ScraplingFetcher()

    urls = [
        "https://example.com",
        "https://example.org",
        "https://example.net",
    ]

    print(f"🎯 目标: {len(urls)} 个页面")

    try:
        results = fetcher.fetch_batch(urls, delay=2)

        # 统计结果
        success_count = sum(1 for r in results if r['success'])
        print(f"\n📊 结果统计:")
        print(f"  成功: {success_count}/{len(urls)}")

        # 显示成功的结果
        for result in results:
            if result['success']:
                print(f"  ✅ {result['url']}")

        # 显示失败的结果
        for result in results:
            if not result['success']:
                print(f"  ❌ {result['url']} - {result.get('error', 'Unknown error')}")

        # 打印统计信息
        fetcher.print_stats()

    except Exception as e:
        print(f"❌ 批量爬取失败: {e}")


def example_4_export_results():
    """示例 4: 导出结果到文件"""
    print("\n" + "=" * 60)
    print("示例 4: 导出结果")
    print("=" * 60)

    fetcher = ScraplingFetcher()

    urls = ["https://example.com", "https://example.org"]

    print(f"🎯 爬取并导出 {len(urls)} 个页面")

    try:
        # 爬取数据
        results = fetcher.fetch_batch(urls, delay=1)

        # 导出到不同格式
        output_dir = Path("./output")
        output_dir.mkdir(exist_ok=True)

        # JSON 格式
        fetcher.export_results(
            results,
            output_dir / "results.json",
            format="json"
        )
        print("✅ 已导出到 JSON")

        # CSV 格式
        fetcher.export_results(
            results,
            output_dir / "results.csv",
            format="csv"
        )
        print("✅ 已导出到 CSV")

        # Excel 格式
        fetcher.export_results(
            results,
            output_dir / "results.xlsx",
            format="excel"
        )
        print("✅ 已导出到 Excel")

        print(f"\n📁 输出目录: {output_dir.absolute()}")

    except Exception as e:
        print(f"❌ 导出失败: {e}")


def example_5_market_research():
    """示例 5: 市场研究场景 - 爬取竞品价格"""
    print("\n" + "=" * 60)
    print("示例 5: 市场研究场景")
    print("=" * 60)

    fetcher = ScraplingFetcher()

    # 模拟竞品页面（实际使用时替换为真实URL）
    competitor_urls = [
        "https://example.com/product1",
        "https://example.org/product2",
    ]

    print(f"🏢 竞品分析: {len(competitor_urls)} 个产品")

    try:
        results = fetcher.fetch_batch(competitor_urls, delay=2)

        # 提取价格信息（示例）
        # 实际使用时需要根据页面结构调整选择器
        products = []
        for result in results:
            if result['success']:
                products.append({
                    'url': result['url'],
                    'price': 'N/A',  # 实际从页面提取
                    'title': 'N/A',  # 实际从页面提取
                })

        # 导出为Excel
        if products:
            import pandas as pd
            df = pd.DataFrame(products)
            output_path = Path("./output/competitor_analysis.xlsx")
            output_path.parent.mkdir(exist_ok=True)
            df.to_excel(output_path, index=False)
            print(f"✅ 竞品分析完成: {output_path.absolute()}")

    except Exception as e:
        print(f"❌ 竞品分析失败: {e}")


def main():
    """运行所有示例"""
    print("🕷️ Scrapling SKILL - 快速开始示例")
    print("=" * 60)

    examples = [
        ("简单爬取", example_1_simple_fetch),
        ("CSS选择器", example_2_select_element),
        ("批量爬取", example_3_batch_fetch),
        ("导出结果", example_4_export_results),
        ("市场研究", example_5_market_research),
    ]

    print("\n可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\n选择要运行的示例 (1-5, 或 'all' 运行所有): ", end="")

    try:
        choice = input().strip()

        if choice.lower() == 'all':
            for name, func in examples:
                func()
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            examples[int(choice) - 1][1]()
        else:
            print("❌ 无效选择")
            return

        print("\n✅ 示例运行完成!")

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")


if __name__ == "__main__":
    main()
