---
license: UNKNOWN
name: scrapy-anti-ban
description: Scrapy反爬策略模块，User-Agent轮换、代理IP池、请求频率控制
github_repo: scrapy/scrapy
github_hash: fc4c57e7958dbbc9532a38f3c622dd990c18591e
last_updated: 2026-04-25
source_type: derived
triggers: ["scrapy anti ban", "Scrapy Anti-Ban"]
---

# Scrapy Anti-Ban

## 元数据
- **名称**: scrapy-anti-ban
- **版本**: 1.0.0
- **来源**: [scrapy/scrapy](https://github.com/scrapy/scrapy) - 60.8k ⭐
- **创建日期**: 2026-03-16
- **匹配岗位**: 01调研师、05安全师

## 功能描述
Scrapy 反爬虫策略与中间件，提供 User-Agent 轮换、代理 IP 池、请求频率控制、Cookies 管理、验证码处理等企业级反爬能力。

## 核心能力

| 能力 | 说明 | 使用场景 |
|------|------|---------|
| **User-Agent 轮换** | 随机切换浏览器标识 | 模拟真实用户 |
| **代理 IP 池** | 动态代理切换 | 突破 IP 封锁 |
| **请求频率控制** | 智能延迟、随机间隔 | 避免触发限制 |
| **Cookies 管理** | Session 维护、自动处理 | 登录态保持 |
| **验证码处理** | 自动识别、人工介入 | 突破验证码 |
| **请求指纹** | 请求特征伪装 | 绕过指纹检测 |

## 反爬策略架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Scrapy 反爬策略架构                        │
├─────────────────────────────────────────────────────────────┤
│  请求层                                                      │
│  ├── User-Agent 轮换                                        │
│  ├── 代理 IP 池                                             │
│  ├── Referer 伪造                                           │
│  └── Headers 随机化                                         │
├─────────────────────────────────────────────────────────────┤
│  行为层                                                      │
│  ├── 请求频率控制                                            │
│  ├── 随机延迟                                                │
│  ├── 访问路径模拟                                            │
│  └── Session 管理                                           │
├─────────────────────────────────────────────────────────────┤
│  验证层                                                      │
│  ├── 验证码识别                                              │
│  ├── 登录态维护                                              │
│  └── 异常处理                                                │
└─────────────────────────────────────────────────────────────┘
```

## Middleware 实现

### 1. User-Agent 轮换中间件
```python
import random
from scrapy import signals

class RandomUserAgentMiddleware:
    """随机 User-Agent 中间件"""

    # 常用 User-Agent 列表
    USER_AGENTS = [
        # Chrome Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        # Chrome Mac
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        # Firefox Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        # Firefox Mac
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
        # Safari Mac
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
        # Edge
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    ]

    def __init__(self, user_agents=None):
        self.user_agents = user_agents or self.USER_AGENTS

    @classmethod
    def from_crawler(cls, crawler):
        user_agents = crawler.settings.getlist('USER_AGENTS')
        return cls(user_agents)

    def process_request(self, request, spider):
        request.headers['User-Agent'] = random.choice(self.user_agents)
```

### 2. 代理 IP 池中间件
```python
import random
import time
from typing import Optional
from scrapy.exceptions import NotConfigured

class ProxyMiddleware:
    """代理 IP 池中间件"""

    def __init__(self, proxy_list: list[str], proxy_enabled: bool = True):
        self.proxy_list = proxy_list
        self.proxy_enabled = proxy_enabled
        self.current_index = 0
        self.failed_proxies = set()
        self.proxy_stats = {}  # 代理成功率统计

    @classmethod
    def from_crawler(cls, crawler):
        proxy_list = crawler.settings.getlist('PROXY_LIST', [])
        proxy_enabled = crawler.settings.getbool('PROXY_ENABLED', True)

        if proxy_enabled and not proxy_list:
            raise NotConfigured("PROXY_LIST is empty but PROXY_ENABLED is True")

        return cls(proxy_list, proxy_enabled)

    def process_request(self, request, spider):
        if not self.proxy_enabled or not self.proxy_list:
            return

        proxy = self._get_next_proxy()
        if proxy:
            request.meta['proxy'] = proxy
            request.meta['proxy_start_time'] = time.time()

    def process_response(self, request, response, spider):
        self._update_proxy_stats(request, response.status)
        return response

    def process_exception(self, request, exception, spider):
        proxy = request.meta.get('proxy')
        if proxy:
            self.failed_proxies.add(proxy)
            spider.logger.warning(f"Proxy failed: {proxy}, error: {exception}")
        return

    def _get_next_proxy(self) -> Optional[str]:
        """获取下一个可用代理"""
        available = [p for p in self.proxy_list if p not in self.failed_proxies]
        if not available:
            # 重置失败代理
            self.failed_proxies.clear()
            available = self.proxy_list

        proxy = available[self.current_index % len(available)]
        self.current_index += 1
        return proxy

    def _update_proxy_stats(self, request, status_code: int):
        """更新代理统计"""
        proxy = request.meta.get('proxy')
        if not proxy:
            return

        if proxy not in self.proxy_stats:
            self.proxy_stats[proxy] = {'success': 0, 'failed': 0}

        if 200 <= status_code < 300:
            self.proxy_stats[proxy]['success'] += 1
        else:
            self.proxy_stats[proxy]['failed'] += 1
```

### 3. 请求频率控制中间件
```python
import random
import time
from collections import defaultdict

class RateLimitMiddleware:
    """智能请求频率控制中间件"""

    def __init__(self, delay: float, random_delay: float, max_per_second: int):
        self.base_delay = delay
        self.random_delay = random_delay
        self.max_per_second = max_per_second
        self.domain_last_request = defaultdict(float)
        self.domain_requests = defaultdict(list)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            delay=crawler.settings.getfloat('RATELIMIT_DELAY', 1.0),
            random_delay=crawler.settings.getfloat('RATELIMIT_RANDOM_DELAY', 0.5),
            max_per_second=crawler.settings.getint('RATELIMIT_MAX_PER_SECOND', 2)
        )

    def process_request(self, request, spider):
        domain = self._get_domain(request.url)
        now = time.time()

        # 计算需要等待的时间
        last_request = self.domain_last_request.get(domain, 0)
        elapsed = now - last_request

        # 基础延迟 + 随机延迟
        required_delay = self.base_delay + random.uniform(0, self.random_delay)

        if elapsed < required_delay:
            time.sleep(required_delay - elapsed)

        # 检查每秒请求数限制
        self._enforce_rate_limit(domain, now)

        self.domain_last_request[domain] = time.time()

    def _enforce_rate_limit(self, domain: str, now: float):
        """强制执行每秒请求数限制"""
        requests = self.domain_requests[domain]

        # 清理超过1秒的请求记录
        requests[:] = [t for t in requests if now - t < 1.0]

        if len(requests) >= self.max_per_second:
            sleep_time = 1.0 - (now - requests[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
            requests.clear()

        requests.append(now)

    def _get_domain(self, url: str) -> str:
        from urllib.parse import urlparse
        return urlparse(url).netloc
```

### 4. Referer 伪造中间件
```python
import random
from urllib.parse import urlparse

class RefererMiddleware:
    """Referer 伪造中间件"""

    def __init__(self, referer_policy: str = 'random'):
        self.referer_policy = referer_policy

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            referer_policy=crawler.settings.get('REFERER_POLICY', 'random')
        )

    def process_request(self, request, spider):
        if 'Referer' in request.headers:
            return

        referer = self._generate_referer(request.url)
        if referer:
            request.headers['Referer'] = referer

    def _generate_referer(self, target_url: str) -> str:
        """生成 Referer"""
        parsed = urlparse(target_url)
        domain = parsed.netloc

        if self.referer_policy == 'google':
            return f'https://www.google.com/search?q={domain}'
        elif self.referer_policy == 'bing':
            return f'https://www.bing.com/search?q={domain}'
        elif self.referer_policy == 'direct':
            return f'{parsed.scheme}://{domain}/'
        else:  # random
            sources = [
                f'https://www.google.com/',
                f'https://www.bing.com/',
                f'https://www.baidu.com/',
                f'{parsed.scheme}://{domain}/',
            ]
            return random.choice(sources)
```

### 5. Cookies 管理中间件
```python
import json
import os
from http.cookiejar import Cookie
from scrapy.http import Request

class CookiesMiddleware:
    """Cookies 管理中间件"""

    def __init__(self, cookies_file: str, cookies_enabled: bool = True):
        self.cookies_file = cookies_file
        self.cookies_enabled = cookies_enabled
        self.cookies = {}

        if cookies_enabled and cookies_file and os.path.exists(cookies_file):
            self._load_cookies()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            cookies_file=crawler.settings.get('COOKIES_FILE', ''),
            cookies_enabled=crawler.settings.getbool('COOKIES_ENABLED', True)
        )

    def process_request(self, request, spider):
        if not self.cookies_enabled:
            return

        domain_cookies = self._get_cookies_for_domain(request.url)
        if domain_cookies:
            request.cookies.update(domain_cookies)

    def process_response(self, request, response, spider):
        if not self.cookies_enabled:
            return response

        # 保存响应中的 Cookies
        if response.headers.get('Set-Cookie'):
            self._save_cookies_from_response(request.url, response)

        return response

    def _load_cookies(self):
        """从文件加载 Cookies"""
        with open(self.cookies_file) as f:
            self.cookies = json.load(f)

    def _save_cookies(self):
        """保存 Cookies 到文件"""
        with open(self.cookies_file, 'w') as f:
            json.dump(self.cookies, f, indent=2)

    def _get_cookies_for_domain(self, url: str) -> dict:
        """获取指定域名的 Cookies"""
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        return self.cookies.get(domain, {})

    def _save_cookies_from_response(self, url: str, response):
        """从响应中保存 Cookies"""
        from urllib.parse import urlparse
        domain = urlparse(url).netloc

        if domain not in self.cookies:
            self.cookies[domain] = {}

        # 解析 Set-Cookie 头
        for cookie_str in response.headers.getlist('Set-Cookie'):
            cookie_parts = cookie_str.decode().split(';')[0].split('=')
            if len(cookie_parts) == 2:
                name, value = cookie_parts
                self.cookies[domain][name.strip()] = value.strip()

        self._save_cookies()
