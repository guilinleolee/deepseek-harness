#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
opportunity-scout - 信号扫描核心脚本

扫描 HN、Product Hunt、GitHub 等平台的热门趋势
灵感来源: BuilderPulse 多源信号聚合逻辑
"""
import io
import sys

# 设置标准输出编码为 UTF-8
try:
    if hasattr(sys.stdout, 'buffer') and not sys.stdout.closed:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except Exception:
    pass

import json
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import requests

# ============ 配置 ============
DEFAULT_OUTPUT_PATH = Path.home() / ".claude" / "opportunity-scout" / "signals"
HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
GITHUB_TRENDING_API = "https://api.github.com/search/repositories"


class SignalScout:
    """信号侦察器"""

    def __init__(self, output_path: Optional[Path] = None):
        self.output_path = output_path or DEFAULT_OUTPUT_PATH
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.signals = []

    def scan_hn(self, limit: int = 30, story_type: str = "topstories") -> List[Dict]:
        """
        扫描 Hacker News

        Args:
            limit: 获取数量
            story_type: topstories, newstories, beststories
        """
        print(f"🔍 扫描 HN {story_type}...")

        try:
            # 获取故事 ID 列表
            response = requests.get(
                f"{HN_API_BASE}/{story_type}.json",
                timeout=10
            )
            story_ids = response.json()[:limit]

            signals = []
            for i, story_id in enumerate(story_ids):
                try:
                    response = requests.get(
                        f"{HN_API_BASE}/item/{story_id}.json",
                        timeout=5
                    )
                    story = response.json()

                    if story and story.get('title'):
                        signal = {
                            'id': f"hn_{story_id}",
                            'source': 'Hacker News',
                            'title': story.get('title', ''),
                            'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                            'score': story.get('score', 0),
                            'comments': story.get('descendants', 0),
                            'author': story.get('by', ''),
                            'timestamp': story.get('time', 0),
                            'created_at': datetime.fromtimestamp(story.get('time', 0)).isoformat() if story.get('time') else '',
                            'text': story.get('text', ''),
                            'type': 'story'
                        }
                        signals.append(signal)
                        self.signals.append(signal)

                    if (i + 1) % 10 == 0:
                        print(f"   进度: {i+1}/{len(story_ids)}")

                    time.sleep(0.1)  # 避免限流

                except Exception as e:
                    print(f"   ⚠️ 获取故事 {story_id} 失败: {e}")
                    continue

            print(f"✅ HN 扫描完成: {len(signals)} 条信号")
            return signals

        except Exception as e:
            print(f"❌ HN 扫描失败: {e}")
            return []

    def scan_github(self, limit: int = 20, timeframe: str = "daily") -> List[Dict]:
        """
        扫描 GitHub Trending

        Args:
            limit: 获取数量
            timeframe: daily, weekly, monthly
        """
        print(f"🔍 扫描 GitHub Trending ({timeframe})...")

        try:
            # GitHub Trending 页面
            trending_url = f"https://github.com/trending?since={timeframe}"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(trending_url, headers=headers, timeout=15)
            response.raise_for_status()

            signals = []

            # 简单解析 HTML (实际生产环境建议用 BeautifulSoup)
            import re
            html = response.text

            # 提取仓库信息
            repo_pattern = r'<h2[^>]*><a[^>]*href="(/[^"]+)"[^>]*>([^<]+)</a></h2>'
            desc_pattern = r'<p[^>]*class="[^"]*col-9[^"]*"[^>]*>([^<]+)</p>'
            star_pattern = r'<a[^>]*href="[^"]*stargazers[^"]*"[^>]*>([0-9,]+)</a>'

            repo_matches = re.findall(repo_pattern, html)
            desc_matches = re.findall(desc_pattern, html)
            star_matches = re.findall(star_pattern, html)

            for i, (match) in enumerate(repo_matches[:limit]):
                repo_path, repo_name = match[0].strip('/'), match[1].strip()
                description = desc_matches[i].strip() if i < len(desc_matches) else ''
                stars = star_matches[i].replace(',', '') if i < len(star_matches) else '0'

                signal = {
                    'id': f"github_{repo_path.replace('/', '_')}",
                    'source': 'GitHub Trending',
                    'title': repo_name,
                    'url': f"https://github.com/{repo_path}",
                    'description': description,
                    'stars': int(stars) if stars.isdigit() else 0,
                    'language': self._extract_language(html, i),
                    'author': repo_path.split('/')[0],
                    'created_at': datetime.now().isoformat(),
                    'type': 'repository'
                }
                signals.append(signal)
                self.signals.append(signal)

            print(f"✅ GitHub 扫描完成: {len(signals)} 条信号")
            return signals

        except Exception as e:
            print(f"❌ GitHub 扫描失败: {e}")
            return []

    def _extract_language(self, html: str, index: int) -> str:
        """从 HTML 中提取编程语言"""
        import re
        lang_pattern = r'<span[^>]*itemprop="programmingLanguage"[^>]*>([^<]+)</span>'
        matches = re.findall(lang_pattern, html)
        return matches[index].strip() if index < len(matches) else 'Unknown'

    def scan_product_hunt(self, limit: int = 20) -> List[Dict]:
        """
        扫描 Product Hunt (模拟实现)

        注意: Product Hunt 需要 API 认证，这里是简化实现
        实际使用时建议申请官方 API
        """
        print(f"🔍 扫描 Product Hunt...")

        # Product Hunt 公开页面
        ph_url = "https://www.producthunt.com/posts"

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html'
            }

            response = requests.get(ph_url, headers=headers, timeout=15)
            response.raise_for_status()

            signals = []

            # 简化解析 (Product Hunt 有反爬虫限制)
            # 实际使用时建议使用官方 API
            import re
            html = response.text

            # 尝试提取产品信息
            title_pattern = r'<h3[^>]*>([^<]+)</h3>'
            titles = re.findall(title_pattern, html)[:limit]

            for i, title in enumerate(titles):
                signal = {
                    'id': f"ph_{i}_{int(time.time())}",
                    'source': 'Product Hunt',
                    'title': title.strip(),
                    'url': ph_url,
                    'votes': 0,
                    'topics': [],
                    'created_at': datetime.now().isoformat(),
                    'type': 'product',
                    'note': '需要 Product Hunt API 才能获取完整数据'
                }
                signals.append(signal)
                self.signals.append(signal)

            print(f"⚠️ Product Hunt 需要 API 认证，获取了 {len(signals)} 条基础信号")
            return signals

        except Exception as e:
            print(f"❌ Product Hunt 扫描失败: {e}")
            return []

    def scan_all(self, limits: Dict[str, int] = None) -> List[Dict]:
        """
        全源扫描

        Args:
            limits: 各数据源的扫描数量
        """
        limits = limits or {'hn': 30, 'github': 20, 'ph': 20}

        print("=" * 50)
        print("🎯 开始全源信号扫描")
        print("=" * 50)

        self.signals = []  # 清空之前的结果

        # 扫描各数据源
        self.scan_hn(limit=limits.get('hn', 30))

        self.scan_github(limit=limits.get('github', 20))

        self.scan_product_hunt(limit=limits.get('ph', 20))

        # 汇总
        print()
        print("=" * 50)
        print(f"✅ 全源扫描完成: 共 {len(self.signals)} 条信号")

        by_source = {}
        for sig in self.signals:
            source = sig['source']
            by_source[source] = by_source.get(source, 0) + 1

        for source, count in by_source.items():
            print(f"   {source}: {count}")

        return self.signals

    def save(self, format: str = "json") -> Path:
        """保存信号"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if format == "json":
            output_file = self.output_path / f"signals_{timestamp}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'count': len(self.signals),
                    'signals': self.signals
                }, f, ensure_ascii=False, indent=2)
        else:
            output_file = self.output_path / f"signals_{timestamp}.md"
            lines = [f"# 信号扫描报告\n", f"**时间**: {datetime.now().isoformat()}\n",
                     f"**总数**: {len(self.signals)}\n\n"]
            for sig in self.signals:
                lines.append(f"## {sig['title']}\n")
                lines.append(f"- 来源: {sig['source']}\n")
                lines.append(f"- URL: {sig['url']}\n")
                lines.append(f"- 评分: {sig.get('score', sig.get('stars', 0))}\n\n")

            with open(output_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)

        print(f"✅ 信号已保存: {output_file}")
        return output_file


def main():
    parser = argparse.ArgumentParser(description="Opportunity Scout - 信号扫描")
    parser.add_argument("command", choices=["scan"], help="扫描命令")
    parser.add_argument("--source", choices=["hn", "github", "ph", "all"],
                        default="all", help="数据源")
    parser.add_argument("--limit", type=int, default=30, help="扫描数量")
    parser.add_argument("--format", choices=["json", "markdown"], default="json",
                        help="输出格式")
    parser.add_argument("--output", type=Path, help="输出路径")
    parser.add_argument("--quiet", action="store_true", help="静默模式")

    args = parser.parse_args()

    scout = SignalScout(args.output)

    if args.source == "hn":
        scout.scan_hn(limit=args.limit)
    elif args.source == "github":
        scout.scan_github(limit=args.limit)
    elif args.source == "ph":
        scout.scan_product_hunt(limit=args.limit)
    else:
        scout.scan_all({'hn': args.limit, 'github': args.limit, 'ph': args.limit})

    if not args.quiet:
        scout.save(format=args.format)


if __name__ == "__main__":
    main()
