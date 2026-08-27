# Web Scraping Workflow
# Scrapling 网络爬虫工作流配置

## 工作流概览

本工作流定义了如何高效地使用 Scrapling 进行网络数据采集，确保任务成功、合法且高效。

---

## 阶段 1: 需求分析 🔍

### 输入检查清单
- [ ] 明确目标网站/URL列表
- [ ] 定义需要提取的数据字段
- [ ] 确认数据格式要求 (JSON/CSV/Excel)
- [ ] 评估数据量和时间要求
- [ ] 检查目标网站的 robots.txt

### 风险评估
```
低风险: 公开数据、官方API、少量请求
中风险: 需要登录、频率限制、需要代理
高风险: 强反爬、验证码、法律灰色地带
```

### 决策树
```
是否需要登录？
├─ 是 → 使用浏览器自动化模式 (playwright)
└─ 否 → 使用快速 HTTP 模式

是否有反爬机制？
├─ 是 → 启用反检测模式 (stealth=True)
└─ 否 → 普通模式即可

数据量大小？
├─ <100页 → 单次任务
├─ 100-1000页 → 批量任务 + 延迟
└─ >1000页 → 分布式爬取 + 断点续传
```

---

## 阶段 2: 环境准备 🛠️

### 依赖安装
```bash
# 核心依赖
pip install scrapling pandas openpyxl

# 浏览器模式
scrapling install

# 可选依赖
pip install aiohttp  # 异步加速
pip install proxy-provider  # 代理池
```

### 配置文件创建
创建 `scrapling_config.yaml`:
```yaml
# 请求配置
request:
  timeout: 30
  retry_times: 3
  delay_range: [1, 3]

# 代理配置
proxy:
  enabled: true
  pool_size: 10
  rotation_strategy: round_robin

# 反检测配置
stealth:
  tls_fingerprint: true
  cloudflare_bypass: true
  user_agent_rotation: true

# 导出配置
export:
  default_format: json
  encoding: utf-8
  pretty_print: true
  batch_size: 100
```

---

## 阶段 3: 数据采集 🚀

### 模式选择

#### 模式 A: 快速 HTTP 模式
**适用场景**: 静态页面、无登录、低反爬
```python
from scrapling import Fetcher

fetcher = Fetcher(stealth=True)
result = fetcher.fetch('https://example.com')
data = result.select('.product-card')
```

#### 模式 B: 浏览器自动化模式
**适用场景**: 动态页面、需要登录、高反爬
```python
from scrapling import PlaywrightFetcher

fetcher = PlaywrightFetcher(headless=True)
result = fetcher.fetch('https://example.com', wait_for_selector='.data-loaded')
data = result.text
```

#### 模式 C: 批量任务模式
**适用场景**: 多页面、大数据量
```python
from scrapling import Fetcher
import pandas as pd

urls = [f'https://example.com/page/{i}' for i in range(1, 101)]
fetcher = Fetcher(stealth=True, delay=2)

results = []
for url in urls:
    try:
        result = fetcher.fetch(url)
        results.append(extract_data(result))
    except Exception as e:
        log_error(url, e)

df = pd.DataFrame(results)
df.to_excel('output.xlsx')
```

---

## 阶段 4: 数据清洗 🧹

### 清洗步骤
```python
def clean_data(raw_data):
    # 1. 去重
    data = drop_duplicates(raw_data)

    # 2. 空值处理
    data = handle_missing(data)

    # 3. 格式标准化
    data = normalize_format(data)

    # 4. 数据验证
    data = validate(data)

    return data
```

### 质量检查
- [ ] 数据完整性检查 (空值率 <5%)
- [ ] 数据一致性检查 (格式统一)
- [ ] 数据准确性检查 (采样验证)
- [ ] 重复数据检查 (去重率)

---

## 阶段 5: 数据导出 📦

### 导出格式选择
```python
# JSON 格式 (适合程序处理)
data.to_json('output.json', orient='records', force_ascii=False)

# CSV 格式 (适合 Excel 打开)
data.to_csv('output.csv', index=False, encoding='utf-8-sig')

# Excel 格式 (支持多Sheet)
with pd.ExcelWriter('output.xlsx') as writer:
    data.to_excel(writer, sheet_name='数据', index=False)
    summary.to_excel(writer, sheet_name='统计', index=False)
```

---

## 阶段 6: 监控与优化 📊