```

### 6. 验证码处理中间件
```python
import base64
from io import BytesIO
from typing import Optional

class CaptchaMiddleware:
    """验证码处理中间件"""

    def __init__(self, captcha_service: str, api_key: str, auto_solve: bool = True):
        self.captcha_service = captcha_service
        self.api_key = api_key
        self.auto_solve = auto_solve

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            captcha_service=crawler.settings.get('CAPTCHA_SERVICE', '2captcha'),
            api_key=crawler.settings.get('CAPTCHA_API_KEY', ''),
            auto_solve=crawler.settings.getbool('CAPTCHA_AUTO_SOLVE', True)
        )

    def process_response(self, request, response, spider):
        # 检测验证码页面
        if self._is_captcha_page(response):
            spider.logger.info(f"Captcha detected on {request.url}")

            if self.auto_solve:
                solved = self._solve_captcha(request, response, spider)
                if solved:
                    # 重新请求
                    return request.replace(dont_filter=True)
            else:
                # 标记需要人工处理
                request.meta['captcha_required'] = True

        return response

    def _is_captcha_page(self, response) -> bool:
        """检测是否为验证码页面"""
        captcha_indicators = [
            'captcha',
            'recaptcha',
            'hcaptcha',
            '验证码',
            '请输入验证码',
        ]

        text = response.text.lower()
        return any(indicator in text for indicator in captcha_indicators)

    def _solve_captcha(self, request, response, spider) -> Optional[str]:
        """解决验证码"""
        # 图片验证码
        captcha_img = response.css('img.captcha::attr(src)').get()
        if captcha_img:
            return self._solve_image_captcha(captcha_img, spider)

        # reCAPTCHA
        site_key = response.css('[data-sitekey]::attr(data-sitekey)').get()
        if site_key:
            return self._solve_recaptcha(site_key, request.url, spider)

        return None

    def _solve_image_captcha(self, img_url: str, spider) -> Optional[str]:
        """解决图片验证码"""
        if self.captcha_service == '2captcha':
            return self._solve_with_2captcha(img_url, spider)
        elif self.captcha_service == 'anticaptcha':
            return self._solve_with_anticaptcha(img_url, spider)
        return None

    def _solve_with_2captcha(self, img_url: str, spider) -> Optional[str]:
        """使用 2captcha 服务"""
        import requests

        try:
            # 提交验证码
            submit_url = f'http://2captcha.com/in.php?key={self.api_key}&method=userrecaptcha&googlekey={img_url}'
            resp = requests.get(submit_url)
            if resp.text.startswith('OK'):
                captcha_id = resp.text.split('|')[1]

                # 等待结果
                import time
                for _ in range(30):
                    time.sleep(5)
                    result_url = f'http://2captcha.com/res.php?key={self.api_key}&action=get&id={captcha_id}'
                    result = requests.get(result_url)
                    if result.text.startswith('OK'):
                        return result.text.split('|')[1]

        except Exception as e:
            spider.logger.error(f"2captcha error: {e}")

        return None

    def _solve_recaptcha(self, site_key: str, page_url: str, spider) -> Optional[str]:
        """解决 reCAPTCHA"""
        # 类似实现...
        return None
