# 生产部署指南
# Production Deployment Guide

## 环境要求

### Python 环境
- Python 3.8+
- pip 20.0+

### 依赖安装
```bash
pip install scrapling pandas openpyxl curl_cffi browserforge
```

## 配置步骤

### 1. 配置文件准备

复制配置模板：
```bash
cp config/production.yaml config/local.yaml
```

根据实际需求修改配置：
- 代理池配置
- 并发数量
- 监控告警阈值
- 数据验证规则

### 2. 目录结构初始化

创建必要的目录：
```bash
mkdir -p output logs checkpoints
```

### 3. 选择器配置

为不同目标网站配置CSS选择器：

创建 `selectors.yaml`:
```yaml
selectors:
  example.com:
    title: "h1.product-title"
    price: ".price-value"
    description: ".product-description"

  another-site.com:
    title: "#product-name"
    price: ".cost"
    reviews: ".review-item"
```

## 部署模式

### 单机部署

适用于小规模数据采集：

```python
from core import ScraplingFetcher, DataCleaner, PerformanceMonitor

# 初始化组件
fetcher = ScraplingFetcher()
cleaner = DataCleaner()
monitor = PerformanceMonitor()

# 执行爬取
result = fetcher.fetch_single('https://example.com')

# 数据清洗
cleaned_data = cleaner.clean_text(result)

# 性能监控
monitor.record_request('https://example.com', duration=2.5, success=True)
monitor.print_stats()
```

### 分布式部署

适用于大规模数据采集：

使用 Celery + Redis:

```python
# tasks.py
from celery import Celery
from core import AsyncScraper

app = Celery('scraper', broker='redis://localhost:6379')

@app.task
def scrape_url(url):
    scraper = AsyncScraper(max_concurrent=5)
    return scraper.fetch_batch_async([url])
```

启动 Worker:
```bash
celery -A tasks worker --loglevel=info
```

## 监控和告警

### 性能监控

```python
from core.monitoring import PerformanceMonitor

monitor = PerformanceMonitor(alert_thresholds={
    'error_rate': 0.5,
    'avg_time': 30
})

# 检查告警
alerts = monitor.check_alerts()
for alert in alerts:
    print(f"ALERT: {alert['message']}")
```

### 错误追踪

```python
from core.monitoring import ErrorTracker

tracker = ErrorTracker()

try:
    # 爬取操作
    pass
except Exception as e:
    tracker.track_error(e, context={'url': url})
    tracker.print_error_summary()
```

## 性能优化建议

### 1. 并发控制
- 小规模 (<1000页): max_concurrent = 3-5
- 中规模 (1000-10000页): max_concurrent = 5-10
- 大规模 (>10000页): max_concurrent = 10-20

### 2. 代理池管理
- 使用高质量代理服务
- 定期刷新代理池
- 监控代理成功率

### 3. 数据分批处理
- 每批 100-1000 条数据
- 及时保存中间结果
- 实现断点续传

### 4. 内存优化
- 使用生成器处理大数据
- 及时释放已处理数据
- 控制并发任务数量

## 安全建议

### 1. 访问控制
- 设置请求频率限制
- 使用 User-Agent 轮换
- 配置合理的延迟

### 2. 数据保护
- 加密存储敏感数据
- 遵守数据保护法规
- 实现数据访问审计

### 3. 错误处理
- 实现优雅降级
- 记录详细错误日志
- 设置合理的超时时间

## 故障排查

### 常见问题

**问题 1**: 代理连接失败
```
解决:
1. 检查代理可用性
2. 切换备用代理
3. 检查网络连接
```

**问题 2**: 内存溢出
```
解决:
1. 减少并发数量
2. 分批处理数据
3. 使用流式处理
```

**问题 3**: 被目标网站封禁
```
解决:
1. 降低请求频率
2. 更换User-Agent
3. 使用高质量代理
```

## 维护建议

### 日常维护
- 每日检查错误日志
- 每周分析性能指标
- 每月更新代理池

### 定期优化
- 根据监控数据调整并发数
- 优化选择器规则
- 更新数据验证逻辑

### 备份策略
- 定期备份数据
- 备份配置文件
- 记录重要变更

## 扩展功能

### 1. 分布式爬取
集成 Celery、Dask 或 Ray

### 2. 持久化存储
集成数据库（MySQL、PostgreSQL、MongoDB）

### 3. 实时监控
集成 Prometheus + Grafana

### 4. 告警通知
集成邮件、钉钉、企业微信等

## 相关文档

- [API文档](./docs/api.md)
- [配置说明](./docs/configuration.md)
- [最佳实践](./docs/best-practices.md)
- [故障排查](./docs/troubleshooting.md)

---

**更新日期**: 2025-02-26
**版本**: v1.1.0
