"""
监控和性能追踪模块
"""

import time
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self, alert_thresholds: Optional[Dict[str, float]] = None):
        """
        初始化性能监控器

        Args:
            alert_thresholds: 告警阈值配置
        """
        self.alert_thresholds = alert_thresholds or {
            'error_rate': 0.5,        # 错误率超过50%告警
            'avg_time': 30,            # 平均时间超过30秒告警
            'fail_rate': 0.3,          # 失败率超过30%告警
        }

        self.metrics = defaultdict(list)
        self.alerts = []

    def record_metric(self, name: str, value: Any):
        """记录指标"""
        self.metrics[name].append({
            'value': value,
            'timestamp': time.time()
        })

    def record_request(self, url: str, duration: float, success: bool):
        """记录请求"""
        self.record_metric('requests', {
            'url': url,
            'duration': duration,
            'success': success,
            'timestamp': datetime.now().isoformat()
        })

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'success_rate': 0.0,
            'error_rate': 0.0,
            'avg_time': 0.0,
            'max_time': 0.0,
            'min_time': 0.0
        }

        # 请求统计
        requests = self.metrics.get('requests', [])
        if requests:
            # 检查是否是record_request记录的数据
            # record_request将数据包装在'value'键中
            first_request = requests[0]
            request_data = first_request.get('value', first_request)

            if 'success' in request_data:
                total = len(requests)
                successful = sum(1 for r in requests if r.get('value', r).get('success'))
                failed = total - successful

                stats['total_requests'] = total
                stats['successful_requests'] = successful
                stats['failed_requests'] = failed
                stats['success_rate'] = successful / total if total > 0 else 0
                stats['error_rate'] = failed / total if total > 0 else 0

                # 时间统计
                durations = [r.get('value', r).get('duration', 0) for r in requests]
                stats['avg_time'] = sum(durations) / len(durations) if durations else 0
                stats['max_time'] = max(durations) if durations else 0
                stats['min_time'] = min(durations) if durations else 0
            else:
                # 通用指标统计
                stats['total_requests'] = len(requests)

        return stats

    def check_alerts(self) -> List[Dict[str, Any]]:
        """检查告警"""
        stats = self.get_stats()
        new_alerts = []

        # 错误率告警
        error_rate_threshold = self.alert_thresholds.get('error_rate', 0.5)
        if stats.get('error_rate', 0) > error_rate_threshold:
            new_alerts.append({
                'type': 'error_rate',
                'severity': 'high',
                'message': f"Error rate {stats['error_rate']:.2%} exceeds threshold",
                'value': stats['error_rate'],
                'threshold': error_rate_threshold
            })

        # 平均时间告警
        avg_time_threshold = self.alert_thresholds.get('avg_time', 30)
        if stats.get('avg_time', 0) > avg_time_threshold:
            new_alerts.append({
                'type': 'avg_time',
                'severity': 'medium',
                'message': f"Average time {stats['avg_time']:.2f}s exceeds threshold",
                'value': stats['avg_time'],
                'threshold': avg_time_threshold
            })

        self.alerts.extend(new_alerts)
        return new_alerts

    def print_stats(self):
        """打印统计信息"""
        stats = self.get_stats()

        print("\n" + "="*50)
        print("Performance Statistics")
        print("="*50)

        if 'total_requests' in stats:
            print(f"Total requests: {stats['total_requests']}")
            print(f"Successful: {stats['successful_requests']}")
            print(f"Failed: {stats['failed_requests']}")
            print(f"Success rate: {stats['success_rate']:.2%}")
            print(f"Error rate: {stats['error_rate']:.2%}")
            print(f"Avg time: {stats['avg_time']:.2f}s")
            print(f"Max time: {stats['max_time']:.2f}s")
            print(f"Min time: {stats['min_time']:.2f}s")

        print("="*50 + "\n")

    def export_metrics(self, filepath: str):
        """导出指标到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'metrics': dict(self.metrics),
                'stats': self.get_stats(),
                'alerts': self.alerts,
                'exported_at': datetime.now().isoformat()
            }, f, indent=2, default=str)

        logger.info(f"Metrics exported to {filepath}")


class ErrorTracker:
    """错误追踪器"""

    def __init__(self, max_errors: int = 1000):
        """
        初始化错误追踪器

        Args:
            max_errors: 最大错误记录数
        """
        self.max_errors = max_errors
        self.errors = []
        self.error_counts = defaultdict(int)

    def track_error(self, error: Exception, context: Optional[Dict] = None):
        """追踪错误"""
        error_info = {
            'type': type(error).__name__,
            'message': str(error),
            'context': context or {},
            'timestamp': datetime.now().isoformat()
        }

        self.errors.append(error_info)
        self.error_counts[error_info['type']] += 1

        # 保持最大数量限制
        if len(self.errors) > self.max_errors:
            self.errors = self.errors[-self.max_errors:]

        logger.error(f"Error tracked: {error_info['type']} - {error_info['message']}")

    def get_error_summary(self) -> Dict[str, Any]:
        """获取错误摘要"""
        return {
            'total_errors': len(self.errors),
            'error_types': dict(self.error_counts),
            'recent_errors': self.errors[-10:]  # 最近10个错误
        }

    def print_error_summary(self):
        """打印错误摘要"""
        summary = self.get_error_summary()

        print("\n" + "="*50)
        print("Error Summary")
        print("="*50)
        print(f"Total errors: {summary['total_errors']}")

        if summary['error_types']:
            print("\nError types:")
            for error_type, count in summary['error_types'].items():
                print(f"  {error_type}: {count}")

        if summary['recent_errors']:
            print("\nRecent errors:")
            for error in summary['recent_errors'][-5:]:
                print(f"  [{error['type']}] {error['message']}")

        print("="*50 + "\n")
