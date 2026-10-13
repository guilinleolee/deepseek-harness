# -*- coding: utf-8 -*-
"""
35-01 数字营销岗位实战案例
广告投放效果监控 + 热门话题抓取 + KOL账号数据收集
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from core import (
    ScraplingFetcher,
    DataCleaner,
    PerformanceMonitor,
    ErrorTracker
)
import json
from typing import List, Dict, Any
from datetime import datetime


class AdPerformanceMonitor:
    """广告投放效果监控器"""

    def __init__(self):
        self.fetcher = ScraplingFetcher(stealth=True, timeout=30)
        self.cleaner = DataCleaner()
        self.monitor = PerformanceMonitor()
        self.error_tracker = ErrorTracker()

    def scrape_ad_metrics(self, ad_url: str) -> Dict:
        """爬取单个广告指标"""
        try:
            import time
            start_time = time.time()

            # 爬取广告数据
            html = self.fetcher.fetch_single(ad_url)

            # 解析广告指标（示例：实际需要根据具体广告平台调整）
            metrics = {
                'impressions': self.cleaner.clean_number(html) or 0,
                'clicks': self.cleaner.clean_number(html) or 0,
                'ctr': 0.0,  # 点击率
                'cost': self.cleaner.clean_number(html) or 0.0,
                'conversions': self.cleaner.clean_number(html) or 0,
                'url': ad_url,
                'scraped_at': datetime.now().isoformat()
            }

            # 计算CTR
            if metrics['impressions'] > 0:
                metrics['ctr'] = (metrics['clicks'] / metrics['impressions']) * 100

            duration = time.time() - start_time
            self.monitor.record_request(ad_url, duration=duration, success=True)

            return metrics

        except Exception as e:
            self.error_tracker.track_error(e, context={'url': ad_url})
            self.monitor.record_request(ad_url, duration=0, success=False)
            return None

    def monitor_ad_campaign(self, ad_urls: List[str]) -> Dict:
        """监控广告活动"""
        print(f"📊 监控 {len(ad_urls)} 个广告...")

        all_metrics = []
        for i, url in enumerate(ad_urls, 1):
            print(f"  [{i}/{len(ad_urls)}] 分析: {url[:50]}...")
            metrics = self.scrape_ad_metrics(url)
            if metrics:
                all_metrics.append(metrics)

        # 汇总数据
        summary = self._calculate_campaign_summary(all_metrics)

        # 打印统计
        self.monitor.print_stats()
        self.error_tracker.print_error_summary()

        return {
            'summary': summary,
            'ads': all_metrics,
            'monitoring_stats': self.monitor.get_stats()
        }

    def _calculate_campaign_summary(self, metrics_list: List[Dict]) -> Dict:
        """计算广告活动汇总数据"""
        if not metrics_list:
            return {}

        total_impressions = sum(m.get('impressions', 0) for m in metrics_list)
        total_clicks = sum(m.get('clicks', 0) for m in metrics_list)
        total_cost = sum(m.get('cost', 0) for m in metrics_list)
        total_conversions = sum(m.get('conversions', 0) for m in metrics_list)

        avg_ctr = sum(m.get('ctr', 0) for m in metrics_list) / len(metrics_list)

        cpc = total_cost / total_clicks if total_clicks > 0 else 0  # 单次点击成本
        cpa = total_cost / total_conversions if total_conversions > 0 else 0  # 单次转化成本

        return {
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'total_conversions': total_conversions,
            'total_cost': total_cost,
            'avg_ctr': avg_ctr,
            'cpc': cpc,
            'cpa': cpa,
            'roas': (total_conversions * 100) / total_cost if total_cost > 0 else 0  # 投资回报率（假设每次转化价值100）
        }


class HotTopicTracker:
    """热门话题追踪器"""

    def __init__(self):
        self.fetcher = ScraplingFetcher(stealth=True, timeout=30)
        self.cleaner = DataCleaner()

    def scrape_hot_topics(self, platform_url: str, limit: int = 20) -> List[Dict]:
        """抓取热门话题"""
        try:
            print(f"🔥 抓取热门话题: {platform_url}")
            html = self.fetcher.fetch_single(platform_url)

            # 解析话题（示例：实际需要根据具体平台结构调整）
            topics = []
            content = self.cleaner.clean_text(html, strip_html=True, remove_extra_spaces=True)

            # 简化处理：按行分割并取前N行
            lines = content.split('\n')
            for i, line in enumerate(lines[:limit]):
                line = line.strip()
                if len(line) > 5:  # 过滤太短的内容
                    topics.append({
                        'rank': i + 1,
                        'topic': line[:100],  # 限制长度
                        'engagement': len(line),  # 简化的互动指标
                        'platform': platform_url.split('/')[2],
                        'scraped_at': datetime.now().isoformat()
                    })

            return topics

        except Exception as e:
            print(f"抓取热门话题失败: {e}")
            return []

    def analyze_topic_trends(self, topics: List[Dict]) -> Dict:
        """分析话题趋势"""
        if not topics:
            return {}

        return {
            'total_topics': len(topics),
            'avg_engagement': sum(t['engagement'] for t in topics) / len(topics),
            'top_topic': topics[0]['topic'] if topics else None,
            'platform_distribution': self._group_by_platform(topics)
        }

    def _group_by_platform(self, topics: List[Dict]) -> Dict:
        """按平台分组"""
        platforms = {}
        for topic in topics:
            platform = topic.get('platform', 'unknown')
            if platform not in platforms:
                platforms[platform] = 0
            platforms[platform] += 1
        return platforms


class KOLDataCollector:
    """KOL账号数据收集器"""

    def __init__(self):
        self.fetcher = ScraplingFetcher(stealth=True, timeout=30)
        self.cleaner = DataCleaner()
        self.monitor = PerformanceMonitor()

    def scrape_kol_profile(self, kol_url: str) -> Dict:
        """爬取KOL账号资料"""
        try:
            import time
            start_time = time.time()

            html = self.fetcher.fetch_single(kol_url)

            # 解析KOL数据（示例：实际需要根据具体平台结构调整）
            profile = {
                'username': self.cleaner.clean_text(html)[:50],
                'followers': self.cleaner.clean_number(html) or 0,
                'following': self.cleaner.clean_number(html) or 0,
                'posts': self.cleaner.clean_number(html) or 0,
                'engagement_rate': 0.0,
                'url': kol_url,
                'scraped_at': datetime.now().isoformat()
            }

            # 计算互动率（简化公式）
            if profile['followers'] > 0:
                profile['engagement_rate'] = (profile['posts'] / profile['followers']) * 100

            duration = time.time() - start_time
            self.monitor.record_request(kol_url, duration=duration, success=True)

            return profile

        except Exception as e:
            print(f"KOL数据抓取失败: {e}")
            self.monitor.record_request(kol_url, duration=0, success=False)
            return None

    def collect_kol_data(self, kol_urls: List[str]) -> List[Dict]:
        """批量收集KOL数据"""
        print(f"👥 收集 {len(kol_urls)} 个KOL账号数据...")

        profiles = []
        for i, url in enumerate(kol_urls, 1):
            print(f"  [{i}/{len(kol_urls)}] 抓取: {url[:50]}...")
            profile = self.scrape_kol_profile(url)
            if profile:
                profiles.append(profile)

        self.monitor.print_stats()

        return profiles

    def rank_kols(self, profiles: List[Dict]) -> List[Dict]:
        """KOL排名"""
        # 按粉丝数排序
        sorted_profiles = sorted(profiles, key=lambda x: x.get('followers', 0), reverse=True)

        # 添加排名
        for i, profile in enumerate(sorted_profiles, 1):
            profile['rank'] = i

        return sorted_profiles


def main():
    """主函数：演示35-01数字营销岗位实战案例"""

    print("="*60)
    print("35-01 数字营销岗位实战案例")
    print("="*60)
    print()

    # 场景1：广告投放效果监控
    print("📊 场景1：广告投放效果监控")
    print("-"*60)

    ad_monitor = AdPerformanceMonitor()

    # 模拟广告URL
    ad_urls = [
        'https://ad-platform.com/campaign/ad1',
        'https://ad-platform.com/campaign/ad2',
        'https://ad-platform.com/campaign/ad3',
    ]

    campaign_data = ad_monitor.monitor_ad_campaign(ad_urls)
    summary = campaign_data['summary']

    print("\n📈 广告活动汇总:")
    print(f"  总曝光量: {summary.get('total_impressions', 0):,}")
    print(f"  总点击量: {summary.get('total_clicks', 0):,}")
    print(f"  总转化数: {summary.get('total_conversions', 0):,}")
    print(f"  总花费: ¥{summary.get('total_cost', 0):.2f}")
    print(f"  平均CTR: {summary.get('avg_ctr', 0):.2f}%")
    print(f"  CPC: ¥{summary.get('cpc', 0):.2f}")
    print(f"  CPA: ¥{summary.get('cpa', 0):.2f}")
    print(f"  ROAS: {summary.get('roas', 0):.2f}")

    print()

    # 场景2：热门话题抓取
    print("🔥 场景2：热门话题抓取")
    print("-"*60)

    topic_tracker = HotTopicTracker()

    # 模拟平台URL
    platform_urls = [
        'https://social-platform1.com/trending',
        'https://social-platform2.com/hot',
    ]

    all_topics = []
    for url in platform_urls:
        topics = topic_tracker.scrape_hot_topics(url, limit=10)
        all_topics.extend(topics)

    trend_analysis = topic_tracker.analyze_topic_trends(all_topics)

    print(f"\n📊 话题趋势分析:")
    print(f"  总话题数: {trend_analysis.get('total_topics', 0)}")
    print(f"  平均互动: {trend_analysis.get('avg_engagement', 0):.2f}")
    print(f"  TOP话题: {trend_analysis.get('top_topic', 'N/A')}")
    print(f"  平台分布: {trend_analysis.get('platform_distribution', {})}")

    print()

    # 场景3：KOL账号数据收集
    print("👥 场景3：KOL账号数据收集")
    print("-"*60)

    kol_collector = KOLDataCollector()

    # 模拟KOL URL
    kol_urls = [
        'https://social-platform.com/user/kol1',
        'https://social-platform.com/user/kol2',
        'https://social-platform.com/user/kol3',
    ]

    profiles = kol_collector.collect_kol_data(kol_urls)
    ranked_kols = kol_ranking = kol_collector.rank_kols(profiles)

    print(f"\n🏆 KOL排名 TOP 3:")
    for kol in ranked_kols[:3]:
        print(f"  #{kol['rank']} {kol['username']}")
        print(f"      粉丝: {kol['followers']:,}")
        print(f"      互动率: {kol['engagement_rate']:.2f}%")

    print()
    print("="*60)
    print("✅ 35-01 数字营销实战案例完成!")
    print("="*60)


if __name__ == '__main__':
    main()