```

### 7. 请求指纹伪装中间件
```python
import random
import hashlib

class FingerprintMiddleware:
    """请求指纹伪装中间件"""

    def __init__(self):
        self.session_ids = {}

    def process_request(self, request, spider):
        # 添加随机 Headers
        self._add_random_headers(request)

        # 维护 Session
        self._maintain_session(request)

    def _add_random_headers(self, request):
        """添加随机 Headers"""
        headers = {
            'Accept': self._get_random_accept(),
            'Accept-Language': self._get_random_accept_language(),
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': random.choice(['none', 'same-origin', 'cross-site']),
            'Sec-Fetch-User': '?1',
        }

        for key, value in headers.items():
            if key not in request.headers:
                request.headers[key] = value

    def _get_random_accept(self) -> str:
        """随机 Accept 头"""
        accepts = [
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        ]
        return random.choice(accepts)

    def _get_random_accept_language(self) -> str:
        """随机 Accept-Language 头"""
        languages = [
            'zh-CN,zh;q=0.9,en;q=0.8',
            'en-US,en;q=0.9',
            'zh-TW,zh;q=0.9,en;q=0.8',
            'ja,en-US;q=0.9,en;q=0.8',
        ]
        return random.choice(languages)

    def _maintain_session(self, request):
        """维护 Session"""
        from urllib.parse import urlparse
        domain = urlparse(request.url).netloc

        if domain not in self.session_ids:
            self.session_ids[domain] = hashlib.md5(
                f"{domain}{random.random()}".encode()
            ).hexdigest()[:16]
