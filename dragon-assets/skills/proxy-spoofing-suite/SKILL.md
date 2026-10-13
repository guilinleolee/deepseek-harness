---
license: UNKNOWN
triggers: ["proxy spoofing suite", "Proxy Spoofing Suite"]
---
# Proxy Spoofing Suite
天龙引擎 V11.17 | 来源: CloakHQ/CloakBrowser

## L0: 一句话描述 (≤15字)
代理欺骗套件：代理池轮换+健康检查+GeoIP伪装

## L1: 使用场景 (50-100字)
当需要为 CloakBrowser L3/L4 隐身路由提供高质量代理池时，通过 proxy_pool_manager.py 实现代理轮换、健康检查、GeoIP匹配国家伪装、HTTP/SOCKS5 支持，以及请求头注入验证。

## L2: 详细文档

### 核心能力

| 能力 | 脚本 | 功能 |
|------|------|------|
| **代理池管理** | `proxy_pool_manager.py` | 代理添加/删除/轮换/健康检查 |
| **GeoIP伪装** | `proxy_pool_manager.py` | 代理IP→国家/时区/语言自动匹配 |
| **请求头注入** | `proxy_pool_manager.py` | Accept-Language/X-Forwarded-For/Via 头注入 |
| **健康检查** | `proxy_pool_manager.py` | 代理可用性/响应速度/匿名度检测 |
| **代理评分** | `proxy_pool_manager.py` | 速度+匿名度+稳定性三维评分 |

### 双模式架构

```
┌─────────────────────────────────────────────────────────────┐
│                     代理欺骗架构                              │
├─────────────────────────────────────────────────────────────┤
│  模式1: 代理池模式 (Proxy Pool)                          │
│  ├── 用途: L3隐身路由                                     │
│  ├── 特性: 轮换+健康检查+评分                            │
│  └── 集成: stealth_router.py L3配置                       │
│                                                             │
│  模式2: 地理伪装模式 (GeoIP Spoofing)                    │
│  ├── 用途: L4隐身路由                                     │
│  ├── 特性: 国家+时区+语言+WebRTC IP完全匹配             │
│  ├── 参数: geoip_from_proxy / auto_timezone / auto_locale │
│  └── 集成: cloakbrowser_launch.py L4配置                  │
└─────────────────────────────────────────────────────────────┘
```

### 代理评分体系

| 维度 | 权重 | 检测内容 |
|------|------|---------|
| **速度** | 40% | 响应时间 <3s 加分，>10s 扣分 |
| **匿名度** | 35% | 是否泄漏 WebRTC/DNS/X-Forwarded-For |
| **稳定性** | 25% | 连续3次请求成功率 |

### 代理评分阈值

| 分数范围 | 评价 | 行动建议 |
|----------|------|---------|
| **≥8.0** | 优质代理 | L4首选 |
| **≥6.0** | 良好代理 | L3可用 |
| **≥4.0** | 一般代理 | 仅备用 |
| **<4.0** | 低质代理 | 自动剔除 |

### L3/L4 代理配置

```
┌─────────────────────────────────────────────────────────────┐
│ L3: Proxy Pool 模式                                      │
│  proxy: 轮换池中选取得分最高代理                         │
│  health_check: 每次请求前验证代理可用性                 │
│  适用: 常规隐身采集                                     │
├─────────────────────────────────────────────────────────────┤
│ L4: GeoIP Spoofing 模式                                 │
│  geoip_from_proxy: True                                 │
│  auto_timezone: True    ← 自动匹配代理IP所在时区        │
│  auto_locale: True     ← 自动匹配代理IP所在语言         │
│  --fingerprint-webrtc-ip=auto  ← WebRTC IP = 代理IP     │
│  适用: 极高检测站点 (LinkedIn/Amazon/Facebook)          │
└─────────────────────────────────────────────────────────────┘
```

### 命令行使用

```bash
# 添加代理到池
python3 scripts/proxy_pool_manager.py add \
  --proxy "socks5://username:password@proxy.example.com:1080" \
  --country US --tags "residential,fast"

# 批量添加代理
python3 scripts/proxy_pool_manager.py batch-add proxies.txt

# 获取最优代理（L3路由）
python3 scripts/proxy_pool_manager.py get --level L3

# 获取GeoIP伪装代理（L4路由）
python3 scripts/proxy_pool_manager.py get --level L4 \
  --country "US" --require-tags "residential"

# 健康检查
python3 scripts/proxy_pool_manager.py health --all

# 健康检查（仅高风险代理）
python3 scripts/proxy_pool_manager.py health --level L3

# 代理评分
python3 scripts/proxy_pool_manager.py score --proxy "socks5://..."

# GeoIP查询
python3 scripts/proxy_pool_manager.py geoip --proxy "socks5://..."

# 头注入验证
python3 scripts/proxy_pool_manager.py headers --proxy "socks5://..." \
  --test-url "https://httpbin.org/headers"

# 列出所有代理
python3 scripts/proxy_pool_manager.py list

# 列出优质代理
python3 scripts/proxy_pool_manager.py list --min-score 8.0

# 删除代理
python3 scripts/proxy_pool_manager.py remove --proxy "socks5://..."

# 导出配置供 stealth_router 使用
python3 scripts/proxy_pool_manager.py export-config --level L4 --country US
```

