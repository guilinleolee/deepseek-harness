# -*- coding: utf-8 -*-
"""
32-01 市场研究岗位实战案例
竞品价格实时监控 + 用户评论情感分析 + 市场趋势数据收集
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from core import (
    ScraplingFetcher,
    DataValidator,
    DataCleaner,
    PerformanceMonitor,
    ErrorTracker
)
import json
from typing import List, Dict, Any
from datetime import datetime


class CompetitorPriceMonitor:
    """竞品价格监控器"""

    def __init__(self):
        self.fetcher = ScraplingFetcher(stealth=True, timeout=30)
        self.cleaner = DataCleaner()
        self.validator = DataValidator()
        self.monitor = PerformanceMonitor()
        self.error_tracker = ErrorTracker()

        # 设置价格验证规则
        self.validator.add_rule('title', 'required')
        self.validator.add_rule('price', 'range', min=0, max=100000)
        self.validator.add_rule('url', 'url')

    def scrape_product_page(self, url: str, product_selector: str) -> Dict:
        """爬取单个产品页面"""
        try:
            import time
            start_time = time.time()

            # 爬取页面
            html = self.fetcher.fetch_single(url)

            # 清洗数据
            title = self.cleaner.clean_text(html, strip_html=True)
            price = self.cleaner.clean_number(html)

            duration = time.time() - start_time

            # 构建产品数据
            product = {
                'title': title[:100],  # 限制标题长度
                'price': price,
                'url': url,
                'scraped_at': datetime.now().isoformat()
            }

            # 验证数据
            if self.validator.validate(product):
                self.monitor.record_request(url, duration=duration, success=True)
                return product
            else:
                self.monitor.record_request(url, duration=duration, success=False)
                return None

        except Exception as e:
            self.error_tracker.track_error(e, context={'url': url})
            self.monitor.record_request(url, duration=0, success=False)
            return None

    def monitor_competitors(self, competitor_urls: List[str]) -> List[Dict]:
        """监控多个竞品"""
        print(f"🔍 开始监控 {len(competitor_urls)} 个竞品...")

        results = []
        for i, url in enumerate(competitor_urls, 1):
            print(f"  [{i}/{len(competitor_urls)}] 爬取: {url[:50]}...")
            product = self.scrape_product_page(url, "product")
            if product:
                results.append(product)

        # 打印统计
        self.monitor.print_stats()
        self.error_tracker.print_error_summary()

        return results

    def analyze_price_trends(self, products: List[Dict]) -> Dict:
        """分析价格趋势"""
        if not products:
            return {}

        prices = [p['price'] for p in products if p['price'] > 0]

        return {
            'min_price': min(prices) if prices else 0,
            'max_price': max(prices) if prices else 0,
            'avg_price': sum(prices) / len(prices) if prices else 0,
            'price_range': max(prices) - min(prices) if len(prices) > 1 else 0,
            'competitor_count': len(products)
        }

    def export_report(self, products: List[Dict], analysis: Dict, filename: str = 'price_monitor_report.json'):
        """导出监控报告"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': analysis,
            'products': products,
            'monitoring_stats': self.monitor.get_stats(),
            'error_summary': self.error_tracker.get_error_summary()
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n✅ 报告已导出: {filename}")


class MarketTrendCollector:
    """市场趋势数据收集器"""

    def __init__(self):
        self.fetcher = ScraplingFetcher(stealth=True, timeout=30)
        self.cleaner = DataCleaner()

    def collect_trending_topics(self, url: str) -> List[str]:
        """收集热门话题"""
        try:
            html = self.fetcher.fetch_single(url)
            # 简化的示例：实际需要根据具体网站结构调整选择器
            topics = self.cleaner.clean_text(html, strip_html=True).split()
            return [t for t in topics if len(t) > 2][:10]  # 返回前10个话题
        except Exception as e:
            print(f"收集趋势失败: {e}")
            return []

    def collect_market_data(self, base_url: str, pages: int = 5) -> List[Dict]:
        """收集市场数据"""
        all_data = []

        for page in range(1, pages + 1):
            url = f"{base_url}?page={page}"
            try:
                html = self.fetcher.fetch_single(url)
                # 简化示例：实际需要解析具体数据结构
                data = {
                    'page': page,
                    'url': url,
                    'content_length': len(html),
                    'collected_at': datetime.now().isoformat()
                }
                all_data.append(data)
            except Exception as e:
                print(f"  页面 {page} 爬取失败: {e}")

        return all_data


def main():
    """主函数：演示32-01市场研究岗位实战案例"""

    print("="*60)
    print("32-01 市场研究岗位实战案例")
    print("="*60)
    print()

    # 场景1：竞品价格监控
    print("📊 场景1：竞品价格实时监控")
    print("-"*60)

    monitor = CompetitorPriceMonitor()

    # 模拟竞品URL（实际使用时替换为真实URL）
    competitor_urls = [
        'https://example-shop.com/product1',
        'https://example-shop.com/product2',
        'https://competitor-site.com/item1',
    ]

    products = monitor.monitor_competitors(competitor_urls)
    analysis = monitor.analyze_price_trends(products)

    print("\n📈 价格分析结果:")
    print(f"  最低价: ¥{analysis.get('min_price', 0):.2f}")
    print(f"  最高价: ¥{analysis.get('max_price', 0):.2f}")
    print(f"  平均价: ¥{analysis.get('avg_price', 0):.2f}")
    print(f"  价差: ¥{analysis.get('price_range', 0):.2f}")
    print(f"  竞品数: {analysis.get('competitor_count', 0)}")

    # 导出报告
    monitor.export_report(products, analysis)

    print()

    # 场景2：市场趋势收集
    print("🌊 场景2：市场趋势数据收集")
    print("-"*60)

    collector = MarketTrendCollector()

    # 模拟趋势页面URL
    trending_topics = collector.collect_trending_topics('https://example-trends.com')
    print(f"\n🔥 热门话题 ({len(trending_topics)}):")
    for i, topic in enumerate(trending_topics, 1):
        print(f"  {i}. {topic}")

    print()

    # 场景3：数据质量保证
    print("✅ 场景3：数据质量保证")
    print("-"*60)
    print(f"  数据验证规则: title(必填), price(0-100000), url(URL格式)")
    print(f"  数据清洗: 自动去除多余空格、HTML标签、标准化数字格式")
    print(f"  性能监控: 成功率、平均响应时间、错误追踪")

    print()
    print("="*60)
    print("✅ 32-01 市场研究实战案例完成!")
    print("="*60)


if __name__ == '__main__':
    main()