### 性能监控
```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start

        print(f"⏱️ {func.__name__} 耗时: {elapsed:.2f}秒")
        print(f"📊 成功率: {success_rate:.2%}")
        print(f"🚀 平均速度: {len(urls)/elapsed:.2f} 页/秒")

        return result
    return wrapper
```

### 错误处理
```python
class ScrapingErrorHandler:
    def __init__(self):
        self.errors = []

    def handle(self, url, error):
        error_type = type(error).__name__

        if error_type == 'TimeoutError':
            # 重试
            return retry_strategy(url)

        elif error_type == 'HTTPError':
            # 代理切换
            return switch_proxy(url)

        elif error_type == 'ParseError':
            # 记录并跳过
            self.log_parse_error(url, error)
            return None

        else:
            # 未知错误，记录并终止
            self.log_unknown_error(url, error)
            raise
```

---

## 最佳实践 ⭐

### ✅ DO (推荐做法)

1. **遵守 robots.txt**
   ```python
   # 检查 robots.txt
   from urllib.robotparser import RobotFileParser

   rp = RobotFileParser()
   rp.set_url('https://example.com/robots.txt')
   rp.read()

   if rp.can_fetch('my-bot', url):
       fetch(url)
   ```

2. **控制请求频率**
   ```python
   import random
   import time

   # 随机延迟 1-3 秒
   time.sleep(random.uniform(1, 3))
   ```

3. **使用代理轮换**
   ```python
   proxies = [
       'http://proxy1.example.com:8080',
       'http://proxy2.example.com:8080',
   ]

   proxy = random.choice(proxies)
   fetch(url, proxy=proxy)
   ```

4. **设置超时时间**
   ```python
   fetcher = Fetcher(timeout=30, retry_times=3)
   ```

5. **增量更新**
   ```python
   # 只爬取新数据
   last_crawl_time = get_last_crawl_time()
   new_data = filter_by_time(data, last_crawl_time)
   ```

### ❌ DON'T (避免做法)

1. ❌ 不要过度频繁请求 (会被封IP)
2. ❌ 不要爬取个人隐私数据 (法律风险)
3. ❌ 不要绕过付费墙 (版权问题)
4. ❌ 不要用于商业间谍 (法律风险)
5. ❌ 不要忽视 robots.txt (不道德)

---

## 常见问题排查 🔧

### 问题 1: 403 Forbidden
**原因**: IP被封或User-Agent被识别
**解决**:
- 启用反检测模式 `stealth=True`
- 更换代理IP
- 轮换User-Agent

### 问题 2: 数据不完整
**原因**: 页面未完全加载
**解决**:
- 增加等待时间 `wait_for_selector`
- 使用浏览器模式
- 检查网络请求

### 问题 3: 速度太慢
**原因**: 同步阻塞或延迟过大
**解决**:
- 使用异步请求 `aiohttp`
- 减少延迟时间
- 增加并发数

### 问题 4: 内存溢出
**原因**: 一次性加载太多数据
**解决**:
- 分批处理
- 使用生成器
- 及时释放内存

---

## 法律合规提醒 ⚖️

### 合法爬取原则
1. ✅ 只爬取公开数据
2. ✅ 遵守 robots.txt
3. ✅ 控制请求频率
4. ✅ 注明数据来源
5. ✅ 尊重版权

### 禁止爬取内容
1. ❌ 个人隐私信息
2. ❌ 付费内容
3. ❌ 商业机密
4. ❌ 国家安全数据
5. ❌ 违法内容

### 免责声明
> 本技能仅供学习和研究使用。使用者需自行承担使用风险，并遵守当地法律法规。开发者不对使用本技能造成的任何后果负责。

---

## 工作流检查清单 ✅

### 开始前
- [ ] 明确数据需求
- [ ] 检查 robots.txt
- [ ] 评估反爬风险
- [ ] 准备代理池

### 执行中
- [ ] 控制请求频率
- [ ] 监控错误率
- [ ] 记录日志
- [ ] 验证数据质量

### 完成后
- [ ] 数据去重
- [ ] 格式标准化
- [ ] 质量检查
- [ ] 备份数据
- [ ] 注明来源

---

## 扩展阅读 📚

- [Scrapling 官方文档](https://github.com/D4Vinci/Scrapling)
- [网络爬虫最佳实践](https://docs.python-requests.org/)
- [robots.txt 协议](https://www.robotstxt.org/)
- [数据安全法律](https://www.csriac.cn/)

---

**版本**: v1.0.0
**更新**: 2025-02-26
**维护**: Claude Code (Dragon Team)
