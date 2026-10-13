---
license: UNKNOWN
triggers: ["fincept market data", "Fincept Market Data Skill"]
---
# Fincept Market Data Skill

## L0: 一句话描述 (≤15字)
金融市场数据一站式连接器

## L1: 使用场景 (50-100字)

**适用场景**:
- 量化交易策略回测需要历史K线数据
- 投资组合监控需要实时行情
- 财务分析需要财务报表和盈利数据
- 加密货币交易需要多交易所实时数据

**触发条件**:
- 需要获取股票/ETF/期货实时或历史行情
- 需要批量获取多只股票财务数据
- 需要获取期权链数据进行波动率分析
- 需要加密货币多交易所比价

**不适用**:
- 实时交易执行（仅数据获取，不含交易接口）
- 替代Bloomberg/Refinitiv等专业终端
- 需要彭博估值等深度数据

## L2: 详细文档

### 目录结构

```
fincept-market-data/
├── SKILL.md                    # 本文件
├── fincept_market_data/        # Python模块
│   ├── __init__.py
│   ├── client.py              # MarketDataClient 主客户端
│   ├── exceptions.py           # 异常类
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base_provider.py   # Provider基类
│   │   ├── yfinance_provider.py
│   │   ├── polygon_provider.py
│   │   └── crypto_provider.py
│   └── cli.py                 # CLI入口 (fincept-market)
├── README.md
└── requirements.txt
```

### 安装依赖

```bash
pip install yfinance pandas sqlalchemy
# 可选: polygon-client (需要API Key)
```

### API参考

#### MarketDataClient

主客户端，封装所有数据源。

```python
from fincept_market_data import MarketDataClient

client = MarketDataClient(
    cache_enabled=True,      # 启用SQLite缓存
    cache_dir="~/.fincept_cache",
    timeout=30,              # 请求超时(秒)
    max_retries=3           # 最大重试次数
)
```

##### 实时行情

```python
# 单只股票
quote = client.quote("AAPL")
# {
#   "symbol": "AAPL",
#   "price": 178.52,
#   "change": 2.34,
#   "change_pct": 1.33,
#   "volume": 52341234,
#   "timestamp": "2024-01-15T16:00:00Z"
# }

# 批量股票
quotes = client.quotes(["AAPL", "MSFT", "GOOGL"])
```

##### 历史K线

```python
# 日线
daily = client.historical(
    "AAPL",
    start="2024-01-01",
    end="2024-12-31",
    interval="1d"
)

# 60分钟K线
hourly = client.historical(
    "AAPL",
    start="2024-01-01",
    end="2024-01-07",
    interval="60m"
)
```

##### 加密货币

```python
# 实时价格
btc = client.crypto("BTC-USD")
# {
#   "symbol": "BTC-USD",
#   "price": 43250.00,
#   "bid": 43248.50,
#   "ask": 43251.00,
#   "volume_24h": 15234567890,
#   "exchange": "Kraken"
# }

# 历史数据
btc_hist = client.crypto_historical(
    "BTC-USD",
    start="2024-01-01",
    end="2024-01-07",
    interval="1h"
)
```

##### 财务报表

```python
# 利润表、资产负债表、现金流量表
financials = client.financials("AAPL")
# {
#   "income_statement": [...],
#   "balance_sheet": [...],
#   "cash_flow": [...]
# }

# 盈利数据
earnings = client.earnings("AAPL")
# [{"date": "2024-01-15", "eps": 2.18, "revenue": 119.58}]
```

##### 期权链

```python
# 期权链
options = client.option_chain("AAPL")
# {
#   "calls": [{"strike": 175, "bid": 5.20, "ask": 5.30, ...}],
#   "puts": [{"strike": 180, "bid": 3.10, "ask": 3.20, ...}],
#   "expiration": "2024-01-19"
# }

# 到期日列表
expirations = client.option_expirations("AAPL")
```