### 输出格式示例

#### 代理列表 JSON 输出

```json
{
  "proxies": [
    {
      "proxy": "socks5://user:pass@us.proxy.com:1080",
      "country": "US",
      "score": 8.5,
      "speed_ms": 1200,
      "anonymity": "elite",
      "stability": 0.95,
      "tags": ["residential", "fast"],
      "last_check": "2026-05-19T10:30:00Z",
      "status": "active"
    }
  ],
  "total": 1,
  "by_country": {"US": 1}
}
```

#### GeoIP 配置输出

```json
{
  "proxy": "socks5://user:pass@us.proxy.com:1080",
  "geoip": {
    "country": "US",
    "timezone": "America/New_York",
    "locale": "en-US",
    "webrtc_ip": "203.0.113.50"
  },
  "cloakbrowser_config": {
    "proxy": "socks5://user:pass@us.proxy.com:1080",
    "geoip_from_proxy": true,
    "auto_timezone": true,
    "auto_locale": true,
    "arguments": ["--fingerprint-webrtc-ip=203.0.113.50"]
  }
}
```

### 代理池存储

| 环境 | 默认路径 |
|------|---------|
| **本地** | `~/.cloakbrowser/proxies.json` |
| **Windows** | `C:\Users\{user}\.cloakbrowser\proxies.json` |

### 代理配置文件格式 (proxies.json)

```json
{
  "version": "1.0",
  "updated": "2026-05-19T10:30:00Z",
  "proxies": [
    {
      "proxy": "socks5://user:pass@host:port",
      "country": "US",
      "tags": ["residential", "fast"],
      "added": "2026-05-10T08:00:00Z",
      "last_used": "2026-05-19T10:00:00Z",
      "use_count": 42,
      "score": 8.5,
      "health": {
        "last_check": "2026-05-19T10:30:00Z",
        "speed_ms": 1200,
        "anonymity": "elite",
        "stability": 0.95,
        "dns_leak": false,
        "webRTC_leak": false
      },
      "status": "active"
    }
  ]
}
```

### 使用场景

- **L3隐身路由**: 普通代理池轮换，绕过基础反爬
- **L4地理伪装**: 代理IP完全匹配国家/时区/语言，绕过高级检测
- **代理健康监控**: 定期检查代理可用性，自动剔除失效代理
- **批量任务**: 代理轮换分配，避免单IP请求过快触发风控

### 天龙岗位协同

| 岗位 | 协同方式 |
|------|---------|
| **17-04桌面自动化** | 代理池 → L3/L4路由配置输入 |
| **01调研师** | 代理切换 → 不同站点数据采集 |
| **35-02社媒运营** | 代理隔离 → LinkedIn/Twitter多账号运营 |
| **38-02销售管理** | 代理管理 → CRM多账号数据采集 |
| **stealth-browser-orchestrator** | 代理 → L4路由配置输入 |

### 安装验证

```bash
# 验证脚本
python3 scripts/proxy_pool_manager.py --help

# 依赖检查（标准库无需额外安装）
python3 -c "import dataclasses, json, subprocess, urllib.request; print('stdlib OK')"

# 验证代理格式
python3 -c "from proxy_pool_manager import ProxyEntry; p = ProxyEntry.from_url('socks5://u:p@h:port'); print(f'Parse OK: {p.country}')"

# 健康检查测试
python3 scripts/proxy_pool_manager.py health --all --verbose
```

### 文件结构

```
proxy-spoofing-suite/
├── SKILL.md                          # 本文件
└── scripts/
    └── proxy_pool_manager.py          # 代理池管理脚本
```

### 依赖

- Python 3.8+
- 标准库：dataclasses, json, pathlib, subprocess, urllib.request, socket, time, re
- 外部依赖（可选）：`requests`（用于健康检查加速）

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-19 | 初始集成，基于 CloakBrowser L3/L4 代理配置 |
