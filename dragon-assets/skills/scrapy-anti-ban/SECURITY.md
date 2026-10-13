# SECURITY.md - Scrapy Anti-Ban 爬虫反检测安全指南

> ⚠️ 本Skill涉及网络爬虫操作，请务必阅读本文档

---

## ⚠️ 法律合规声明

**重要**: 使用爬虫前，请确保：

1. ✅ 遵守目标网站的 `robots.txt`
2. ✅ 遵守目标网站的服务条款
3. ✅ 不采集个人隐私数据
4. ✅ 不对目标服务器造成过大负载
5. ✅ 仅用于合法用途（研究、公开数据等）

---

## 🔴 高风险操作

### 高频请求爬虫

**风险**: 可能被目标网站封禁IP或账号

**症状**:
- IP被封禁
- 返回403/429错误
- 账号被封禁

**安全操作流程**:
```python
# 1. 设置合理的请求间隔
DOWNLOAD_DELAY = 2  # 秒

# 2. 使用代理池
ROTATING_PROXY_LIST = ['proxy1:8080', 'proxy2:8080']

# 3. 监控被封情况
python spider.py --monitor
```

### 绕过验证码

**风险**: 可能违反网站服务条款

**安全操作流程**:
```python
# 1. 检查是否有公开API
# 优先使用官方API

# 2. 降低请求频率避免触发验证码
CONCURRENT_REQUESTS = 1
DOWNLOAD_DELAY = 5

# 3. 使用验证码处理服务（仅限合法场景）
# CAPTCHA_SOLVER = '2captcha'  # 需要合法授权
```

---

## 🟡 中风险操作

### User-Agent轮换

**风险**: 可能被识别为爬虫

**安全操作流程**:
```python
# 使用真实的User-Agent池
USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
    # 更多真实UA
]

# 与请求头一致
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml...',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}
```

### 代理IP池

**风险**: 低质量代理可能泄露数据

**安全操作流程**:
```python
# 1. 使用可信代理服务
# 2. 检查代理是否匿名
# 3. 定期更新代理池

# 验证代理
python check_proxy.py --proxy "http://proxy:8080"
```

---

## 📋 请求频率建议

| 网站类型 | 建议频率 | 说明 |
|---------|---------|------|
| 大型电商 | 1-2秒/请求 | 有反爬机制 |
| 新闻网站 | 2-3秒/请求 | 较宽松 |
| 社交媒体 | 5-10秒/请求 | 严格反爬 |
| 政府网站 | 3-5秒/请求 | 避免影响服务 |

---

## 🐛 常见陷阱

### 陷阱1: 忽略robots.txt

**症状**: 被网站封禁

**原因**: 未遵守robots.txt规则

**解决方案**:
```python
# 在settings.py中启用
ROBOTSTXT_OBEY = True

# 或手动检查
python check_robots.py --url "https://example.com"
```

### 陷阱2: Cookie过期

**症状**: 登录状态丢失，无法访问需要登录的页面

**原因**: Cookie未持久化或已过期

**解决方案**:
```python
# 启用Cookie持久化
COOKIES_ENABLED = True
COOKIES_DEBUG = True

# 定期刷新Cookie
python refresh_cookies.py
```

### 陷阱3: 请求指纹一致

**症状**: 被识别为同一爬虫

**原因**: TLS指纹、浏览器指纹一致

**解决方案**:
```python
# 使用curl_cffi模拟真实浏览器TLS指纹
from curl_cffi import requests

# 或使用中间件随机化指纹
DOWNLOADER_MIDDLEWARES = {
    'scrapy_anticrawl.RandomizeFingerprintMiddleware': 400,
}
```

---

## 📞 紧急处理

如果被封禁：

1. **停止爬虫**: 立即停止所有请求
2. **更换IP**: 使用新的代理IP
3. **降低频率**: 大幅降低请求频率
4. **检查原因**: 分析被封原因，调整策略

---

**版本**: 1.0.0
**更新时间**: 2026-03-18