##### 批量获取

```python
# 批量股票历史数据（并行）
data = client.batch_historical(
    ["AAPL", "MSFT", "GOOGL"],
    start="2024-01-01",
    end="2024-12-31",
    interval="1d",
    parallel=True  # 并行获取
)
```

### CLI命令

```bash
# 实时行情
fincept-market quote AAPL
fincept-market quotes AAPL,MSFT,GOOGL

# 历史数据
fincept-market hist AAPL --start 2024-01-01 --end 2024-12-31 --interval 1d

# 加密货币
fincept-market crypto BTC-USD
fincept-market crypto-hist BTC-USD --interval 1h

# 财务报表
fincept-market financials AAPL

# 期权链
fincept-market options AAPL

# 批量数据
fincept-market batch AAPL,MSFT --start 2024-01-01 --end 2024-12-31
```

### 数据源支持矩阵

| 数据源 | 实时行情 | 历史K线 | 财务报表 | 期权链 | 加密货币 |
|--------|---------|---------|---------|--------|---------|
| Yahoo Finance | ✅ | ✅ | ✅ | ✅ | ✅ |
| Polygon.io | ✅ | ✅ | ✅ | ✅ | ❌ |
| Kraken | ❌ | ✅ | ❌ | ❌ | ✅ |
| Binance | ❌ | ✅ | ❌ | ❌ | ✅ |
| Coinbase | ❌ | ✅ | ❌ | ❌ | ✅ |
| Alpha Vantage | ✅ | ✅ | ❌ | ❌ | ❌ |

### 错误处理

```python
from fincept_market_data.exceptions import (
    RateLimitError,
    DataNotFoundError,
    ProviderError
)

try:
    data = client.quote("INVALID_SYMBOL")
except DataNotFoundError:
    print("Symbol not found")
except RateLimitError:
    print("Rate limited, wait and retry")
except ProviderError as e:
    print(f"Provider error: {e}")
```

### 缓存机制

```python
# 缓存默认启用
client = MarketDataClient(cache_enabled=True)

# 手动控制缓存
client.cache.get("AAPL", "quote")     # 获取缓存
client.cache.set("AAPL", "quote", data, ttl=300)  # 设置缓存，TTL=300秒
client.cache.clear()                  # 清除所有缓存
client.cache.stats()                  # 查看缓存统计
```

### Provider优先级配置

```python
client = MarketDataClient(
    provider_priority=["polygon", "yfinance"],  # 优先使用Polygon
    api_keys={
        "polygon": "YOUR_POLYGON_API_KEY",
        "alpha_vantage": "YOUR_ALPHA_VANTAGE_API_KEY"
    }
)
```

### 数据字段说明

#### Quote字段
| 字段 | 类型 | 说明 |
|------|------|------|
| symbol | str | 股票代码 |
| price | float | 当前价格 |
| change | float | 价格变化 |
| change_pct | float | 变化百分比 |
| volume | int | 成交量 |
| timestamp | str | 时间戳 |

#### Historical字段
| 字段 | 类型 | 说明 |
|------|------|------|
| datetime | str | K线时间 |
| open | float | 开盘价 |
| high | float | 最高价 |
| low | float | 最低价 |
| close | float | 收盘价 |
| volume | int | 成交量 |

### 天龙引擎集成

```bash
# 投资研究员使用
[@62-02] 使用fincept-market获取苹果和微软的历史数据进行对比分析

# 量化研究员使用
[@64-01] 获取BTC历史数据，进行波动率分析

# 财务分析师使用
[@17-01] 获取AAPL最新财报数据
```

## 技术规格

- **Python版本**: 3.11+
- **依赖**: yfinance, pandas, sqlalchemy, requests
- **缓存**: SQLite (默认路径: ~/.fincept_cache)
- **超时**: 30秒（可配置）
- **重试**: 指数退避，最多重试3次
- **并发**: 批量请求支持并行（可选）
