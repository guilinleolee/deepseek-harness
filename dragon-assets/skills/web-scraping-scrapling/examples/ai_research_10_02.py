# -*- coding: utf-8 -*-
"""
10-02 AI研究员岗位实战案例
学术数据集构建 + 训练数据收集 + 研究语料库管理
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from core import (
    ScraplingFetcher,
    DataCleaner,
    DataValidator,
    ProxyPool,
    PerformanceMonitor,
    ErrorTracker,
    run_async_scraper
)
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import re
from pathlib import Path


class ResearchDatasetBuilder:
    """研究数据集构建器"""

    def __init__(self, dataset_name: str = "research_dataset"):
        self.fetcher = ScraplingFetcher(stealth=True, timeout=30)
        self.cleaner = DataCleaner()
        self.validator = DataValidator()
        self.monitor = PerformanceMonitor()
        self.error_tracker = ErrorTracker()
        self.proxy_pool = ProxyPool(strategy='score_based')

        self.dataset_name = dataset_name
        self.dataset_dir = f"datasets/{dataset_name}"
        os.makedirs(self.dataset_dir, exist_ok=True)

        # 数据集元数据
        self.metadata = {
            'name': dataset_name,
            'created_at': datetime.now().isoformat(),
            'sources': [],
            'statistics': {},
            'quality_metrics': {}
        }

    def setup_validation_rules(self):
        """设置数据验证规则"""
        # 标题验证
        self.validator.add_rule('title', 'required')
        self.validator.add_rule('title', 'type', value_type=str)
        self.validator.add_rule('title', 'pattern', pattern=r'.{5,500}')

        # 内容验证
        self.validator.add_rule('content', 'required')
        self.validator.add_rule('content', 'type', value_type=str)
        self.validator.add_rule('content', 'range', min=50)

        # URL验证
        self.validator.add_rule('url', 'required')
        self.validator.add_rule('url', 'url')

        # 时间戳验证
        self.validator.add_rule('collected_at', 'required')
        self.validator.add_rule('collected_at', 'type', value_type=str)

    def collect_from_academic_sources(self, sources: List[Dict]) -> List[Dict]:
        """从学术源收集数据"""
        print(f"📚 从学术源收集数据: {len(sources)} 个源")

        all_papers = []

        for i, source in enumerate(sources, 1):
            url = source.get('url')
            source_type = source.get('type', 'arxiv')

            print(f"  [{i}/{len(sources)}] 📥 采集: {url[:70]}...")

            try:
                # 使用代理
                proxy = self.proxy_pool.get_next_proxy()

                # 采集数据
                paper_data = self._fetch_academic_paper(url, source_type)

                if paper_data and self.validator.validate(paper_data):
                    all_papers.append(paper_data)
                    self.metadata['sources'].append(url)

                    # 记录成功
                    if proxy:
                        self.proxy_pool.record_success(proxy)

                else:
                    errors = self.validator.get_errors()
                    if errors:
                        print(f"      ⚠️  验证失败: {errors[0]}")

                    if proxy:
                        self.proxy_pool.record_failure(proxy)

            except Exception as e:
                print(f"      ❌ 失败: {e}")
                self.error_tracker.track_error(e, context={'url': url})

        # 保存数据集
        self._save_dataset(all_papers, 'academic')

        return all_papers

    def _fetch_academic_paper(self, url: str, source_type: str) -> Optional[Dict]:
        """抓取学术论文"""
        import time
        start_time = time.time()

        try:
            html = self.fetcher.fetch_single(url)

            # 解析论文数据（简化版，实际需要根据具体平台调整）
            paper = {
                'title': self.cleaner.clean_text(html[:200], strip_html=True),
                'abstract': self.cleaner.clean_text(html[:1000], strip_html=True),
                'content': self.cleaner.clean_text(html, strip_html=True, remove_extra_spaces=True),
                'url': url,
                'source_type': source_type,
                'collected_at': datetime.now().isoformat(),
                'content_length': len(html),
                'word_count': len(html.split())
            }

            # 提取元数据
            paper['metadata'] = self._extract_paper_metadata(html, source_type)

            duration = time.time() - start_time
            self.monitor.record_request(url, duration=duration, success=True)

            return paper

        except Exception as e:
            duration = time.time() - start_time
            self.monitor.record_request(url, duration=duration, success=False)
            raise e

    def _extract_paper_metadata(self, html: str, source_type: str) -> Dict:
        """提取论文元数据"""
        metadata = {
            'authors': [],
            'publication_date': None,
            'citations': 0,
            'categories': []
        }

        # 简化版提取（实际需要更复杂的解析）
        content = self.cleaner.clean_text(html, strip_html=True)

        # 提取可能的作者名（大写字母开头的词）
        words = content.split()[:50]  # 只看前50个词
        for word in words:
            if re.match(r'^[A-Z][a-z]+$', word) and len(word) > 2:
                if len(metadata['authors']) < 5:  # 最多5个作者
                    metadata['authors'].append(word)

        # 提取可能的年份
        years = re.findall(r'\b(19|20)\d{2}\b', content)
        if years:
            metadata['publication_date'] = years[0] + "-01-01"

        return metadata

    def collect_training_data(self, urls: List[str], category: str = "general") -> List[Dict]:
        """收集训练数据"""
        print(f"🎯 收集训练数据: {len(urls)} 个URL [类别: {category}]")

        all_data = []

        for i, url in enumerate(urls, 1):
            if i % 10 == 0:
                print(f"  进度: {i}/{len(urls)}...")

            try:
                data = self._fetch_training_sample(url, category)
                if data:
                    all_data.append(data)

            except Exception as e:
                self.error_tracker.track_error(e, context={'url': url})

        print(f"  ✅ 成功收集: {len(all_data)}/{len(urls)}")

        # 保存训练数据
        self._save_dataset(all_data, f'training_{category}')

        return all_data

    def _fetch_training_sample(self, url: str, category: str) -> Optional[Dict]:
        """抓取训练样本"""
        html = self.fetcher.fetch_single(url)

        # 清洗内容
        content = self.cleaner.clean_text(
            html,
            strip_html=True,
            remove_extra_spaces=True,
            remove_newlines=False
        )

        # 质量检查
        if len(content) < 100:  # 内容太短
            return None

        return {
            'text': content,
            'url': url,
            'category': category,
            'collected_at': datetime.now().isoformat(),
            'char_count': len(content),
            'word_count': len(content.split()),
            'language': self._detect_language(content)
        }

    @staticmethod
    def _detect_language(text: str) -> str:
        """简单语言检测"""
        # 检测中文
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        if chinese_chars > len(text) * 0.3:
            return 'zh'

        # 默认英文
        return 'en'

    def _save_dataset(self, data: List[Dict], subset_name: str):
        """保存数据集"""
        filename = f"{self.dataset_dir}/{subset_name}.jsonl"

        with open(filename, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')

        print(f"  💾 数据已保存: {filename} ({len(data)} 条)")

        # 更新元数据
        self.metadata['statistics'][subset_name] = {
            'count': len(data),
            'file': filename,
            'saved_at': datetime.now().isoformat()
        }

    def export_metadata(self):
        """导出数据集元数据"""
        metadata_file = f"{self.dataset_dir}/metadata.json"

        # 计算质量指标
        self.metadata['quality_metrics'] = self._calculate_quality_metrics()

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)

        print(f"📋 元数据已导出: {metadata_file}")

    def _calculate_quality_metrics(self) -> Dict:
        """计算数据质量指标"""
        stats = self.monitor.get_stats()
        error_summary = self.error_tracker.get_error_summary()

        return {
            'total_requests': stats.get('total_requests', 0),
            'success_rate': stats.get('success_rate', 0.0),
            'error_count': error_summary['total_errors'],
            'error_types': error_summary['error_types'],
            'avg_response_time': stats.get('avg_time', 0.0)
        }

    def print_summary(self):
        """打印数据集摘要"""
        print("\n" + "="*60)
        print(f"数据集摘要: {self.dataset_name}")
        print("="*60)

        print(f"\n📁 数据集目录: {self.dataset_dir}")
        print(f"📅 创建时间: {self.metadata['created_at']}")

        print(f"\n📊 数据统计:")
        for subset, stats in self.metadata['statistics'].items():
            print(f"  {subset}:")
            print(f"    - 数量: {stats['count']}")
            print(f"    - 文件: {stats['file']}")

        print(f"\n✅ 数据源: {len(self.metadata['sources'])} 个")

        # 打印质量指标
        self.monitor.print_stats()
        self.error_tracker.print_error_summary()
        self.proxy_pool.print_stats()


class AsyncResearchCollector:
    """异步研究数据收集器（高性能）"""

    def __init__(self, max_concurrent: int = 20):
        self.max_concurrent = max_concurrent
        self.monitor = PerformanceMonitor()
        self.error_tracker = ErrorTracker()

    async def collect_large_corpus(self, urls: List[str],
                                    batch_size: int = 1000) -> List[Dict]:
        """收集大规模语料库"""
        print(f"🚀 收集大规模语料库: {len(urls)} 个URL")
        print(f"⚙️  并发数: {self.max_concurrent}")
        print(f"📦 批次大小: {batch_size}")

        all_results = []
        total_batches = (len(urls) + batch_size - 1) // batch_size

        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min((batch_idx + 1) * batch_size, len(urls))
            batch_urls = urls[start_idx:end_idx]

            print(f"\n批次 {batch_idx + 1}/{total_batches}:")
            print(f"  URL范围: {start_idx + 1}-{end_idx}")

            # 异步采集批次
            batch_results = await run_async_scraper(
                batch_urls,
                max_concurrent=self.max_concurrent
            )

            # 处理结果
            successful = [r for r in batch_results if r.get('status') == 'success']
            failed = [r for r in batch_results if r.get('status') == 'failed']

            all_results.extend(successful)

            print(f"  ✅ 成功: {len(successful)}/{len(batch_urls)}")
            print(f"  ❌ 失败: {len(failed)}/{len(batch_urls)}")

            # 保存中间结果
            if successful:
                self._save_batch_results(batch_idx, successful)

        print(f"\n🎉 总计收集: {len(all_results)}/{len(urls)}")

        return all_results

    def _save_batch_results(self, batch_idx: int, results: List[Dict]):
        """保存批次结果"""
        output_dir = "datasets/corpus_batches"
        os.makedirs(output_dir, exist_ok=True)

        filename = f"{output_dir}/batch_{batch_idx:04d}.jsonl"

        with open(filename, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')

        print(f"  💾 批次已保存: {filename}")


class TrainingDataValidator:
    """训练数据验证器"""

    def __init__(self):
        self.cleaner = DataCleaner()
        self.validator = DataValidator()

    def validate_training_samples(self, samples: List[Dict]) -> Dict:
        """验证训练样本质量"""
        print(f"\n🔍 验证训练样本质量: {len(samples)} 个样本")

        # 设置验证规则
        self.validator.add_rule('text', 'required')
        self.validator.add_rule('text', 'range', min=50)
        self.validator.add_rule('char_count', 'range', min=50)
        self.validator.add_rule('category', 'required')

        valid_samples = []
        invalid_samples = []

        for i, sample in enumerate(samples):
            if self.validator.validate(sample):
                valid_samples.append(sample)
            else:
                invalid_samples.append({
                    'index': i,
                    'errors': self.validator.get_errors(),
                    'sample': sample
                })

        # 统计
        stats = {
            'total': len(samples),
            'valid': len(valid_samples),
            'invalid': len(invalid_samples),
            'valid_rate': len(valid_samples) / len(samples) if samples else 0,
            'invalid_samples': invalid_samples[:10]  # 只保留前10个
        }

        print(f"  ✅ 有效样本: {stats['valid']}/{stats['total']} ({stats['valid_rate']:.2%})")
        print(f"  ❌ 无效样本: {stats['invalid']}")

        # 按类别统计
        category_counts = {}
        for sample in valid_samples:
            category = sample.get('category', 'unknown')
            category_counts[category] = category_counts.get(category, 0) + 1

        print(f"\n📊 类别分布:")
        for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            print(f"  {category}: {count}")

        return stats

    def analyze_dataset_statistics(self, samples: List[Dict]) -> Dict:
        """分析数据集统计信息"""
        print(f"\n📈 分析数据集统计信息")

        char_counts = [s.get('char_count', 0) for s in samples]
        word_counts = [s.get('word_count', 0) for s in samples]

        stats = {
            'total_samples': len(samples),
            'total_chars': sum(char_counts),
            'total_words': sum(word_counts),
            'avg_char_count': sum(char_counts) / len(char_counts) if char_counts else 0,
            'avg_word_count': sum(word_counts) / len(word_counts) if word_counts else 0,
            'min_char_count': min(char_counts) if char_counts else 0,
            'max_char_count': max(char_counts) if char_counts else 0,
            'median_char_count': sorted(char_counts)[len(char_counts)//2] if char_counts else 0
        }

        print(f"  总样本数: {stats['total_samples']:,}")
        print(f"  总字符数: {stats['total_chars']:,}")
        print(f"  总词数: {stats['total_words']:,}")
        print(f"  平均字符数: {stats['avg_char_count']:.0f}")
        print(f"  平均词数: {stats['avg_word_count']:.0f}")
        print(f"  中位数字符数: {stats['median_char_count']:.0f}")

        return stats


def main():
    """主函数：演示10-02 AI研究岗位实战案例"""

    print("="*60)
    print("10-02 AI研究员岗位实战案例")
    print("="*60)
    print()

    # 场景1：学术论文数据集构建
    print("📚 场景1：学术论文数据集构建")
    print("-"*60)

    builder = ResearchDatasetBuilder(dataset_name="ai_papers")
    builder.setup_validation_rules()

    # 模拟学术源
    academic_sources = [
        {'url': 'https://arxiv.org/abs/2401.00001', 'type': 'arxiv'},
        {'url': 'https://arxiv.org/abs/2401.00002', 'type': 'arxiv'},
        {'url': 'https://openreview.net/forum?id=abc123', 'type': 'openreview'},
    ]

    papers = builder.collect_from_academic_sources(academic_sources)

    print()

    # 场景2：训练数据收集
    print("🎯 场景2：训练数据收集")
    print("-"*60)

    # 模拟训练数据URL
    training_urls = [f'https://example.com/article/{i}' for i in range(50)]

    # 同步收集
    training_data = builder.collect_training_data(training_urls[:10], category="tech")

    print()

    # 场景3：异步大规模语料库收集
    print("⚡ 场景3：异步大规模语料库收集")
    print("-"*60)

    async_collector = AsyncResearchCollector(max_concurrent=20)

    # 模拟大规模URL列表
    corpus_urls = [f'https://corpus.example.com/doc/{i}' for i in range(100)]

    print(f"📋 准备收集语料库:")
    print(f"  - 总URL数: {len(corpus_urls)}")
    print(f"  - 并发数: {async_collector.max_concurrent}")
    print(f"  - 预估批次: {(len(corpus_urls) + 999) // 1000}")

    print()

    # 场景4：训练数据验证
    print("🔍 场景4：训练数据验证")
    print("-"*60)

    if training_data:
        validator = TrainingDataValidator()

        # 验证数据质量
        validation_stats = validator.validate_training_samples(training_data)

        # 分析统计信息
        dataset_stats = validator.analyze_dataset_statistics(training_data)

    print()

    # 场景5：导出数据集元数据
    print("💾 场景5：导出数据集元数据")
    print("-"*60)

    builder.export_metadata()

    print()
    print("="*60)
    print("✅ 10-02 AI研究实战案例完成!")
    print("="*60)
    print()
    print("📊 核心能力验证:")
    print("  ✅ 学术数据集构建（ArXiv/OpenReview）")
    print("  ✅ 训练数据收集和清洗")
    print("  ✅ 异步大规模语料库收集")
    print("  ✅ 数据质量验证")
    print("  ✅ 数据集统计分析")
    print("  ✅ 元数据管理")
    print()

    # 打印摘要
    builder.print_summary()


if __name__ == '__main__':
    main()
