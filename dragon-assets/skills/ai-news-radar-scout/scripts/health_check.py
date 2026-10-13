#!/usr/bin/env python3
"""
AI News Radar - 信息源健康检查
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

try:
    import requests
except ImportError:
    print("错误: 请先安装依赖 pip install requests")
    exit(1)


class HealthChecker:
    """源健康检查器"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.results = []

    def check_source(self, url: str) -> dict:
        """检查单个源"""
        result = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "status_code": None,
            "response_time_ms": None,
            "error": None
        }

        try:
            import time
            start = time.time()
            response = requests.head(url, timeout=self.timeout, allow_redirects=True)
            elapsed = (time.time() - start) * 1000

            result["status_code"] = response.status_code
            result["response_time_ms"] = round(elapsed, 2)

            if response.status_code < 400:
                result["status"] = "healthy"
            elif response.status_code < 500:
                result["status"] = "client_error"
            else:
                result["status"] = "server_error"

        except requests.exceptions.Timeout:
            result["status"] = "timeout"
            result["error"] = "连接超时"
        except requests.exceptions.ConnectionError:
            result["status"] = "connection_error"
            result["error"] = "连接失败"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def check_batch(self, urls: list) -> dict:
        """批量检查"""
        for url in urls:
            result = self.check_source(url)
            self.results.append(result)

        stats = defaultdict(int)
        for r in self.results:
            stats[r["status"]] += 1

        return {
            "total": len(urls),
            "healthy": stats.get("healthy", 0),
            "unhealthy": sum(v for k, v in stats.items() if k != "healthy"),
            "by_status": dict(stats),
            "results": self.results
        }

    def generate_report(self, output_path: str = None):
        """生成健康报告"""
        stats = defaultdict(int)
        for r in self.results:
            stats[r["status"]] += 1

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": len(self.results),
                "healthy": stats.get("healthy", 0),
                "unhealthy": sum(v for k, v in stats.items() if k != "healthy"),
                "health_rate": stats.get("healthy", 0) / max(len(self.results), 1)
            },
            "by_status": dict(stats),
            "details": self.results
        }

        if output_path:
            Path(output_path).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"✅ 健康报告已生成: {output_path}")

        return report


def load_sources_from_json(config_path: str) -> list:
    """从JSON配置文件加载信息源"""
    try:
        data = json.loads(Path(config_path).read_text(encoding="utf-8"))
        return [s.get("url") or s.get("feed") for s in data.get("sources", [])]
    except:
        return []


def main():
    parser = argparse.ArgumentParser(description="AI News Radar - 源健康检查")
    parser.add_argument("--sources", help="信息源配置文件")
    parser.add_argument("--source-list", nargs="+", help="信息源URL列表")
    parser.add_argument("--output", "-o", help="输出报告路径")
    parser.add_argument("--timeout", type=int, default=10, help="超时秒数")

    args = parser.parse_args()

    # 加载信息源
    if args.sources:
        urls = load_sources_from_json(args.sources)
    elif args.source_list:
        urls = args.source_list
    else:
        urls = []

    if not urls:
        print("错误: 未提供信息源")
        sys.exit(1)

    checker = HealthChecker(timeout=args.timeout)
    checker.check_batch(urls)
    report = checker.generate_report(args.output)

    # 打印摘要
    print("\n📊 健康检查摘要:")
    print(f"   总计: {report['summary']['total']}")
    print(f"   健康: {report['summary']['healthy']}")
    print(f"   异常: {report['summary']['unhealthy']}")
    print(f"   健康率: {report['summary']['health_rate']:.1%}")


if __name__ == "__main__":
    main()
