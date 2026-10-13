"""
简化版性能基准测试

测试指标:
- 缓存命中率
- 延迟百分位数 P50/P95/P99
- 吞吐量
"""

import pytest
import time
import tempfile
import os
from datetime import datetime

from core.fetcher import UnifiedFetcher
from core.config import Config
from models.article import Article


def create_test_article(url, title="Test Article"):
    """创建测试Article对象"""
    return Article(
        url=url,
        url_hash="",
        title=title,
        author="Test Author",
        account_name="Test Account",
        content_html="<html>Test</html>",
        content_markdown="Test",
        content_text="Test",
        source="cache",
        fetch_time=datetime.now()
    )


def test_cache_performance():
    """测试缓存性能"""

    # 创建临时数据库
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db.close()
    db_path = temp_db.name

    try:
        # 创建配置
        config = Config(
            cache_path=db_path,
            cache_enabled=True,
            l1_cache_size=100,
            cache_ttl_days=30
        )

        fetcher = UnifiedFetcher(config=config)

        # 测试URL列表
        test_urls = [f"https://mp.weixin.qq.com/s/bench{i}" for i in range(20)]

        print("\n" + "="*60)
        print("缓存性能测试")
        print("="*60)

        # 第一轮：填充缓存
        print("\n[第一轮] 填充缓存...")
        start = time.time()
        for url in test_urls:
            article = create_test_article(url)
            fetcher.cache.set(article)
        fill_time = time.time() - start

        # 第二轮：测试缓存命中
        print("[第二轮] 测试缓存命中...")
        cache_hits = 0
        total = 0
        latencies = []

        for i in range(100):
            url = test_urls[i % len(test_urls)]
            start_time = time.time()
            result = fetcher.cache.get(url)
            latency_ms = (time.time() - start_time) * 1000
            latencies.append(latency_ms)
            total += 1
            if result:
                cache_hits += 1

        # 计算统计信息
        latencies_sorted = sorted(latencies)
        p50 = latencies_sorted[int(len(latencies_sorted) * 0.50)]
        p95 = latencies_sorted[int(len(latencies_sorted) * 0.95)]
        p99 = latencies_sorted[int(len(latencies_sorted) * 0.99)]
        avg = sum(latencies) / len(latencies)

        # 输出结果
        print("\n" + "="*60)
        print("性能测试结果")
        print("="*60)
        print(f"缓存填充时间: {fill_time:.3f}s")
        print(f"总请求数: {total}")
        print(f"缓存命中数: {cache_hits}")
        print(f"缓存命中率: {cache_hits/total*100:.1f}%")
        print(f"\n延迟统计 (毫秒):")
        print(f"  平均: {avg:.3f}ms")
        print(f"  P50: {p50:.3f}ms")
        print(f"  P95: {p95:.3f}ms")
        print(f"  P99: {p99:.3f}ms")
        print(f"  最小: {min(latencies):.3f}ms")
        print(f"  最大: {max(latencies):.3f}ms")
        print("="*60)

        # 生成性能报告
        report_path = "C:/Users/li/.claude/skills/wechat-skills-unified/docs/PERFORMANCE_BENCHMARK_V1.0.2.md"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# 性能基准测试报告 V1.0.2\n\n")
            f.write(f"**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**项目版本**: WeChat SKILL Unified V1.0.2\n\n")

            f.write("## 测试环境\n\n")
            f.write("- Python 3.8+\n")
            f.write("- SQLite 缓存\n")
            f.write("- L1内存缓存: 100条\n")
            f.write("- 测试URL数: 20\n")
            f.write("- 总请求数: 100\n\n")

            f.write("## 测试结果\n\n")

            f.write("### 缓存命中率\n\n")
            f.write(f"- **总请求**: {total}\n")
            f.write(f"- **缓存命中**: {cache_hits}\n")
            f.write(f"- **命中率**: {cache_hits/total*100:.1f}%\n")
            f.write(f"- **目标**: >85%\n")
            f.write(f"- **状态**: {'[PASS]' if cache_hits/total > 0.85 else '[FAIL]'}\n\n")

            f.write("### 延迟百分位数\n\n")
            f.write(f"- **平均延迟**: {avg:.3f}ms\n")
            f.write(f"- **P50**: {p50:.3f}ms\n")
            f.write(f"- **P95**: {p95:.3f}ms\n")
            f.write(f"- **P99**: {p99:.3f}ms\n")
            f.write(f"- **范围**: {min(latencies):.3f}ms ~ {max(latencies):.3f}ms\n\n")

            f.write("## 总结\n\n")
            all_pass = cache_hits/total > 0.85 and p95 < 50
            f.write(f"**整体状态**: {'[PASS] 所有测试通过' if all_pass else '[FAIL] 部分指标未达标'}\n\n")

        print(f"\n[OK] 性能报告已保存到: {report_path}")

        # 断言
        assert cache_hits / total > 0.85, f"缓存命中率 {cache_hits/total*100:.1f}% 低于目标 85%"
        assert p95 < 50, f"P95延迟 {p95:.3f}ms 超过目标 50ms"

    finally:
        # 清理临时文件
        if os.path.exists(db_path):
            os.remove(db_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