```

## settings.py 配置

```python
# 反爬虫配置

# User-Agent
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    # ... 更多 User-Agent
]

# 代理配置
PROXY_ENABLED = True
PROXY_LIST = [
    'http://proxy1.example.com:8080',
    'http://proxy2.example.com:8080',
    # ... 更多代理
]

# 频率控制
RATELIMIT_DELAY = 1.0
RATELIMIT_RANDOM_DELAY = 0.5
RATELIMIT_MAX_PER_SECOND = 2

# Cookies
COOKIES_ENABLED = True
COOKIES_FILE = 'cookies.json'

# 验证码
CAPTCHA_SERVICE = '2captcha'  # 或 'anticaptcha'
CAPTCHA_API_KEY = 'your_api_key'
CAPTCHA_AUTO_SOLVE = True

# Referer
REFERER_POLICY = 'random'  # 'google', 'bing', 'direct', 'random'

# 中间件配置
DOWNLOADER_MIDDLEWARES = {
    'myproject.middlewares.RandomUserAgentMiddleware': 400,
    'myproject.middlewares.ProxyMiddleware': 410,
    'myproject.middlewares.RateLimitMiddleware': 420,
    'myproject.middlewares.RefererMiddleware': 430,
    'myproject.middlewares.CookiesMiddleware': 440,
    'myproject.middlewares.FingerprintMiddleware': 450,
    'myproject.middlewares.CaptchaMiddleware': 460,
}
```

## 与天龙引擎协同

```bash
# 自然语言触发
[@调研师] 配置 Scrapy 反爬虫策略，突破某网站限制
[@安全师] 分析目标网站的反爬机制并制定策略

# Skill 调用
/scrapy-anti-ban enable --feature user-agent
/scrapy-anti-ban enable --feature proxy --list proxies.txt
/scrapy-anti-ban config --delay 2 --random 0.5
```

## 与 Chrome CDP 协同

| 场景 | 推荐方案 |
|------|---------|
| **静态页面** | Scrapy + Anti-Ban |
| **动态渲染** | Chrome CDP |
| **高反爬** | Chrome CDP + Anti-Ban |
| **大规模采集** | Scrapy + Anti-Ban + 代理池 |

## 参考资料
- [Downloader Middleware 文档](https://docs.scrapy.org/en/latest/topics/downloader-middleware.html)
- [2captcha API](https://2captcha.com/api-docs)
- [反爬虫策略大全](https://github.com/scrapy/scrapy)

## 更新日志
- **v1.0.0** (2026-03-16): 初始版本，7种反爬中间件